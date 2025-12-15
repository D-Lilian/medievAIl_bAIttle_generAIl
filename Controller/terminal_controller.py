# -*- coding: utf-8 -*-
"""
@file terminal_controller.py
@brief Terminal Controller - Manages the terminal view for simulation display

@details
Controls the terminal view display. Communicates with the simulation
ONLY through SimulationController. Receives SimulationController and
Scenario from eval.py.

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
    - ViewState: Centralized state management
    - InputHandler: Keyboard input processing
    - MapRenderer/UIRenderer/DebugRenderer: Separate rendering components
    - UnitCacheManager: Unit data extraction and caching
    """

    def __init__(self, sim_controller: SimulationController, scenario: Scenario, view: Optional[TerminalView] = None):
        """
        @brief Initialize the controller.

        @param sim_controller SimulationController instance (from eval.py)
        @param scenario Scenario instance (from eval.py)
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

        # Connect save callback
        self.view.on_quick_save = self.save_load.save_game

        self.running = False

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
            self.view.input_handler.on_quick_save = self.save_load.save_game
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
                    # Use set_tick_speed for efficient direct sync
                    self.sim_controller.set_tick_speed(self.view.tick_speed)

                # 4. Sync pause state
                #    ViewState.paused <-> Simulation.paused (via SimulationController)
                if self.view.paused != self.sim_controller.simulation.paused:
                    self.sim_controller.toggle_pause()
        finally:
            self.view.cleanup()


def run_terminal_view(sim_controller: SimulationController, scenario: Scenario) -> None:
    """
    @brief Helper function to launch the terminal view.

    @details
    Entry point for external callers (e.g., eval.py).
    Creates a TerminalController with the SimulationController and Scenario, then runs the interactive terminal view.
    Tick speed is retrieved from sim_controller.get_tick_speed().

    @param sim_controller SimulationController instance (from eval.py)
    @param scenario Scenario instance (from eval.py)

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
