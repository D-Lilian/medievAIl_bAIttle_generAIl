# -*- coding: utf-8 -*-
"""
@file       data.py
@brief      Pandas DataFrame-based data structures for battle analysis.

@details    Data science approach using pandas DataFrames for storage and analysis.

@par Essential Schema (BATTLE_COLUMNS):
    - run_id: int
    - unit_type: str
    - n_value: int
    - team_a_casualties: int
    - team_b_casualties: int
    - winner: str
    - winner_casualties: int
    - duration_ticks: int

@see BATTLE_COLUMNS_EXTENDED for detailed analysis columns.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json

import pandas as pd
import numpy as np


## @defgroup DataSchema DataFrame Schema Definitions
## @{

## @var BATTLE_COLUMNS
#  @brief Essential columns for Lanchester analysis (optimized for speed).
BATTLE_COLUMNS = [
    'run_id',
    'unit_type',
    'n_value',
    'team_a_casualties',
    'team_b_casualties',
    'winner',
    'winner_casualties',
    'duration_ticks',
]

## @var BATTLE_COLUMNS_EXTENDED
#  @brief Extended columns for detailed analysis.
BATTLE_COLUMNS_EXTENDED = BATTLE_COLUMNS + [
    'team_a_initial',
    'team_b_initial',
    'team_a_survivors',
    'team_b_survivors',
    'loser_casualties',
    'ai_name',
    'scenario',
    'timestamp',
    'repetition'
]

## @var DTYPES
#  @brief Data types for DataFrame columns.
## @}
DTYPES = {
    'run_id': 'int64',
    'unit_type': 'string',
    'n_value': 'int64',
    'team_a_casualties': 'int64',
    'team_b_casualties': 'int64',
    'winner': 'string',
    'winner_casualties': 'int64',
    'duration_ticks': 'int64',
}


def create_empty_dataframe() -> pd.DataFrame:
    """
    @brief  Create an empty DataFrame with the correct schema.
    @return pd.DataFrame with BATTLE_COLUMNS structure.
    """
    df = pd.DataFrame(columns=BATTLE_COLUMNS)
    return df


## @class LanchesterData
#  @brief Container for Lanchester analysis data with pandas DataFrame.

@dataclass
class LanchesterData:
    """
    @brief  Container for Lanchester analysis data.
    
    @details Stores simulation results in a pandas DataFrame and provides
             aggregation methods for analysis.
    
    @par Workflow:
    @code
        for unit_type in [Knight, Crossbow]:
            for N in range(1, 100):
                data[unit_type, N] = Lanchester(unit_type, N).run()
        PlotLanchester(data)
    @endcode
    """
    df: pd.DataFrame = field(default_factory=create_empty_dataframe)
    
    # Metadata
    ai_name: str = ""
    scenario_name: str = "Lanchester"
    unit_types: List[str] = field(default_factory=list)
    n_range: List[int] = field(default_factory=list)
    num_repetitions: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_result(self, result: Dict[str, Any]):
        """
        @brief  Add a single simulation result to the DataFrame.
        @param  result Dict containing battle result fields.
        """
        new_row = pd.DataFrame([result])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
    
    def add_results(self, results: List[Dict[str, Any]]):
        """
        @brief  Add multiple simulation results (batch mode).
        @param  results List of result dictionaries.
        """
        new_df = pd.DataFrame(results)
        # Avoid FutureWarning by using proper concatenation
        if self.df.empty:
            self.df = new_df
        else:
            self.df = pd.concat([self.df, new_df], ignore_index=True)
    
    ## @name Aggregation Methods
    ## @{
    
    def get_summary_by_type_and_n(self) -> pd.DataFrame:
        """
        @brief  Get aggregated statistics grouped by unit_type and n_value.
        @return pd.DataFrame with mean/std for casualties, win rates, duration.
        """
        if self.df.empty:
            return pd.DataFrame()
        
        # Group by type and N
        grouped = self.df.groupby(['unit_type', 'n_value'])
        
        # Compute aggregations (optimized - only essential columns)
        agg = grouped.agg(
            # Casualties statistics
            mean_team_a_casualties=('team_a_casualties', 'mean'),
            std_team_a_casualties=('team_a_casualties', 'std'),
            mean_team_b_casualties=('team_b_casualties', 'mean'),
            std_team_b_casualties=('team_b_casualties', 'std'),
            mean_winner_casualties=('winner_casualties', 'mean'),
            std_winner_casualties=('winner_casualties', 'std'),
            
            # Duration
            mean_duration=('duration_ticks', 'mean'),
            std_duration=('duration_ticks', 'std'),
            
            # Count
            n_runs=('run_id', 'count')
        ).reset_index()
        
        # Compute win rates separately (lambda not supported in named agg)
        def compute_win_rates(group):
            return pd.Series({
                'team_a_win_rate': (group['winner'] == 'A').mean(),
                'team_b_win_rate': (group['winner'] == 'B').mean(),
                'draw_rate': (group['winner'] == 'draw').mean()
            })
        
        win_rates = self.df.groupby(['unit_type', 'n_value']).apply(
            compute_win_rates, include_groups=False
        ).reset_index()
        
        # Merge
        summary = agg.merge(win_rates, on=['unit_type', 'n_value'])
        
        # Fill NaN std with 0 (for single runs)
        # Use ffill pattern to avoid FutureWarning about downcasting
        for col in summary.select_dtypes(include=['float64']).columns:
            summary[col] = summary[col].fillna(0)
        
        return summary
    
    def get_casualties_for_plot(self) -> pd.DataFrame:
        """
        @brief  Get data formatted for Lanchester casualty plotting.
        @return pd.DataFrame in long format (unit_type, n, casualties, std).
        """
        summary = self.get_summary_by_type_and_n()
        if summary.empty:
            return pd.DataFrame()
        
        # Melt for long format (better for ggplot)
        plot_df = summary[['unit_type', 'n_value', 
                           'mean_winner_casualties', 'std_winner_casualties',
                           'mean_team_b_casualties', 'std_team_b_casualties',
                           'team_b_win_rate', 'mean_duration']].copy()
        
        # Rename for clarity in plots
        plot_df.columns = ['unit_type', 'n', 
                           'winner_casualties', 'winner_casualties_std',
                           'team_2n_casualties', 'team_2n_casualties_std',
                           'team_2n_win_rate', 'duration']
        
        return plot_df
    
    def get_full_summary(self) -> pd.DataFrame:
        """
        @brief  Get summary statistics aggregated by unit type.
        @return pd.DataFrame with one row per unit type.
        """
        if self.df.empty:
            return pd.DataFrame()
        
        grouped = self.df.groupby('unit_type')
        
        summary = grouped.agg(
            total_runs=('run_id', 'count'),
            n_range_min=('n_value', 'min'),
            n_range_max=('n_value', 'max'),
            mean_casualties_a=('team_a_casualties', 'mean'),
            mean_casualties_b=('team_b_casualties', 'mean'),
            total_duration=('duration_ticks', 'sum'),
        ).reset_index()
        
        # Win rates
        def win_rate_a(x):
            return (x == 'A').mean()
        def win_rate_b(x):
            return (x == 'B').mean()
        
        win_a = self.df.groupby('unit_type')['winner'].apply(win_rate_a).reset_index()
        win_a.columns = ['unit_type', 'overall_team_a_win_rate']
        
        win_b = self.df.groupby('unit_type')['winner'].apply(win_rate_b).reset_index()
        win_b.columns = ['unit_type', 'overall_team_b_win_rate']
        
        summary = summary.merge(win_a, on='unit_type').merge(win_b, on='unit_type')
        
        return summary
    
    ## @}

    def to_long_format(self) -> pd.DataFrame:
        """
        @brief  Convert data to long format for ggplot-style plotting.
        @return pd.DataFrame with columns: unit_type, n_value, metric, value, std.
        """
        summary = self.get_summary_by_type_and_n()
        if summary.empty:
            return pd.DataFrame()
        
        # Metrics to include
        metrics = [
            ('mean_winner_casualties', 'std_winner_casualties', 'Winner Casualties'),
            ('mean_team_b_casualties', 'std_team_b_casualties', 'Team 2N Casualties'),
            ('team_b_win_rate', None, 'Win Rate (2N team)'),
            ('mean_duration', 'std_duration', 'Battle Duration'),
        ]
        
        records = []
        for _, row in summary.iterrows():
            for mean_col, std_col, metric_name in metrics:
                value = row[mean_col]
                std = row[std_col] if std_col else 0
                
                # Scale win rate to percentage
                if 'rate' in mean_col.lower():
                    value *= 100
                    std = 0  # No std for rates
                
                records.append({
                    'unit_type': row['unit_type'],
                    'n_value': row['n_value'],
                    'metric': metric_name,
                    'value': value,
                    'std': std
                })
        
        return pd.DataFrame(records)

    ## @name I/O Methods
    ## @{
    
    def save_csv(self, filepath: str):
        """@brief Save raw data to CSV file."""
        self.df.to_csv(filepath, index=False)
    
    def save_parquet(self, filepath: str):
        """@brief Save raw data to Parquet format (faster, smaller)."""
        self.df.to_parquet(filepath, index=False)
    
    @classmethod
    def load_csv(cls, filepath: str) -> 'LanchesterData':
        """@brief Load data from CSV file."""
        data = cls()
        data.df = pd.read_csv(filepath)
        return data
    
    def to_dict(self) -> Dict[str, Any]:
        """@brief Export to dictionary for JSON serialization."""
        return {
            'data': self.df.to_dict(orient='records'),
            'metadata': {
                'ai_name': self.ai_name,
                'scenario_name': self.scenario_name,
                'unit_types': self.unit_types,
                'n_range': self.n_range,
                'num_repetitions': self.num_repetitions,
                'timestamp': self.timestamp,
                'total_simulations': len(self.df)
            }
        }
    
    def save_json(self, filepath: str):
        """@brief Save to JSON format (web compatible)."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
    
    ## @}


## @defgroup LegacyClasses Legacy Compatibility Classes
## @{

@dataclass
class TeamStats:
    """
    @brief  Statistics for a single team in a battle.
    @deprecated Use LanchesterData DataFrame columns instead.
    """
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
        if self.initial_units == 0:
            return 0.0
        return self.casualties / self.initial_units
    
    @property 
    def hp_loss_rate(self) -> float:
        if self.total_initial_hp == 0:
            return 0.0
        return (self.total_initial_hp - self.total_remaining_hp) / self.total_initial_hp


@dataclass 
class BattleResult:
    """
    @brief  Complete result from a single battle simulation.
    @deprecated Use LanchesterData DataFrame rows instead.
    """
    ticks: int = 0
    winner: Optional[str] = None
    team_a: TeamStats = field(default_factory=TeamStats)
    team_b: TeamStats = field(default_factory=TeamStats)
    duration_seconds: float = 0.0
    scenario_name: str = ""
    scenario_params: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
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
    
    def to_dataframe_row(self, run_id: int, unit_type: str, n_value: int, 
                         ai_name: str, repetition: int) -> Dict[str, Any]:
        """@brief Convert to a DataFrame row dictionary."""
        winner_cas = 0
        loser_cas = 0
        
        if self.winner == 'A':
            winner_cas = self.team_a.casualties
            loser_cas = self.team_b.casualties
        elif self.winner == 'B':
            winner_cas = self.team_b.casualties
            loser_cas = self.team_a.casualties
        
        return {
            'run_id': run_id,
            'unit_type': unit_type,
            'n_value': n_value,
            'team_a_initial': self.team_a.initial_units,
            'team_b_initial': self.team_b.initial_units,
            'team_a_survivors': self.team_a.surviving_units,
            'team_b_survivors': self.team_b.surviving_units,
            'team_a_casualties': self.team_a.casualties,
            'team_b_casualties': self.team_b.casualties,
            'team_a_hp_damage': self.team_a.total_damage_taken,
            'team_b_hp_damage': self.team_b.total_damage_taken,
            'team_a_damage_dealt': self.team_a.total_damage_dealt,
            'team_b_damage_dealt': self.team_b.total_damage_dealt,
            'winner': self.winner,
            'winner_casualties': winner_cas,
            'loser_casualties': loser_cas,
            'duration_ticks': self.ticks,
            'ai_name': ai_name,
            'scenario': self.scenario_name,
            'timestamp': self.timestamp,
            'repetition': repetition
        }


@dataclass
class AggregatedResults:
    """
    @brief  Aggregated results from multiple simulation runs.
    @deprecated Use LanchesterData.get_summary_by_type_and_n() instead.
    """
    scenario_name: str
    scenario_params: Dict[str, Any]
    num_runs: int
    results: List[BattleResult] = field(default_factory=list)
    
    @property
    def avg_team_a_casualties(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.team_a.casualties for r in self.results) / len(self.results)
    
    @property
    def avg_team_b_casualties(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.team_b.casualties for r in self.results) / len(self.results)
    
    @property
    def avg_team_a_survivors(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.team_a.surviving_units for r in self.results) / len(self.results)
    
    @property
    def avg_team_b_survivors(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.team_b.surviving_units for r in self.results) / len(self.results)
    
    @property
    def avg_ticks(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.ticks for r in self.results) / len(self.results)
    
    @property
    def team_a_win_rate(self) -> float:
        if not self.results:
            return 0.0
        wins = sum(1 for r in self.results if r.winner == 'A')
        return wins / len(self.results)
    
    @property
    def team_b_win_rate(self) -> float:
        if not self.results:
            return 0.0
        wins = sum(1 for r in self.results if r.winner == 'B')
        return wins / len(self.results)
    
    @property
    def draw_rate(self) -> float:
        if not self.results:
            return 0.0
        draws = sum(1 for r in self.results if r.winner == 'draw')
        return draws / len(self.results)
    
    def add_result(self, result: BattleResult):
        self.results.append(result)
        self.num_runs = len(self.results)


@dataclass
class PlotData:
    """
    @brief  Data structure for scenario plotting.
    @deprecated Use LanchesterData.to_long_format() instead.
    """
    unit_type: str
    ai_name: str = ""
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
        self.n_values.append(n)
        self.avg_team_a_casualties.append(aggregated.avg_team_a_casualties)
        self.avg_team_b_casualties.append(aggregated.avg_team_b_casualties)
        self.avg_team_a_survivors.append(aggregated.avg_team_a_survivors)
        self.avg_team_b_survivors.append(aggregated.avg_team_b_survivors)
        self.team_a_win_rates.append(aggregated.team_a_win_rate)
        self.team_b_win_rates.append(aggregated.team_b_win_rate)
        self.avg_ticks.append(aggregated.avg_ticks)
        
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
    @brief  Collects battle statistics from simulation scenarios.
    @deprecated Use DataCollector from collector.py instead.
    """
    
    @staticmethod
    def collect_from_scenario(scenario, simulation_output: dict) -> BattleResult:
        """
        @brief  Collect battle statistics from a completed simulation.
        @param  scenario The Scenario object that was simulated.
        @param  simulation_output Output dict from Simulation.simulate().
        @return BattleResult containing all collected statistics.
        """
        result = BattleResult()
        result.ticks = simulation_output.get('ticks', 0)
        
        # Team A stats
        team_a = TeamStats()
        team_a.initial_units = len(scenario.units_a)
        team_a.surviving_units = sum(1 for u in scenario.units_a if u.hp > 0)
        team_a.casualties = team_a.initial_units - team_a.surviving_units
        team_a.total_damage_dealt = sum(getattr(u, 'damage_dealt', 0) for u in scenario.units_a)
        team_a.total_initial_hp = sum(getattr(u, 'max_hp', 100) for u in scenario.units_a)
        team_a.total_remaining_hp = sum(max(u.hp, 0) for u in scenario.units_a)
        
        # Team B stats  
        team_b = TeamStats()
        team_b.initial_units = len(scenario.units_b)
        team_b.surviving_units = sum(1 for u in scenario.units_b if u.hp > 0)
        team_b.casualties = team_b.initial_units - team_b.surviving_units
        team_b.total_damage_dealt = sum(getattr(u, 'damage_dealt', 0) for u in scenario.units_b)
        team_b.total_initial_hp = sum(getattr(u, 'max_hp', 100) for u in scenario.units_b)
        team_b.total_remaining_hp = sum(max(u.hp, 0) for u in scenario.units_b)
        
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
        """@brief Save results list to JSON file."""
        data = [r.to_dict() for r in results]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_results(filepath: str) -> List[BattleResult]:
        """@brief Load results list from JSON file."""
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
