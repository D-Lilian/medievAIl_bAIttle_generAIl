# -*- coding: utf-8 -*-
"""
@file terminal_controller.py
@brief Terminal Controller - Manages the terminal view for simulation display

@details
Controls the terminal view display. Communicates with the simulation
ONLY through SimulationController. Receives SimulationController and
Scenario from main.py.

Implements the "Game Loop" pattern for the terminal interface.

@note Compatible with SOLID/KISS refactored terminal_view.py
"""
from typing import Optional

from Controller.simulation_controller import SimulationController
from View.terminal_view import TerminalView
from Model.scenario import Scenario
from Utils.save_load import SaveLoad


class TerminalController:
    """
    @brief Controller for the Terminal View.

    @details
    Orchestrates the interaction between SimulationController and TerminalView.
    Does NOT interact directly with Simulation - uses SimulationController as intermediary.
    
    Uses the refactored TerminalView which follows SOLID principles:
    - ViewState (`View/state.py`): Centralized state management
    - InputHandler (`View/input_handler.py`): Keyboard input processing
    - Renderers (`View/renderers/`): Separate rendering components (Map, UI, Debug)
    - UnitCacheManager (`View/unit_cache.py`): Unit data extraction and caching
    """

    def __init__(self, sim_controller: SimulationController, scenario: Scenario, view: Optional[TerminalView] = None):
        """
        @brief Initialize the controller.

        @param sim_controller SimulationController instance (from main.py)
        @param scenario Scenario instance (from main.py)
        @param view Optional TerminalView instance. If None, a new one is created.
        """
        self.sim_controller = sim_controller
        self.scenario = scenario
        self.save_load = SaveLoad(scenario)

        # Dependency Injection: Allow passing an existing view, or create a default one
        if view:
            self.view = view
        else:
            self.view = TerminalView(scenario.size_x, scenario.size_y, tick_speed=sim_controller.get_tick_speed())

        # Set general names for report generation
        if hasattr(scenario.general_a, 'name'):
            self.view.report_generator.general_a_name = scenario.general_a.name
        if hasattr(scenario.general_b, 'name'):
            self.view.report_generator.general_b_name = scenario.general_b.name

        # Connect save callback
        self.view.on_quick_save = self._handle_save

        self.running = False

    def _handle_save(self):
        """Handle save request and notify view."""
        self.save_load.save_game()
        self.view.state.notification = "Game Saved!"
        self.view.state.notification_time = __import__('time').time()

    def run(self):
        """
        @brief Run the terminal view loop.

        @details
        Starts the curses application and enters the main display loop.
        View updates are synced with simulation state via SimulationController.
        
        The TerminalView.update() method handles:
        - Input processing (via InputHandler)
        - Unit cache update (via UnitCacheManager)
        - Rendering (via MapRenderer, UIRenderer, DebugRenderer)
        - Framerate control
        """
        try:
            self.view.init_curses()
            # Connect save callback to input handler
            self.view.input_handler.on_quick_save = self._handle_save
            self.running = True

            while self.running:
                # 1. Update View (Render current state & Handle Input)
                #    Returns False when user requests quit (ESC or Q)
                self.running = self.view.update(self.sim_controller.simulation)

                # 2. Check if simulation is finished (one team eliminated)
                sim = self.sim_controller.simulation
                team1_alive = [u for u in sim.scenario.units_a if u.hp > 0]
                team2_alive = [u for u in sim.scenario.units_b if u.hp > 0]
                
                if not team1_alive or not team2_alive:
                    self.running = False
                    # Pause simulation so we can see the final state
                    if not sim.paused:
                        self.sim_controller.toggle_pause()

                # 3. Sync speed from view to simulation controller
                #    ViewState.tick_speed <-> Simulation.tick_speed (via SimulationController)
                if self.view.tick_speed != self.sim_controller.get_tick_speed():
                    while self.sim_controller.get_tick_speed() < self.view.tick_speed:
                        self.sim_controller.increase_tick()
                    while self.sim_controller.get_tick_speed() > self.view.tick_speed:
                        self.sim_controller.decrease_tick()

                # 4. Sync pause state
                #    ViewState.paused <-> Simulation.paused (via SimulationController)
                if self.view.paused != self.sim_controller.simulation.paused:
                    self.sim_controller.toggle_pause()
        finally:
            # Switch to headless mode: unpause and unlock speed so it finishes
            if self.sim_controller and self.sim_controller.simulation:
                self.sim_controller.simulation.paused = False
                self.sim_controller.simulation.unlocked = True

            self.view.cleanup()


def run_terminal_view(sim_controller: SimulationController, scenario: Scenario) -> None:
    """
    @brief Helper function to launch the terminal view.

    @details
    Entry point for external callers (e.g., main.py).
    Creates a TerminalController with the SimulationController and Scenario, then runs the interactive terminal view.
    Tick speed is retrieved from sim_controller.get_tick_speed().

    @param sim_controller SimulationController instance (from main.py)
    @param scenario Scenario instance (from main.py)

    @code
    from Controller.terminal_controller import run_terminal_view
    from Controller.simulation_controller import SimulationController
    
    sim_controller = SimulationController()
    sim_controller.initialize_simulation(scenario, tick_speed=20, paused=True, unlocked=True)
    run_terminal_view(sim_controller, scenario)
    @endcode
    """
    controller = TerminalController(sim_controller, scenario)
    controller.run()


if __name__ == "__main__":
    print("Usage: Import run_terminal_view and pass SimulationController + Scenario")
    print("")
    print("  from Controller.terminal_controller import run_terminal_view")
    print("  from Controller.simulation_controller import SimulationController")
    print("  ")
    print("  sim_controller = SimulationController()")
    print("  sim_controller.initialize_simulation(scenario, tick_speed=20, paused=True, unlocked=True)")
    print("  run_terminal_view(sim_controller, scenario)")
    raise SystemExit(1)
