# -*- coding: utf-8 -*-
"""
@file plot_runner.py
@brief Plot Runner - Orchestrates data collection and plotting for analysis

@details
Provides the infrastructure to run multiple simulations with varying parameters,
collect results, and generate plots. Follows KISS principle with simple,
focused functions.

"""

import copy
import os
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime

from Model.simulation import Simulation
from Model.scenario import Scenario
from Model.generals import General
from Model.strategies import StrategieBrainDead, StrategieDAFT
from Model.units import UnitType

from Utils.battle_data import (
    BattleResult, BattleDataCollector, AggregatedResults, PlotData
)
from Utils.plotters import get_plotter, PLOTTERS
from Utils.lanchester_scenario import Lanchester, LanchesterScenario


class PlotRunner:
    """
    Orchestrates running simulations and generating plots.
    
    Manages the workflow of:
    1. Creating scenarios with varying parameters
    2. Running simulations multiple times
    3. Collecting and aggregating results
    4. Generating plots and reports
    """
    
    def __init__(self, ai_name: str = 'DAFT', num_repetitions: int = 10,
                 output_dir: str = "Reports"):
        """
        Initialize the plot runner.
        
        @param ai_name: Name of AI to use for simulations
        @param num_repetitions: Number of times to repeat each scenario
        @param output_dir: Directory for output files
        """
        self.ai_name = ai_name
        self.num_repetitions = num_repetitions
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def run_lanchester_analysis(self, unit_types: List[str], 
                                 n_range: range) -> Dict[str, PlotData]:
        """
        Run Lanchester analysis for given unit types and N range.
        
        @param unit_types: List of unit type names ['Knight', 'Crossbowman']
        @param n_range: Range of N values to test
        @return: Dictionary mapping unit type to PlotData
        """
        all_data = {}
        
        for unit_type in unit_types:
            print(f"\n{'='*50}")
            print(f"Running Lanchester analysis for {unit_type}")
            print(f"{'='*50}")
            
            plot_data = PlotData(unit_type=unit_type)
            
            for n in n_range:
                print(f"  N={n}: Running {self.num_repetitions} simulations...", end='', flush=True)
                
                aggregated = self._run_scenario_batch(
                    scenario_factory=lambda: Lanchester(unit_type, n),
                    scenario_name='Lanchester',
                    scenario_params={'unit_type': unit_type, 'n': n}
                )
                
                plot_data.add_data_point(n, aggregated)
                
                # Print summary
                win_rate = aggregated.team_b_win_rate * 100
                avg_b_cas = aggregated.avg_team_b_casualties
                print(f" Done. 2N win rate: {win_rate:.1f}%, 2N casualties: {avg_b_cas:.1f}")
            
            all_data[unit_type] = plot_data
        
        return all_data
    
    def _run_scenario_batch(self, scenario_factory: Callable[[], Scenario],
                            scenario_name: str,
                            scenario_params: Dict[str, Any]) -> AggregatedResults:
        """
        Run a batch of simulations for the same scenario configuration.
        
        @param scenario_factory: Function that creates a fresh Scenario
        @param scenario_name: Name of the scenario
        @param scenario_params: Parameters used to create the scenario
        @return: Aggregated results from all runs
        """
        aggregated = AggregatedResults(
            scenario_name=scenario_name,
            scenario_params=scenario_params,
            num_runs=0
        )
        
        for i in range(self.num_repetitions):
            # Create fresh scenario for each run
            scenario = scenario_factory()
            
            # Assign generals
            scenario.general_a = self._create_general(
                self.ai_name, scenario.units_a, scenario.units_b
            )
            scenario.general_b = self._create_general(
                self.ai_name, scenario.units_b, scenario.units_a
            )
            
            # Run simulation
            sim = Simulation(
                scenario,
                tick_speed=5,
                unlocked=True,  # Run as fast as possible
                paused=False
            )
            
            output = sim.simulate()
            
            # Collect results
            result = BattleDataCollector.collect_from_scenario(scenario, output)
            result.scenario_name = scenario_name
            result.scenario_params = scenario_params
            
            aggregated.add_result(result)
        
        return aggregated
    
    def _create_general(self, name: str, units_a, units_b) -> General:
        """Create a general with the specified AI strategy."""
        name_up = name.upper()
        
        if name_up == 'BRAINDEAD':
            strategy_map = {
                UnitType.CROSSBOWMAN: StrategieBrainDead(None),
                UnitType.KNIGHT: StrategieBrainDead(None),
                UnitType.PIKEMAN: StrategieBrainDead(None),
            }
        else:  # Default to DAFT
            strategy_map = {
                UnitType.CROSSBOWMAN: StrategieDAFT(None),
                UnitType.KNIGHT: StrategieDAFT(None),
                UnitType.PIKEMAN: StrategieDAFT(None),
            }
        
        return General(unitsA=units_a, unitsB=units_b, sS=None, sT=strategy_map)
    
    def generate_plot(self, plotter_name: str, data: Dict[str, PlotData]) -> str:
        """
        Generate a plot using the specified plotter.
        
        @param plotter_name: Name of the plotter to use
        @param data: Data to plot
        @return: Path to generated plot file
        """
        plotter = get_plotter(plotter_name, self.output_dir)
        return plotter.plot(data)
    
    def generate_report(self, data: Dict[str, PlotData], 
                        plot_path: str,
                        scenario_name: str = "Lanchester") -> str:
        """
        Generate a markdown report for the analysis.
        
        @param data: Plot data used for analysis
        @param plot_path: Path to the generated plot
        @param scenario_name: Name of the scenario analyzed
        @return: Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.output_dir, f"{scenario_name}_report_{timestamp}.md")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report(data, plot_path, scenario_name))
        
        print(f"\nReport generated: {report_path}")
        return report_path
    
    def _generate_markdown_report(self, data: Dict[str, PlotData],
                                   plot_path: str,
                                   scenario_name: str) -> str:
        """Generate markdown content for the report."""
        
        lines = [
            f"# {scenario_name} Analysis Report",
            f"",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"**AI Used:** {self.ai_name}",
            f"",
            f"**Repetitions per configuration:** {self.num_repetitions}",
            f"",
            f"---",
            f"",
            f"## Overview",
            f"",
            f"This report analyzes the battle outcomes for different unit types ",
            f"under the Lanchester scenario (N units vs 2N units).",
            f"",
            f"### Lanchester's Laws",
            f"",
            f"- **Linear Law (Melee):** In ancient/melee combat, casualties are ",
            f"  proportional to the number of soldiers. Advantages scale linearly.",
            f"",
            f"- **Square Law (Ranged):** In modern/ranged combat, fighting effectiveness ",
            f"  scales with the square of the number of soldiers.",
            f"",
            f"---",
            f"",
            f"## Results by Unit Type",
            f"",
        ]
        
        for unit_type, plot_data in data.items():
            lines.extend([
                f"### {unit_type}",
                f"",
            ])
            
            if plot_data.n_values:
                # Create summary table
                lines.extend([
                    f"| N | Team A (N) Casualties | Team B (2N) Casualties | Team B Win Rate |",
                    f"|---|----------------------|------------------------|-----------------|",
                ])
                
                for i, n in enumerate(plot_data.n_values):
                    if i < len(plot_data.avg_team_a_casualties):
                        a_cas = plot_data.avg_team_a_casualties[i]
                        b_cas = plot_data.avg_team_b_casualties[i]
                        b_win = plot_data.team_b_win_rates[i] * 100
                        lines.append(f"| {n} | {a_cas:.1f} | {b_cas:.1f} | {b_win:.1f}% |")
                
                lines.append("")
        
        # Add plot reference
        plot_filename = os.path.basename(plot_path)
        lines.extend([
            f"---",
            f"",
            f"## Visualization",
            f"",
            f"![{scenario_name} Analysis](./{plot_filename})",
            f"",
            f"---",
            f"",
            f"## Interpretation",
            f"",
            f"- If melee units (Knight) show **linear** casualty scaling with N, ",
            f"  this confirms Lanchester's Linear Law.",
            f"",
            f"- If ranged units (Crossbowman) show **quadratic** casualty scaling with N, ",
            f"  this confirms Lanchester's Square Law.",
            f"",
            f"- The larger army (2N) should consistently win in all configurations.",
            f"",
            f"---",
            f"",
            f"*Report generated by MedievAIl bAIttle generAIl*",
        ])
        
        return "\n".join(lines)


def run_plot_command(ai: str, plotter: str, scenario_name: str, 
                     param_name: str, param_values: List[Any],
                     num_repetitions: int = 10) -> None:
    """
    Execute the plot command from CLI.
    
    @param ai: AI name to use
    @param plotter: Plotter name to use
    @param scenario_name: Scenario to run
    @param param_name: Parameter to vary
    @param param_values: Values for the varying parameter
    @param num_repetitions: Number of repetitions per configuration
    """
    runner = PlotRunner(ai_name=ai, num_repetitions=num_repetitions)
    
    if scenario_name.lower() == 'lanchester':
        # For Lanchester, param_values should be unit types
        # and we need a range for N
        
        # Parse param_values as [unit_types, n_range]
        # Default behavior: treat first as unit types list, generate default range
        if isinstance(param_values, list) and len(param_values) > 0:
            unit_types = param_values if isinstance(param_values[0], str) else ['Knight', 'Crossbowman']
        else:
            unit_types = ['Knight', 'Crossbowman']
        
        # Default N range for Lanchester
        n_range = range(5, 51, 5)
        
        print(f"\nRunning Lanchester Analysis")
        print(f"  Unit types: {unit_types}")
        print(f"  N range: {list(n_range)}")
        print(f"  Repetitions: {num_repetitions}")
        
        data = runner.run_lanchester_analysis(unit_types, n_range)
        
        plot_path = runner.generate_plot(plotter, data)
        print(f"\nPlot generated: {plot_path}")
        
        report_path = runner.generate_report(data, plot_path, scenario_name)
        
    else:
        print(f"Unknown scenario: {scenario_name}")
        print(f"Available scenarios: Lanchester")
