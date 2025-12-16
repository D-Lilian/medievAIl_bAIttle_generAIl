# -*- coding: utf-8 -*-
"""
@file data_collector.py
@brief Data Collector - Runs simulations and collects data for analysis

@details
Separates data collection from plotting. Runs scenarios with varying parameters,
collects results into a unified data structure that can be used by any plotter.

Supports the workflow:
    for type in [Knight,Crossbow]:
        for N in range(1,100):
            data[type,N] = Lanchester(type, N).run()  # repeat N times
    PlotLanchester(data)

"""

import os
from typing import List, Dict, Any, Callable, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from Controller.simulation_controller import SimulationController
from Model.simulation import Simulation
from Model.scenario import Scenario
from Model.generals import General
from Model.strategies import (
    StrategieBrainDead,
    StrategieDAFT,
    StrategieCrossbowmanSomeIQ,
    StrategieKnightSomeIQ,
    StrategiePikemanSomeIQ,
    StrategieStartSomeIQ,
)
from Model.units import UnitType

from Utils.battle_data import BattleResult, BattleDataCollector, AggregatedResults, PlotData
from Utils.lanchester_scenario import Lanchester


@dataclass
class CollectedData:
    """
    Container for all collected simulation data.
    
    Organized by (unit_type, N) -> AggregatedResults
    Can be passed to any Plotter for visualization.
    """
    unit_types: List[str] = field(default_factory=list)
    n_range: List[int] = field(default_factory=list)
    
    # data[type][n] -> AggregatedResults
    results: Dict[str, Dict[int, AggregatedResults]] = field(default_factory=dict)
    
    # For plotting convenience: PlotData per unit type
    plot_data: Dict[str, PlotData] = field(default_factory=dict)
    
    # Metadata
    ai_name: str = ""
    scenario_name: str = ""
    num_repetitions: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_casualties(self, unit_type: str, n: int, team: str = 'winner') -> float:
        """Get average casualties for a specific (type, N) combination."""
        if unit_type not in self.results or n not in self.results[unit_type]:
            return 0.0
        agg = self.results[unit_type][n]
        if team == 'winner':
            # Winner is usually team B (2N)
            return agg.avg_team_b_casualties
        elif team == 'A':
            return agg.avg_team_a_casualties
        elif team == 'B':
            return agg.avg_team_b_casualties
        return 0.0
    
    def get_survivors(self, unit_type: str, n: int, team: str = 'winner') -> float:
        """Get average survivors for a specific (type, N) combination."""
        if unit_type not in self.results or n not in self.results[unit_type]:
            return 0.0
        agg = self.results[unit_type][n]
        if team == 'winner' or team == 'B':
            return agg.avg_team_b_survivors
        return agg.avg_team_a_survivors
    
    def get_win_rate(self, unit_type: str, n: int, team: str = 'B') -> float:
        """Get win rate for a specific (type, N) combination."""
        if unit_type not in self.results or n not in self.results[unit_type]:
            return 0.0
        agg = self.results[unit_type][n]
        if team == 'B':
            return agg.team_b_win_rate
        return agg.team_a_win_rate


class DataCollector:
    """
    Collects simulation data by running scenarios with varying parameters.
    
    Workflow:
        collector = DataCollector(ai_name='DAFT', num_repetitions=10)
        data = collector.collect_lanchester(
            unit_types=['Knight', 'Crossbow'],
            n_range=range(1, 100)
        )
        # data can now be passed to any Plotter
    """
    
    AVAILABLE_AIS = ['BRAINDEAD', 'DAFT', 'SOMEIQ']
    
    def __init__(self, ai_name: str = 'DAFT', num_repetitions: int = 10):
        """
        Initialize the data collector.
        
        @param ai_name: Name of AI to use for both sides
        @param num_repetitions: Number of times to repeat each configuration
        """
        self.ai_name = ai_name.upper()
        self.num_repetitions = num_repetitions
        self.simulation_controller = SimulationController()
    
    def collect_lanchester(self, unit_types: List[str], 
                           n_range: range) -> CollectedData:
        """
        Collect Lanchester analysis data.
        
        Runs Lanchester(type, N) for each type in unit_types and N in n_range,
        repeating num_repetitions times for each configuration.
        
        Signature: Lanchester(type, N) creates N units vs 2N units
        
        @param unit_types: List of unit type names ['Knight', 'Crossbow']
        @param n_range: Range of N values to test
        @return: CollectedData with all simulation results
        """
        data = CollectedData(
            unit_types=list(unit_types),
            n_range=list(n_range),
            ai_name=self.ai_name,
            scenario_name='Lanchester',
            num_repetitions=self.num_repetitions
        )
        
        total_configs = len(unit_types) * len(n_range)
        current = 0
        
        print(f"\n{'='*60}")
        print(f"DATA COLLECTION: Lanchester Analysis")
        print(f"{'='*60}")
        print(f"AI: {self.ai_name}")
        print(f"Unit types: {unit_types}")
        print(f"N range: {list(n_range)[:5]}...{list(n_range)[-1]} ({len(n_range)} values)")
        print(f"Repetitions per config: {self.num_repetitions}")
        print(f"Total simulations: {total_configs * self.num_repetitions}")
        print(f"{'='*60}\n")
        
        for unit_type in unit_types:
            print(f"\n[{unit_type}] Starting collection...")
            
            data.results[unit_type] = {}
            data.plot_data[unit_type] = PlotData(unit_type=unit_type)
            
            for n in n_range:
                current += 1
                progress = (current / total_configs) * 100
                print(f"  [{progress:5.1f}%] {unit_type} N={n}: ", end='', flush=True)
                
                # Run simulations for this (type, N) configuration
                aggregated = self._run_batch(
                    unit_type=unit_type,
                    n=n
                )
                
                # Store results
                data.results[unit_type][n] = aggregated
                data.plot_data[unit_type].add_data_point(n, aggregated)
                
                # Print summary
                win_rate = aggregated.team_b_win_rate * 100
                b_cas = aggregated.avg_team_b_casualties
                print(f"{self.num_repetitions} runs | 2N win: {win_rate:.0f}% | 2N casualties: {b_cas:.1f}")
        
        print(f"\n{'='*60}")
        print(f"DATA COLLECTION COMPLETE")
        print(f"{'='*60}\n")
        
        return data
    
    def _run_batch(self, unit_type: str, n: int) -> AggregatedResults:
        """
        Run a batch of simulations for one (type, N) configuration.
        
        @param unit_type: Type of units
        @param n: Number of units for team A (team B gets 2*n)
        @return: Aggregated results from all runs
        """
        aggregated = AggregatedResults(
            scenario_name='Lanchester',
            scenario_params={'unit_type': unit_type, 'n': n},
            num_runs=0
        )
        
        for _ in range(self.num_repetitions):
            # Create fresh scenario: N vs 2N
            scenario = Lanchester(unit_type, n)
            
            # Assign generals (same AI for both sides)
            scenario.general_a = self._create_general(scenario.units_a, scenario.units_b)
            scenario.general_b = self._create_general(scenario.units_b, scenario.units_a)
            
            # Run simulation using SimulationController
            self.simulation_controller.initialize_simulation(
                scenario,
                tick_speed=5,
                paused=False,
                unlocked=True
            )
            output = self.simulation_controller.simulation.simulate()
            
            # Collect results
            result = BattleDataCollector.collect_from_scenario(scenario, output)
            result.scenario_name = 'Lanchester'
            result.scenario_params = {'unit_type': unit_type, 'n': n}
            
            aggregated.add_result(result)
        
        return aggregated
    
    def _create_general(self, units_a, units_b) -> General:
        """Create a general with the configured AI strategy."""
        if self.ai_name == 'BRAINDEAD':
            strategy_map = {
                UnitType.CROSSBOWMAN: StrategieBrainDead(None),
                UnitType.KNIGHT: StrategieBrainDead(None),
                UnitType.PIKEMAN: StrategieBrainDead(None),
            }
            return General(unitsA=units_a, unitsB=units_b, sS=None, sT=strategy_map)
        
        elif self.ai_name == 'SOMEIQ':
            strategy_map = {
                UnitType.CROSSBOWMAN: StrategieCrossbowmanSomeIQ(),
                UnitType.KNIGHT: StrategieKnightSomeIQ(),
                UnitType.PIKEMAN: StrategiePikemanSomeIQ(),
            }
            return General(unitsA=units_a, unitsB=units_b, 
                          sS=StrategieStartSomeIQ(), sT=strategy_map)
        
        else:  # Default to DAFT
            strategy_map = {
                UnitType.CROSSBOWMAN: StrategieDAFT(None),
                UnitType.KNIGHT: StrategieDAFT(None),
                UnitType.PIKEMAN: StrategieDAFT(None),
            }
            return General(unitsA=units_a, unitsB=units_b, sS=None, sT=strategy_map)


def parse_types_arg(types_str: str) -> List[str]:
    """
    Parse the types argument from CLI.
    
    Examples:
        '[Knight,Crossbow]' -> ['Knight', 'Crossbow']
        '[Knight]' -> ['Knight']
        'Knight,Crossbow' -> ['Knight', 'Crossbow']
    
    @param types_str: String representation of types list
    @return: List of unit type names
    """
    # Remove brackets if present
    types_str = types_str.strip('[]')
    
    # Split by comma
    types = [t.strip() for t in types_str.split(',')]
    
    # Normalize names
    name_map = {
        'knight': 'Knight',
        'crossbow': 'Crossbowman',
        'crossbowman': 'Crossbowman',
        'pikeman': 'Pikeman',
        'pike': 'Pikeman',
        'melee': 'Knight',
        'ranged': 'Crossbowman',
        'archer': 'Crossbowman',
    }
    
    normalized = []
    for t in types:
        lower = t.lower()
        normalized.append(name_map.get(lower, t))
    
    return normalized


def parse_range_arg(range_str: str) -> range:
    """
    Parse the range argument from CLI.
    
    Examples:
        'range(1,100)' -> range(1, 100)
        'range(1,100,5)' -> range(1, 100, 5)
        '1-100' -> range(1, 101)
        '1:100:5' -> range(1, 100, 5)
    
    @param range_str: String representation of range
    @return: Python range object
    """
    range_str = range_str.strip()
    
    # Handle range(min,max) or range(min,max,step)
    if range_str.startswith('range(') and range_str.endswith(')'):
        inner = range_str[6:-1]
        parts = [int(p.strip()) for p in inner.split(',')]
        if len(parts) == 2:
            return range(parts[0], parts[1])
        elif len(parts) == 3:
            return range(parts[0], parts[1], parts[2])
        elif len(parts) == 1:
            return range(1, parts[0])
    
    # Handle min-max format
    if '-' in range_str and not range_str.startswith('-'):
        parts = range_str.split('-')
        if len(parts) == 2:
            return range(int(parts[0]), int(parts[1]) + 1)
    
    # Handle min:max:step format
    if ':' in range_str:
        parts = range_str.split(':')
        if len(parts) == 2:
            return range(int(parts[0]), int(parts[1]))
        elif len(parts) == 3:
            return range(int(parts[0]), int(parts[1]), int(parts[2]))
    
    # Default fallback
    return range(5, 51, 5)
