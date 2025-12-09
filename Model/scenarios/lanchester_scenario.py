# -*- coding: utf-8 -*-
"""
@file lanchester_scenario.py
@brief Lanchester Scenario - Test Lanchester's Laws of Combat

@details
Implements the Lanchester(type, N) scenario where:
- type: Unit type to use (melee like Knight, or ranged like Crossbowman)
- N: Base number of units (Team A gets N, Team B gets 2*N)

This scenario is designed to test Lanchester's Laws:
- Linear Law: Casualties proportional to N (melee combat)
- Square Law: Casualties proportional to N² (ranged combat)

"""
import sys
import os
from typing import Type, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Model.scenarios.base_scenario import BaseScenario, BattleResult, MockGeneral
from Model.units import Unit, Team, Knight, Crossbowman, Pikeman, UnitType
from Model.orders import AttackNearestTroupOmniscient


class LanchesterScenario(BaseScenario):
    """
    @brief Scenario for testing Lanchester's Laws
    
    @details Creates a battle with:
    - Team A: N units of specified type
    - Team B: 2*N units of same type
    - Units placed within range of each other
    
    Used to verify combat mechanics follow Lanchester's predictions:
    - Melee units should follow Linear Law
    - Ranged units should follow Square Law
    """
    
    # Mapping from string names to unit classes
    UNIT_TYPES = {
        'Knight': Knight,
        'Crossbowman': Crossbowman,
        'Pikeman': Pikeman,
        'melee': Knight,      # Alias for melee type
        'ranged': Crossbowman, # Alias for ranged type
        'archer': Crossbowman, # Alias
    }
    
    def __init__(self, size_x: int = 120, size_y: int = 120):
        super().__init__(size_x, size_y)
        self._unit_type_name: str = ""
        self._n: int = 0
        self._unit_class: Type[Unit] = None
    
    @property
    def name(self) -> str:
        return f"Lanchester({self._unit_type_name}, {self._n})"
    
    def setup(self, unit_type: str = "Knight", n: int = 10, spacing: float = 2.0, 
              distance: float = 10.0) -> 'LanchesterScenario':
        """
        @brief Set up the Lanchester scenario
        
        @param unit_type Type of unit ("Knight", "Crossbowman", "melee", "ranged")
        @param n Base number of units (Team A gets N, Team B gets 2*N)
        @param spacing Spacing between units in a line
        @param distance Initial distance between the two armies
        @return self for method chaining
        """
        self.reset()
        
        # Validate and store parameters
        self._unit_type_name = unit_type
        self._n = n
        
        if unit_type not in self.UNIT_TYPES:
            raise ValueError(f"Unknown unit type: {unit_type}. Valid types: {list(self.UNIT_TYPES.keys())}")
        
        self._unit_class = self.UNIT_TYPES[unit_type]
        
        # Calculate positions
        # Team A on the left, Team B on the right
        center_y = self.size_y // 2
        
        # Team A: N units
        team_a_x = self.size_x // 3
        start_y_a = center_y - (n * spacing) // 2
        
        for i in range(n):
            unit = self._unit_class(Team.A, team_a_x, start_y_a + i * spacing)
            # Initialize damage tracking
            unit.damage_dealt = 0
            unit.distance_moved = 0
            self.units.append(unit)
            self.units_a.append(unit)
            # Give order to attack nearest enemy (UnitType.ALL = any type)
            unit.order_manager.AddMaxPriority(AttackNearestTroupOmniscient(unit, UnitType.ALL))
        
        # Team B: 2*N units (positioned close enough to be in range for ranged)
        team_b_x = team_a_x + distance
        start_y_b = center_y - (2 * n * spacing) // 2
        
        for i in range(2 * n):
            unit = self._unit_class(Team.B, team_b_x, start_y_b + i * spacing)
            unit.damage_dealt = 0
            unit.distance_moved = 0
            self.units.append(unit)
            self.units_b.append(unit)
            unit.order_manager.AddMaxPriority(AttackNearestTroupOmniscient(unit, UnitType.ALL))
        
        # Use mock generals (no AI interference)
        self.general_a = MockGeneral()
        self.general_b = MockGeneral()
        
        return self
    
    def _get_parameters(self):
        """Return scenario parameters for result tracking"""
        return {
            'unit_type': self._unit_type_name,
            'n': self._n,
            'team_a_count': self._n,
            'team_b_count': 2 * self._n,
        }


class LanchesterExperiment:
    """
    @brief Run multiple Lanchester scenarios and collect data
    
    @details Runs the Lanchester scenario for multiple unit types
    and N values, collecting results for analysis.
    """
    
    def __init__(self):
        self.results: List[BattleResult] = []
    
    def run(self, unit_types: List[str], n_range: range, 
            repetitions: int = 1, tick_speed: int = 100) -> List[BattleResult]:
        """
        @brief Run experiments for all combinations of unit types and N values
        
        @param unit_types List of unit type names to test
        @param n_range Range of N values to test
        @param repetitions Number of times to repeat each configuration
        @param tick_speed Simulation speed
        @return List of BattleResult objects
        """
        self.results = []
        total = len(unit_types) * len(n_range) * repetitions
        current = 0
        
        for unit_type in unit_types:
            for n in n_range:
                for rep in range(repetitions):
                    current += 1
                    print(f"Running {current}/{total}: {unit_type} N={n} rep={rep+1}")
                    
                    scenario = LanchesterScenario()
                    scenario.setup(unit_type=unit_type, n=n)
                    result = scenario.run(tick_speed=tick_speed, unlocked=True)
                    result.parameters['repetition'] = rep + 1
                    self.results.append(result)
        
        return self.results
    
    def to_dataframe(self):
        """
        @brief Convert results to a pandas DataFrame
        
        @return pandas DataFrame with all results
        """
        import pandas as pd
        
        data = []
        for r in self.results:
            row = {
                'unit_type': r.parameters.get('unit_type', ''),
                'n': r.parameters.get('n', 0),
                'repetition': r.parameters.get('repetition', 1),
                'team_a_initial': r.team_a_initial,
                'team_a_remaining': r.team_a_remaining,
                'team_a_casualties': r.team_a_casualties,
                'team_a_casualty_rate': r.team_a_casualty_rate,
                'team_b_initial': r.team_b_initial,
                'team_b_remaining': r.team_b_remaining,
                'team_b_casualties': r.team_b_casualties,
                'team_b_casualty_rate': r.team_b_casualty_rate,
                'winner': r.winner,
                'ticks': r.ticks,
            }
            data.append(row)
        
        return pd.DataFrame(data)


if __name__ == "__main__":
    # Quick test
    print("Testing Lanchester Scenario...")
    scenario = LanchesterScenario()
    scenario.setup(unit_type="Knight", n=5)
    result = scenario.run()
    print(f"Result: {result.winner} wins!")
    print(f"Team A: {result.team_a_remaining}/{result.team_a_initial} remaining")
    print(f"Team B: {result.team_b_remaining}/{result.team_b_initial} remaining")
