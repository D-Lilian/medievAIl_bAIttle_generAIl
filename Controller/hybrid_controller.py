# -*- coding: utf-8 -*-
"""
@file hybrid_controller.py
@brief Hybrid Controller - Allows switching between Terminal and Pygame views during runtime

@details
This controller manages both Terminal (curses) and Pygame (2.5D) views,
allowing the user to switch between them with F9 during the battle.

The controller maintains a single SimulationController instance and switches
between view controllers dynamically.

@controls
F9: Switch between Terminal and Pygame views
"""
from enum import Enum
from typing import Optional

from Controller.simulation_controller import SimulationController
from Model.scenario import Scenario


class ViewMode(Enum):
    """Available view modes."""
    TERMINAL = "terminal"
    PYGAME = "pygame"


class HybridController:
    """
    @brief Controller that allows switching between Terminal and Pygame views.
    
    @details
    Maintains a single SimulationController and switches between view modes.
    State (pause, tick speed) is preserved across switches.
    
    Usage:
        controller = HybridController(sim_controller, scenario, initial_mode=ViewMode.PYGAME)
        controller.run()
    """
    
    def __init__(self, sim_controller: SimulationController, scenario: Scenario,
                 initial_mode: ViewMode = ViewMode.PYGAME):
        """
        @brief Initialize hybrid controller.
        
        @param sim_controller SimulationController instance
        @param scenario Scenario instance
        @param initial_mode Initial view mode (TERMINAL or PYGAME)
        """
        self.sim_controller = sim_controller
        self.scenario = scenario
        self.current_mode = initial_mode
        self.running = False
        
    def run(self):
        """
        @brief Main loop - runs the current view and handles mode switches.
        
        Switch is one-way only: Terminal -> Pygame (F9).
        Once in Pygame view, ESC quits the application.
        """
        self.running = True
        
        while self.running:
            if self.current_mode == ViewMode.TERMINAL:
                result = self._run_terminal_view()
                if result == "SWITCH":
                    self._switch_view()
                else:
                    self.running = False
            else:
                result = self._run_pygame_view()
                if result == "SWITCH":
                    self._switch_view()
                else:
                    self.running = False

        return None
                
    def _switch_view(self):
        """Switch between Terminal and Pygame views."""
        if self.current_mode == ViewMode.PYGAME:
            self.current_mode = ViewMode.TERMINAL
        else:
            self.current_mode = ViewMode.PYGAME
        
    def _run_terminal_view(self) -> str:
        """
        @brief Run the terminal view until quit or switch.
        @return "SWITCH", "QUIT", or False
        """
        # Lazy import to avoid circular dependencies
        from View.terminal_view import TerminalView
        
        # Create terminal view
        terminal_view = TerminalView(
            self.scenario.size_x, 
            self.scenario.size_y,
            tick_speed=self.sim_controller.get_tick_speed()
        )
        
        try:
            terminal_view.init_curses()
            
            # Add F9 switch handler
            original_process = terminal_view.input_handler.process
            switch_requested = [False]  # Use list to allow modification in closure
            
            def process_with_switch():
                import curses
                try:
                    key = terminal_view.input_handler.stdscr.getch()
                except (KeyboardInterrupt, curses.error):
                    return True
                    
                if key == -1:
                    return True
                    
                # F9 = Switch view
                if key == curses.KEY_F9:
                    switch_requested[0] = True
                    return False  # Exit the loop
                    
                # Put the key back for normal processing
                curses.ungetch(key)
                return original_process()
            
            terminal_view.input_handler.process = process_with_switch

            if terminal_view.paused != self.sim_controller.simulation.paused:
                terminal_view.paused = not terminal_view.paused
            
            running = True
            while running:
                # Update view
                running = terminal_view.update(self.sim_controller.simulation)
                
                # Check simulation end
                sim = self.sim_controller.simulation
                team1_alive = [u for u in sim.scenario.units_a if u.hp > 0]
                team2_alive = [u for u in sim.scenario.units_b if u.hp > 0]
                
                if not team1_alive or not team2_alive:
                    running = False
                    if not sim.paused:
                        self.sim_controller.toggle_pause()
                
                # Sync speed
                if terminal_view.tick_speed != self.sim_controller.get_tick_speed():
                    while self.sim_controller.get_tick_speed() < terminal_view.tick_speed:
                        self.sim_controller.increase_tick()
                    while self.sim_controller.get_tick_speed() > terminal_view.tick_speed:
                        self.sim_controller.decrease_tick()
                
                # Sync pause
                if terminal_view.paused != self.sim_controller.simulation.paused:
                    self.sim_controller.toggle_pause()
                    
        finally:
            terminal_view.cleanup()
            
        if switch_requested[0]:
            return "SWITCH"
        return "QUIT"
    
    def _run_pygame_view(self) -> str:
        """
        @brief Run the pygame view until quit or switch.
        @return "SWITCH", "QUIT", or False
        """
        # Lazy imports to avoid import errors when pygame not available
        from View.pygame_view import PygameView
        
        # Initialize pygame
        pygame_view = PygameView(self.scenario, self.sim_controller)
        pygame_view.paused = self.sim_controller.simulation.paused

        result = pygame_view.run()
        print(result)

        # Cleanup pygame
        pygame_view.cleanup()

        if result == "SWITCH":
            return "SWITCH"
        return "QUIT"
