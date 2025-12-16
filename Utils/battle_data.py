# -*- coding: utf-8 -*-
"""
@file battle_data.py
@brief Battle Data Collection - Structures for storing simulation results

@details
Provides dataclasses and utilities for collecting, storing, and aggregating
battle statistics from simulations. Follows SOLID principles with single
responsibility for data representation.

"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
from datetime import datetime


@dataclass
class TeamStats:
    """Statistics for a single team in a battle."""
    initial_units: int = 0
    surviving_units: int = 0
    casualties: int = 0
    total_initial_hp: int = 0
    total_remaining_hp: int = 0
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    unit_type_breakdown: Dict[str, int] = field(default_factory=dict)
    
    @property
    def casualty_rate(self) -> float:
        """Percentage of units lost."""
        if self.initial_units == 0:
            return 0.0
        return self.casualties / self.initial_units
    
    @property 
    def hp_loss_rate(self) -> float:
        """Percentage of total HP lost."""
        if self.total_initial_hp == 0:
            return 0.0
        return (self.total_initial_hp - self.total_remaining_hp) / self.total_initial_hp


@dataclass 
class BattleResult:
    """Complete result from a single battle simulation."""
    ticks: int = 0
    winner: Optional[str] = None  # 'A', 'B', or 'draw'
    team_a: TeamStats = field(default_factory=TeamStats)
    team_b: TeamStats = field(default_factory=TeamStats)
    duration_seconds: float = 0.0
    scenario_name: str = ""
    scenario_params: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'ticks': self.ticks,
            'winner': self.winner,
            'team_a': {
                'initial_units': self.team_a.initial_units,
                'surviving_units': self.team_a.surviving_units,
                'casualties': self.team_a.casualties,
                'total_initial_hp': self.team_a.total_initial_hp,
                'total_remaining_hp': self.team_a.total_remaining_hp,
                'total_damage_dealt': self.team_a.total_damage_dealt,
                'total_damage_taken': self.team_a.total_damage_taken,
                'casualty_rate': self.team_a.casualty_rate,
            },
            'team_b': {
                'initial_units': self.team_b.initial_units,
                'surviving_units': self.team_b.surviving_units,
                'casualties': self.team_b.casualties,
                'total_initial_hp': self.team_b.total_initial_hp,
                'total_remaining_hp': self.team_b.total_remaining_hp,
                'total_damage_dealt': self.team_b.total_damage_dealt,
                'total_damage_taken': self.team_b.total_damage_taken,
                'casualty_rate': self.team_b.casualty_rate,
            },
            'duration_seconds': self.duration_seconds,
            'scenario_name': self.scenario_name,
            'scenario_params': self.scenario_params,
            'timestamp': self.timestamp,
        }


@dataclass
class AggregatedResults:
    """Aggregated results from multiple runs of the same scenario configuration."""
    scenario_name: str
    scenario_params: Dict[str, Any]
    num_runs: int
    results: List[BattleResult] = field(default_factory=list)
    
    @property
    def avg_team_a_casualties(self) -> float:
        """Average casualties for Team A."""
        if not self.results:
            return 0.0
        return sum(r.team_a.casualties for r in self.results) / len(self.results)
    
    @property
    def avg_team_b_casualties(self) -> float:
        """Average casualties for Team B."""
        if not self.results:
            return 0.0
        return sum(r.team_b.casualties for r in self.results) / len(self.results)
    
    @property
    def avg_team_a_survivors(self) -> float:
        """Average surviving units for Team A."""
        if not self.results:
            return 0.0
        return sum(r.team_a.surviving_units for r in self.results) / len(self.results)
    
    @property
    def avg_team_b_survivors(self) -> float:
        """Average surviving units for Team B."""
        if not self.results:
            return 0.0
        return sum(r.team_b.surviving_units for r in self.results) / len(self.results)
    
    @property
    def avg_ticks(self) -> float:
        """Average simulation ticks."""
        if not self.results:
            return 0.0
        return sum(r.ticks for r in self.results) / len(self.results)
    
    @property
    def team_a_win_rate(self) -> float:
        """Win rate for Team A."""
        if not self.results:
            return 0.0
        wins = sum(1 for r in self.results if r.winner == 'A')
        return wins / len(self.results)
    
    @property
    def team_b_win_rate(self) -> float:
        """Win rate for Team B."""
        if not self.results:
            return 0.0
        wins = sum(1 for r in self.results if r.winner == 'B')
        return wins / len(self.results)
    
    @property
    def draw_rate(self) -> float:
        """Draw rate."""
        if not self.results:
            return 0.0
        draws = sum(1 for r in self.results if r.winner == 'draw')
        return draws / len(self.results)
    
    def add_result(self, result: BattleResult):
        """Add a battle result to the aggregation."""
        self.results.append(result)
        self.num_runs = len(self.results)


@dataclass
class PlotData:
    """Data structure for plotting Lanchester-style graphs."""
    unit_type: str
    n_values: List[int] = field(default_factory=list)
    avg_winner_casualties: List[float] = field(default_factory=list)
    avg_loser_casualties: List[float] = field(default_factory=list)
    avg_team_a_casualties: List[float] = field(default_factory=list)
    avg_team_b_casualties: List[float] = field(default_factory=list)
    avg_team_a_survivors: List[float] = field(default_factory=list)
    avg_team_b_survivors: List[float] = field(default_factory=list)
    team_a_win_rates: List[float] = field(default_factory=list)
    team_b_win_rates: List[float] = field(default_factory=list)
    avg_ticks: List[float] = field(default_factory=list)
    
    def add_data_point(self, n: int, aggregated: AggregatedResults):
        """Add a data point from aggregated results."""
        self.n_values.append(n)
        self.avg_team_a_casualties.append(aggregated.avg_team_a_casualties)
        self.avg_team_b_casualties.append(aggregated.avg_team_b_casualties)
        self.avg_team_a_survivors.append(aggregated.avg_team_a_survivors)
        self.avg_team_b_survivors.append(aggregated.avg_team_b_survivors)
        self.team_a_win_rates.append(aggregated.team_a_win_rate)
        self.team_b_win_rates.append(aggregated.team_b_win_rate)
        self.avg_ticks.append(aggregated.avg_ticks)
        
        # Winner casualties (Team B should win in Lanchester scenarios with 2:1 advantage)
        # But we record based on actual results
        winner_casualties = []
        loser_casualties = []
        for r in aggregated.results:
            if r.winner == 'B':
                winner_casualties.append(r.team_b.casualties)
                loser_casualties.append(r.team_a.casualties)
            elif r.winner == 'A':
                winner_casualties.append(r.team_a.casualties)
                loser_casualties.append(r.team_b.casualties)
        
        if winner_casualties:
            self.avg_winner_casualties.append(sum(winner_casualties) / len(winner_casualties))
        else:
            self.avg_winner_casualties.append(0.0)
            
        if loser_casualties:
            self.avg_loser_casualties.append(sum(loser_casualties) / len(loser_casualties))
        else:
            self.avg_loser_casualties.append(0.0)


class BattleDataCollector:
    """
    Collects battle statistics from simulation scenarios.
    
    Responsible for extracting data from Simulation results and
    creating structured BattleResult objects.
    """
    
    @staticmethod
    def collect_from_scenario(scenario, simulation_output: dict) -> BattleResult:
        """
        Collect battle statistics from a completed simulation.
        
        @param scenario: The Scenario that was simulated
        @param simulation_output: Output dict from Simulation.simulate()
        @return: BattleResult with all statistics
        """
        result = BattleResult()
        result.ticks = simulation_output.get('ticks', 0)
        
        # Team A stats
        team_a = TeamStats()
        team_a.initial_units = len(scenario.units_a)
        team_a.surviving_units = sum(1 for u in scenario.units_a if u.hp > 0)
        team_a.casualties = team_a.initial_units - team_a.surviving_units
        team_a.total_damage_dealt = sum(u.damage_dealt for u in scenario.units_a)
        
        # Team B stats  
        team_b = TeamStats()
        team_b.initial_units = len(scenario.units_b)
        team_b.surviving_units = sum(1 for u in scenario.units_b if u.hp > 0)
        team_b.casualties = team_b.initial_units - team_b.surviving_units
        team_b.total_damage_dealt = sum(u.damage_dealt for u in scenario.units_b)
        
        # Cross-reference damage taken
        team_a.total_damage_taken = team_b.total_damage_dealt
        team_b.total_damage_taken = team_a.total_damage_dealt
        
        result.team_a = team_a
        result.team_b = team_b
        
        # Determine winner
        if team_a.surviving_units > 0 and team_b.surviving_units == 0:
            result.winner = 'A'
        elif team_b.surviving_units > 0 and team_a.surviving_units == 0:
            result.winner = 'B'
        else:
            result.winner = 'draw'
        
        return result
    
    @staticmethod
    def save_results(results: List[BattleResult], filepath: str):
        """Save results to JSON file."""
        data = [r.to_dict() for r in results]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_results(filepath: str) -> List[BattleResult]:
        """Load results from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = []
        for d in data:
            result = BattleResult(
                ticks=d['ticks'],
                winner=d['winner'],
                duration_seconds=d.get('duration_seconds', 0),
                scenario_name=d.get('scenario_name', ''),
                scenario_params=d.get('scenario_params', {}),
                timestamp=d.get('timestamp', '')
            )
            result.team_a = TeamStats(
                initial_units=d['team_a']['initial_units'],
                surviving_units=d['team_a']['surviving_units'],
                casualties=d['team_a']['casualties'],
                total_damage_dealt=d['team_a'].get('total_damage_dealt', 0),
                total_damage_taken=d['team_a'].get('total_damage_taken', 0),
            )
            result.team_b = TeamStats(
                initial_units=d['team_b']['initial_units'],
                surviving_units=d['team_b']['surviving_units'],
                casualties=d['team_b']['casualties'],
                total_damage_dealt=d['team_b'].get('total_damage_dealt', 0),
                total_damage_taken=d['team_b'].get('total_damage_taken', 0),
            )
            results.append(result)
        
        return results
