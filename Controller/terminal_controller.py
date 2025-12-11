# -*- coding: utf-8 -*-
"""
@file terminal_controller.py
@brief Terminal Controller - Manages the terminal view for simulation display

@details
Controls the terminal view display. Communicates with the simulation
ONLY through SimulationController. Can receive a Simulation from eval.py
but delegates all simulation operations to SimulationController.

Implements the "Game Loop" pattern for the terminal interface.

@note Compatible with SOLID/KISS refactored terminal_view.py
"""
from typing import Optional

from Controller.simulation_controller import SimulationController
from View.terminal_view import TerminalView
from Model.simulation import Simulation


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

    def __init__(self, simulation: Simulation, view: Optional[TerminalView] = None, tick_speed: int = 20):
        """
        @brief Initialize the controller.

        @param simulation Simulation instance (passed from eval.py)
        @param view Optional TerminalView instance. If None, a new one is created.
        @param tick_speed Initial simulation speed (ticks per second)
        """
        # Use SimulationController as intermediary
        self.sim_controller = SimulationController()
        self.sim_controller.simulation = Simulation(simulation, tick_speed=tick_speed, paused=True, unlocked=True)

        # Store scenario reference for view initialization
        scenario = self.sim_controller.simulation.scenario

        # Dependency Injection: Allow passing an existing view, or create a default one
        if view:
            self.view = view
        else:
            self.view = TerminalView(scenario.size_x, scenario.size_y, tick_speed=tick_speed)

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
            self.running = True

            while self.running:
                # 1. Update View (Render current state & Handle Input)
                #    Returns False when user requests quit (ESC)
                self.running = self.view.update(self.sim_controller.simulation)

                # 2. Sync speed from view to simulation controller
                #    ViewState.tick_speed <-> Simulation.tick_speed
                if self.view.tick_speed != self.sim_controller.simulation.tick_speed:
                    self.sim_controller.simulation.tick_speed = self.view.tick_speed

                # 3. Sync pause state
                #    ViewState.paused <-> Simulation.paused (via SimulationController)
                if self.view.paused != self.sim_controller.simulation.paused:
                    self.sim_controller.toggle_pause()

        finally:
            self.view.cleanup()


def run_terminal_view(simulation: Simulation, tick_speed: int = 20) -> None:
    """
    @brief Helper function to launch the terminal view with a simulation.

    @details
    Entry point for external callers (e.g., eval.py).
    Creates a TerminalController and runs the interactive terminal view.

    @param simulation Simulation instance (from eval.py)
    @param tick_speed Display speed (ticks per second), default 20

    @code
    from Controller.terminal_controller import run_terminal_view
    run_terminal_view(simulation, tick_speed=20)
    @endcode
    """
    controller = TerminalController(simulation, tick_speed=tick_speed)
    controller.run()


if __name__ == "__main__":
    print("Usage: Import run_terminal_view and pass a Simulation from eval.py")
    print("")
    print("  from Controller.terminal_controller import run_terminal_view")
    print("  run_terminal_view(simulation, tick_speed=20)")
    raise SystemExit(1)
