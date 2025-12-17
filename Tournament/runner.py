# -*- coding: utf-8 -*-
"""
@file runner.py
@brief Tournament Runner

@details
Orchestrates running a complete tournament between AI generals.
Follows Single Responsibility Principle - only handles tournament execution.
"""

from typing import List

from Controller.simulation_controller import SimulationController
from Model.generals import General
from Model.strategies import (
    StrategieBrainDead,
    StrategieDAFT,
    StrategieCrossbowmanSomeIQ,
    StrategieKnightSomeIQ,
    StrategiePikemanSomeIQ,
    StrategieStartSomeIQ,
    StrategieSimpleAttackBestAvoidWorst,
)
from Model.units import UnitType
from Utils.predefined_scenarios import PredefinedScenarios

from Tournament.config import TournamentConfig
from Tournament.results import MatchResult, TournamentResults


class TournamentRunner:
    """
    Orchestrates running a complete tournament between AI generals.
    
    Handles:
    - All pairwise matchups including reflexive (X vs X)
    - Position alternation for fairness
    - Multiple rounds per matchup
    - Result collection
    """
    
    # Available generals
    AVAILABLE_GENERALS = ['BRAINDEAD', 'DAFT', 'SOMEIQ', 'RPC']
    
    # Available scenarios
    SCENARIO_MAP = {
        'classical_medieval_battle': PredefinedScenarios.classic_medieval_battle,
        'defensive_siege': PredefinedScenarios.defensive_siege,
        'cavalry_charge': PredefinedScenarios.cavalry_charge,
        'cannae_envelopment': PredefinedScenarios.cannae_envelopment,
        'british_square': PredefinedScenarios.british_square,
    }
    
    def __init__(self, config: TournamentConfig):
        """
        Initialize tournament runner.
        
        @param config: Tournament configuration
        """
        self.config = config
        self.results = TournamentResults(config=config)
        self.simulation_controller = SimulationController()
    
    def run(self) -> TournamentResults:
        """
        Run the complete tournament.
        
        For each scenario and each pair of generals (including X vs X),
        runs the specified number of rounds, alternating positions if configured.
        
        @return: Complete tournament results
        """
        total_matchups = (
            len(self.config.generals) ** 2 * 
            len(self.config.scenarios) * 
            self.config.rounds_per_matchup
        )
        
        print(f"\n{'='*60}")
        print(f"TOURNAMENT START")
        print(f"{'='*60}")
        print(f"Generals: {self.config.generals}")
        print(f"Scenarios: {self.config.scenarios}")
        print(f"Rounds per matchup: {self.config.rounds_per_matchup}")
        print(f"Alternate positions: {self.config.alternate_positions}")
        print(f"Total matches: {total_matchups}")
        print(f"{'='*60}\n")
        
        match_count = 0
        
        for scenario_name in self.config.scenarios:
            print(f"\n--- Scenario: {scenario_name} ---")
            
            if scenario_name not in self.SCENARIO_MAP:
                print(f"  WARNING: Unknown scenario '{scenario_name}', skipping")
                continue
            
            for general_a_name in self.config.generals:
                for general_b_name in self.config.generals:
                    print(f"  {general_a_name} vs {general_b_name}: ", end='', flush=True)
                    
                    wins_a = 0
                    wins_b = 0
                    draws = 0
                    
                    for round_num in range(self.config.rounds_per_matchup):
                        # Alternate positions every other round if configured
                        if self.config.alternate_positions and round_num % 2 == 1:
                            result = self._run_match(
                                general_b_name, general_a_name, 
                                scenario_name, swap_result=True
                            )
                        else:
                            result = self._run_match(
                                general_a_name, general_b_name, 
                                scenario_name
                            )
                        
                        self.results.add_match(result)
                        match_count += 1
                        
                        if result.is_draw:
                            draws += 1
                            print('D', end='', flush=True)
                        elif result.winner == 'A':
                            wins_a += 1
                            print('A', end='', flush=True)
                        else:
                            wins_b += 1
                            print('B', end='', flush=True)
                    
                    print(f" | {general_a_name}: {wins_a}, {general_b_name}: {wins_b}, Draws: {draws}")
        
        print(f"\n{'='*60}")
        print(f"TOURNAMENT COMPLETE - {match_count} matches played")
        print(f"{'='*60}\n")
        
        return self.results
    
    def _run_match(self, general_a_name: str, general_b_name: str, 
                   scenario_name: str, swap_result: bool = False) -> MatchResult:
        """
        Run a single match.
        
        @param general_a_name: Name of general for Team A
        @param general_b_name: Name of general for Team B
        @param scenario_name: Name of scenario to use
        @param swap_result: If True, swap the general names in result (for position alternation)
        @return: Match result
        """
        # Create fresh scenario
        scenario = self.SCENARIO_MAP[scenario_name]()
        
        # Create generals
        general_a = self._create_general(general_a_name, scenario.units_a, scenario.units_b)
        general_b = self._create_general(general_b_name, scenario.units_b, scenario.units_a)
        
        scenario.general_a = general_a
        scenario.general_b = general_b
        
        # Store initial counts
        initial_a = len(scenario.units_a)
        initial_b = len(scenario.units_b)
        
        # Run simulation using SimulationController
        self.simulation_controller.initialize_simulation(
            scenario,
            tick_speed=5,
            paused=False,
            unlocked=True
        )
        
        # Run synchronously (not in thread) for tournament
        output = self.simulation_controller.simulation.simulate()
        
        # Collect results
        ticks = output.get('ticks', 0)
        survivors_a = sum(1 for u in scenario.units_a if u.hp > 0)
        survivors_b = sum(1 for u in scenario.units_b if u.hp > 0)
        casualties_a = initial_a - survivors_a
        casualties_b = initial_b - survivors_b
        
        # Determine winner
        is_draw = False
        if survivors_a > 0 and survivors_b == 0:
            winner = 'A'
        elif survivors_b > 0 and survivors_a == 0:
            winner = 'B'
        else:
            # Draw (timeout or both teams have survivors/both eliminated)
            winner = None
            is_draw = True
        
        # Handle position swap for alternation
        if swap_result:
            # Swap back the names to reflect original matchup
            result_general_a = general_b_name
            result_general_b = general_a_name
            # Also swap winner perspective
            if winner == 'A':
                winner = 'B'
            elif winner == 'B':
                winner = 'A'
            # Swap stats
            survivors_a, survivors_b = survivors_b, survivors_a
            casualties_a, casualties_b = casualties_b, casualties_a
        else:
            result_general_a = general_a_name
            result_general_b = general_b_name
        
        return MatchResult(
            general_a=result_general_a,
            general_b=result_general_b,
            scenario_name=scenario_name,
            winner=winner,
            ticks=ticks,
            team_a_survivors=survivors_a,
            team_b_survivors=survivors_b,
            team_a_casualties=casualties_a,
            team_b_casualties=casualties_b,
            is_draw=is_draw
        )
    
    def _create_general(self, name: str, units_a, units_b) -> General:
        """Create a general with the specified AI strategy."""
        name_up = name.upper()
        
        if name_up == 'BRAINDEAD':
            strategy_map = {
                UnitType.CROSSBOWMAN: StrategieBrainDead(None),
                UnitType.KNIGHT: StrategieBrainDead(None),
                UnitType.PIKEMAN: StrategieBrainDead(None),
            }
            return General(unitsA=units_a, unitsB=units_b, sS=None, sT=strategy_map)
        
        elif name_up == 'DAFT':
            strategy_map = {
                UnitType.CROSSBOWMAN: StrategieDAFT(None),
                UnitType.KNIGHT: StrategieDAFT(None),
                UnitType.PIKEMAN: StrategieDAFT(None),
            }
            return General(unitsA=units_a, unitsB=units_b, sS=None, sT=strategy_map)
        
        elif name_up == 'SOMEIQ':
            strategy_map = {
                UnitType.CROSSBOWMAN: StrategieCrossbowmanSomeIQ(),
                UnitType.KNIGHT: StrategieKnightSomeIQ(),
                UnitType.PIKEMAN: StrategiePikemanSomeIQ(),
            }
            start_strategy = StrategieStartSomeIQ()
            return General(unitsA=units_a, unitsB=units_b, sS=start_strategy, sT=strategy_map)
        
        elif name_up == 'RPC':
            # Rock-Paper-Counter: each unit type targets its counter
            strategy_map = {
                UnitType.CROSSBOWMAN: StrategieSimpleAttackBestAvoidWorst(favoriteTroup=UnitType.PIKEMAN, hatedTroup=UnitType.KNIGHT),
                UnitType.KNIGHT: StrategieSimpleAttackBestAvoidWorst(favoriteTroup=UnitType.CROSSBOWMAN, hatedTroup=UnitType.PIKEMAN),
                UnitType.PIKEMAN: StrategieSimpleAttackBestAvoidWorst(favoriteTroup=UnitType.KNIGHT, hatedTroup=UnitType.CROSSBOWMAN),
            }
            return General(unitsA=units_a, unitsB=units_b, sS=None, sT=strategy_map)
        
        else:
            raise ValueError(f"Unknown general: {name}. Available: {self.AVAILABLE_GENERALS}")
