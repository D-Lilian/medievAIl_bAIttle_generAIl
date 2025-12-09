# -*- coding: utf-8 -*-
"""
@file base_plotter.py
@brief Base Plotter - Abstract class for data visualization

@details
Defines the BasePlotter abstract class for creating visualizations
from battle simulation results. Supports multiple output formats.

"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model.scenarios.base_scenario import BattleResult


class BasePlotter(ABC):
    """
    @brief Abstract base class for all plotters
    
    @details Defines the interface for creating visualizations
    from battle results. Supports multiple output formats:
    - Static images (matplotlib/seaborn)
    - Interactive plots (plotly)
    - Markdown reports
    - HTML dashboards
    """
    
    def __init__(self, output_dir: str = "Reports"):
        """
        @brief Initialize the plotter
        
        @param output_dir Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[BattleResult] = []
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this plotter"""
        pass
    
    def load_results(self, results: List[BattleResult]) -> 'BasePlotter':
        """
        @brief Load battle results for visualization
        
        @param results List of BattleResult objects
        @return self for method chaining
        """
        self.results = results
        return self
    
    def load_from_json(self, filepath: str) -> 'BasePlotter':
        """
        @brief Load results from a JSON file
        
        @param filepath Path to JSON file
        @return self for method chaining
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.results = []
        for item in data:
            result = BattleResult(
                scenario_name=item.get('scenario_name', ''),
                parameters=item.get('parameters', {}),
                team_a_initial=item['team_a']['initial'],
                team_a_remaining=item['team_a']['remaining'],
                team_a_casualties=item['team_a']['casualties'],
                team_a_total_hp_initial=item['team_a'].get('hp_initial', 0),
                team_a_total_hp_remaining=item['team_a'].get('hp_remaining', 0),
                team_a_damage_dealt=item['team_a'].get('damage_dealt', 0),
                team_b_initial=item['team_b']['initial'],
                team_b_remaining=item['team_b']['remaining'],
                team_b_casualties=item['team_b']['casualties'],
                team_b_total_hp_initial=item['team_b'].get('hp_initial', 0),
                team_b_total_hp_remaining=item['team_b'].get('hp_remaining', 0),
                team_b_damage_dealt=item['team_b'].get('damage_dealt', 0),
                ticks=item.get('ticks', 0),
                winner=item.get('winner', '')
            )
            self.results.append(result)
        return self
    
    def save_results_json(self, filename: str = "results.json") -> str:
        """
        @brief Save results to JSON file
        
        @param filename Output filename
        @return Path to saved file
        """
        filepath = self.output_dir / filename
        data = [r.to_dict() for r in self.results]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return str(filepath)
    
    @abstractmethod
    def plot(self, **kwargs) -> Any:
        """
        @brief Create the visualization
        
        @param kwargs Plotter-specific options
        @return Figure or plot object
        """
        pass
    
    @abstractmethod
    def save(self, filename: str, **kwargs) -> str:
        """
        @brief Save the visualization to a file
        
        @param filename Output filename
        @param kwargs Format-specific options
        @return Path to saved file
        """
        pass
    
    def to_markdown(self, filename: str = "report.md") -> str:
        """
        @brief Generate a markdown report
        
        @param filename Output filename
        @return Path to saved file
        """
        filepath = self.output_dir / filename
        
        md = f"# {self.name} Report\n\n"
        md += f"Generated from {len(self.results)} simulation results.\n\n"
        
        # Summary statistics
        md += "## Summary Statistics\n\n"
        md += self._generate_summary_table()
        
        # Detailed results
        md += "\n## Detailed Results\n\n"
        md += self._generate_results_table()
        
        with open(filepath, 'w') as f:
            f.write(md)
        
        return str(filepath)
    
    def _generate_summary_table(self) -> str:
        """Generate markdown summary table"""
        if not self.results:
            return "No results available.\n"
        
        # Group by unit type
        by_type: Dict[str, List[BattleResult]] = {}
        for r in self.results:
            ut = r.parameters.get('unit_type', 'unknown')
            if ut not in by_type:
                by_type[ut] = []
            by_type[ut].append(r)
        
        md = "| Unit Type | Simulations | Avg Team A Casualties | Avg Team B Casualties | Team B Win Rate |\n"
        md += "|-----------|-------------|----------------------|----------------------|-----------------|\n"
        
        for ut, results in by_type.items():
            n = len(results)
            avg_a_cas = sum(r.team_a_casualties for r in results) / n
            avg_b_cas = sum(r.team_b_casualties for r in results) / n
            b_wins = sum(1 for r in results if r.winner == 'B') / n * 100
            md += f"| {ut} | {n} | {avg_a_cas:.1f} | {avg_b_cas:.1f} | {b_wins:.1f}% |\n"
        
        return md
    
    def _generate_results_table(self) -> str:
        """Generate markdown results table"""
        if not self.results:
            return "No results available.\n"
        
        md = "| Scenario | N | A Init | A Rem | B Init | B Rem | Winner | Ticks |\n"
        md += "|----------|---|--------|-------|--------|-------|--------|-------|\n"
        
        for r in self.results[:50]:  # Limit to 50 rows
            n = r.parameters.get('n', '-')
            md += f"| {r.scenario_name} | {n} | {r.team_a_initial} | {r.team_a_remaining} | "
            md += f"{r.team_b_initial} | {r.team_b_remaining} | {r.winner} | {r.ticks} |\n"
        
        if len(self.results) > 50:
            md += f"\n*...and {len(self.results) - 50} more results*\n"
        
        return md
