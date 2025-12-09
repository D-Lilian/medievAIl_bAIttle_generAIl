# -*- coding: utf-8 -*-
"""
@file terminal_controller.py
@brief Terminal Controller - Manages the simulation execution

@details
Controls the flow of the simulation when running in terminal mode.
Handles user input passed from the view and updates the model accordingly.
Implements the "Game Loop" pattern.

"""
import random
import sys
import os
from typing import Optional

# Add parent directory to path for Model imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model.simulation import Simulation, DEFAULT_NUMBER_OF_TICKS_PER_SECOND
from View.terminal_view import TerminalView
from Model.scenario import Scenario
from Model.units import Knight, Pikeman, Team

class TerminalController:
    """
    @brief Controller for the Terminal View

    @details
    Orchestrates the interaction between the Simulation (Model) and the TerminalView (View).
    It runs the main loop, handles timing, and updates the model state.
    """

    def __init__(self, scenario: Scenario, view: Optional[TerminalView] = None, tick_speed: int = 5):
        """
        @brief Initialize the controller

        @param scenario The battle scenario to simulate
        @param view Optional TerminalView instance. If None, a new one is created.
        @param tick_speed Initial simulation speed (ticks per second)
        """
        self.scenario = scenario
        self.simulation = Simulation(scenario, tick_speed=tick_speed, paused=True, unlocked=True)
        
        # Dependency Injection: Allow passing an existing view, or create a default one
        if view:
            self.view = view
        else:
            self.view = TerminalView(scenario.size_x, scenario.size_y, tick_speed=tick_speed)
            
        self.running = False

    def run(self):
        """
        @brief Run the simulation loop
        
        @details
        Starts the curses application and enters the main game loop.
        Synchronizes the view and the model.
        """
        try:
            self.view.init_curses()
            self.running = True
            
            # Initialize generals (AI)
            self._initialize_generals()

            while self.running:
                # 1. Update Model (if not paused)
                if not self.view.paused and not self.simulation.finished():
                    self._step()
                
                # 2. Update View (Render & Handle Input)
                self.running = self.view.update(self.simulation)
                
                # 3. Sync Control State (Speed)
                if self.view.tick_speed != self.simulation.tick_speed:
                    self.simulation.tick_speed = self.view.tick_speed

        finally:
            self.view.cleanup()

    def _initialize_generals(self):
        """Initialize the AI generals for both teams."""
        if self.scenario.general_a:
            self.scenario.general_a.BeginStrategy()
            self.scenario.general_a.CreateOrders()
        if self.scenario.general_b:
            self.scenario.general_b.BeginStrategy()
            self.scenario.general_b.CreateOrders()

    def _step(self):
        """
        @brief Execute one simulation step (tick)
        
        @details
        Advances the simulation state by one tick.
        
        NOTE: This logic duplicates some of `Simulation.simulate()` because
        the Model does not expose a granular `step()` method, and we cannot
        modify the Model. This allows us to have interactive control over the loop.
        """
        
        # 1. Randomize unit order for fairness
        random.shuffle(self.scenario.units)

        # 2. Process Unit Orders
        for unit in self.scenario.units:
            if not self.simulation.is_unit_still_alive(unit):
                continue

            for unit_order in unit.order_manager:
                if unit_order.Try(self.simulation):
                    unit_order.Remove(unit_order)
            
            # Reset flags (used for rendering/logic)
            self.simulation.as_unit_attacked = False
            self.simulation.as_unit_moved = False
        
        self.simulation.tick += 1

        # 3. Handle Reload Times
        for unit in list(self.simulation.reload_units):
            unit.update_reload(1 / DEFAULT_NUMBER_OF_TICKS_PER_SECOND)
            if unit.can_attack():
                try:
                    self.simulation.reload_units.remove(unit)
                except ValueError:
                    pass
        
        # 4. General (AI) Logic - Every second (approx)
        if self.simulation.tick % DEFAULT_NUMBER_OF_TICKS_PER_SECOND == 0:
            self._update_generals()

    def _update_generals(self):
        """Update the Generals' knowledge and orders."""
        types = self.simulation.type_present_in_team()
        
        if self.scenario.general_a:
            for types_present in types.get("A", []):
                if types_present not in self.simulation.types_present.get("A", []):
                    self.scenario.general_a.notify(types_present)
            self.scenario.general_a.CreateOrders()
            
        if self.scenario.general_b:
            for types_present in types.get("B", []):
                if types_present not in self.simulation.types_present.get("B", []):
                    self.scenario.general_b.HandleUnitTypeDepleted(types_present)
            self.scenario.general_b.CreateOrders()
        
        self.simulation.types_present = types

if __name__ == "__main__":
    # Demo scenario if run directly
    units = []
    units_a = []
    units_b = []
    
    # Team A (Cyan) - Left side
    for i in range(5):
        u = Knight(Team.A, 20, 20 + i*5)
        units.append(u)
        units_a.append(u)
    
    for i in range(5):
        u = Pikeman(Team.A, 25, 20 + i*5)
        units.append(u)
        units_a.append(u)
        
    # Team B (Red) - Right side
    for i in range(5):
        u = Knight(Team.B, 100, 20 + i*5)
        units.append(u)
        units_b.append(u)
        
    for i in range(5):
        u = Pikeman(Team.B, 95, 20 + i*5)
        units.append(u)
        units_b.append(u)
    
    # Mock generals for demo
    class MockGeneral:
        def BeginStrategy(self): pass
        def CreateOrders(self): pass
        def notify(self, t): pass
        def HandleUnitTypeDepleted(self, t): pass

    scenario = Scenario(units, units_a, units_b, MockGeneral(), MockGeneral(), size_x=120, size_y=120)
    
    controller = TerminalController(scenario, tick_speed=20)
    controller.run()
