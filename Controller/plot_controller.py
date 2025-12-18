# -*- coding: utf-8 -*-
"""
@file       plot_controller.py
@brief      Orchestrates Lanchester analysis workflow.

@details    Complete workflow:
            1. Data collection (simulations -> DataFrame)
            2. Plot generation (plotnine)
            3. Statistical analysis
            4. HTML report generation

@see DataCollector, PlotReportGenerator
"""

import os
import re
import webbrowser
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

import pandas as pd
import numpy as np

from Plotting import (
    DataCollector, 
    parse_types_arg, 
    parse_range_arg,
    PLOTTERS, 
    get_plotter,
    PlotReportGenerator,
    LanchesterData,
)


class PlotController:
    """
    @brief  Controller for Lanchester analysis and plot generation.
    
    @details Coordinates data collection, plotting, statistical analysis,
             and report generation.
    """
    
    ## @var DEFAULT_OUTPUT_DIR
    #  @brief Default directory for output files.
    DEFAULT_OUTPUT_DIR = "Reports"
    
    @staticmethod
    def run_plot(args) -> Dict[str, Optional[str]]:
        """
        @brief  Run plot command from CLI arguments.
        @param  args CLI arguments from argparse.
        @return Dictionary with paths to generated files.
        """
        # Parse arguments
        ai = args.ai
        plotter_name = args.plotter
        scenario = args.scenario
        
        # Parse types: "[Knight,Crossbow]" -> ["Knight", "Crossbow"]
        unit_types = parse_types_arg(args.types)
        
        # Parse range: "range(20,100,20)" -> range(20, 100, 20)
        n_range = parse_range_arg(args.range_expr)
        
        num_reps = args.N
        
        # Validate plotter
        if plotter_name not in PLOTTERS:
            print(f"Error: Unknown plotter '{plotter_name}'. Available: {list(PLOTTERS.keys())}")
            return {"error": "Unknown plotter"}
        
        # Check Lanchester plotter/scenario consistency
        is_lanchester_plotter = plotter_name.lower() in ('plotlanchester', 'lanchester')
        is_lanchester_scenario = scenario.lower() == "lanchester"
        
        if is_lanchester_plotter and not is_lanchester_scenario:
            print(f"Error: PlotLanchester requires 'Lanchester' scenario (N vs 2N).")
            print(f"Usage: ./battle plot {ai} PlotLanchester Lanchester '[types]' 'range(...)'")
            return {"error": "PlotLanchester requires Lanchester scenario"}
        
        if is_lanchester_scenario and not is_lanchester_plotter:
            print(f"Error: 'Lanchester' scenario should only be used with PlotLanchester.")
            print(f"For other plots, use a different scenario (e.g., 'classic', 'shield_wall').")
            return {"error": "Lanchester scenario requires PlotLanchester"}
        
        # Display compact config
        if is_lanchester_plotter:
            total_sims = len(unit_types) * len(n_range) * num_reps
            print(f"\nLanchester Analysis: {ai} | {', '.join(unit_types)} | N={list(n_range)} | {num_reps}x = {total_sims} sims")
        else:
            total_sims = len(unit_types) * len(n_range) * num_reps
            print(f"\n{plotter_name}: {ai} | {', '.join(unit_types)} | N={list(n_range)} | {num_reps}x = {total_sims} sims")
        
        collector = DataCollector(ai_name=ai, num_repetitions=num_reps)
        
        if is_lanchester_scenario:
            data = collector.collect_lanchester(unit_types, n_range)
        else:
            # For generic scenarios, use symmetric battles (N vs N)
            data = collector.collect_symmetric(unit_types, n_range)
        
        # Save raw data
        data_path = Path(PlotController.DEFAULT_OUTPUT_DIR) / "lanchester_data.csv"
        data.save_csv(str(data_path))
        
        # Generate plot
        plotter = get_plotter(plotter_name, output_dir=PlotController.DEFAULT_OUTPUT_DIR)
        plot_path = plotter.plot(data, ai_name=ai)
        
        # Only generate full report for PlotLanchester
        if is_lanchester_plotter:
            # Statistical analysis
            stats_results = PlotController._run_statistical_analysis(data, verbose=False)
            
            # Generate report (auto-opens in browser)
            report_gen = PlotReportGenerator(output_dir=PlotController.DEFAULT_OUTPUT_DIR)
            report_path = report_gen.generate(data, plot_path, stats_results, auto_open=True)
            
            # Compact summary
            PlotController._print_compact_summary(data, plot_path, report_path)
        else:
            report_path = None
            print(f"\n✓ Plot saved: {plot_path}")
        
        return {
            "data": str(data_path),
            "plot": str(plot_path),
            "report": str(report_path) if report_path else None
        }
    
    @staticmethod
    def _run_statistical_analysis(data: LanchesterData, verbose: bool = True) -> Dict[str, Any]:
        """
        @brief  Run statistical analysis testing Lanchester's Laws.
        @param  data LanchesterData with simulation results.
        @param  verbose Print progress to console.
        @return Dictionary with statistical test results.
        
        @details Tests Linear Law (casualties ∝ N) vs Square Law (casualties ∝ N²).
        """
        results = {
            'lanchester_tests': {},
            'descriptive': {},
            'raw_df_summary': None
        }
        
        if data.df.empty:
            return results
        
        # Get summary DataFrame
        summary = data.get_summary_by_type_and_n()
        
        if summary.empty:
            return results
        
        # Store raw summary
        results['raw_df_summary'] = summary.to_dict(orient='records')
        
        # Test Lanchester laws for each unit type
        for unit_type in data.unit_types:
            type_data = summary[summary['unit_type'] == unit_type]
            
            if len(type_data) < 3:
                continue
            
            n_values = type_data['n_value'].values
            casualties = type_data['mean_winner_casualties'].values
            
            # Skip if all casualties are zero or constant (no variance)
            if np.std(casualties) == 0:
                results['lanchester_tests'][unit_type] = {
                    'linear_r2': 0.0,
                    'quadratic_r2': 0.0,
                    'best_fit': "N/A (constant casualties)",
                    'best_r2': 0.0,
                    'interpretation': f"Casualties are constant ({casualties[0]:.1f}) - no scaling pattern detected."
                }
                continue
            
            # Fit linear model: casualties = a * N + b
            try:
                linear_coeffs = np.polyfit(n_values, casualties, 1)
                linear_pred = np.polyval(linear_coeffs, n_values)
                ss_res = np.sum((casualties - linear_pred)**2)
                ss_tot = np.sum((casualties - np.mean(casualties))**2)
                linear_r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            except:
                linear_r2 = 0
            
            # Fit quadratic model: casualties = a * N² + b * N + c
            try:
                quad_coeffs = np.polyfit(n_values, casualties, 2)
                quad_pred = np.polyval(quad_coeffs, n_values)
                ss_res = np.sum((casualties - quad_pred)**2)
                ss_tot = np.sum((casualties - np.mean(casualties))**2)
                quad_r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            except:
                quad_r2 = 0
            
            # Determine best fit
            best_fit = "Linear (Lanchester's Linear Law)" if linear_r2 > quad_r2 else "Quadratic (Lanchester's Square Law)"
            best_r2 = max(linear_r2, quad_r2)
            
            results['lanchester_tests'][unit_type] = {
                'linear_r2': float(linear_r2),
                'quadratic_r2': float(quad_r2),
                'best_fit': best_fit,
                'best_r2': float(best_r2),
                'interpretation': PlotController._interpret_lanchester(unit_type, linear_r2, quad_r2)
            }
        
        # Descriptive statistics by unit type
        for unit_type in data.unit_types:
            type_df = data.df[data.df['unit_type'] == unit_type]
            
            # Skip if no valid data for this unit type
            if len(type_df) == 0:
                results['descriptive'][unit_type] = {
                    'n_simulations': 0,
                    'casualties_mean': 0.0,
                    'casualties_std': 0.0,
                    'casualties_min': 0,
                    'casualties_max': 0,
                    'duration_mean': 0.0,
                    'win_rate_2n': 0.0,
                }
                continue
            
            results['descriptive'][unit_type] = {
                'n_simulations': len(type_df),
                'casualties_mean': float(type_df['winner_casualties'].mean()),
                'casualties_std': float(type_df['winner_casualties'].std()),
                'casualties_min': int(type_df['winner_casualties'].min()),
                'casualties_max': int(type_df['winner_casualties'].max()),
                'duration_mean': float(type_df['duration_ticks'].mean()),
                'win_rate_2n': float((type_df['winner'] == 'B').mean()),
            }
        
        return results
    
    @staticmethod
    def _interpret_lanchester(unit_type: str, linear_r2: float, quad_r2: float) -> str:
        """@brief Generate interpretation of Lanchester test results."""
        
        is_melee = unit_type.lower() in ['knight', 'pikeman', 'infantry', 'melee']
        is_ranged = unit_type.lower() in ['crossbowman', 'crossbow', 'archer', 'ranged']
        
        if linear_r2 > quad_r2:
            fit_type = "Linear Law"
            expected_for = "melee combat"
        else:
            fit_type = "Square Law"
            expected_for = "ranged combat"
        
        if is_melee and linear_r2 > quad_r2:
            return f"✓ As expected for melee units, casualties follow the Linear Law."
        elif is_ranged and quad_r2 > linear_r2:
            return f"✓ As expected for ranged units, casualties follow the Square Law."
        elif is_melee and quad_r2 > linear_r2:
            return f"⚠ Unexpected: Melee unit shows Square Law behavior (focus fire possible?)."
        elif is_ranged and linear_r2 > quad_r2:
            return f"⚠ Unexpected: Ranged unit shows Linear Law behavior (limited focus fire?)."
        else:
            return f"Unit follows {fit_type}, typical for {expected_for}."
    
    @staticmethod
    def _open_results(plot_path: str, report_path: str):
        """@brief Open plot and report in default applications."""
        print("\nOpening results...")
        
        # Open the plot image
        if plot_path and os.path.exists(plot_path):
            abs_plot = os.path.abspath(plot_path)
            if sys.platform == 'linux':
                subprocess.Popen(['xdg-open', abs_plot], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', abs_plot])
            else:
                os.startfile(abs_plot)
        
        # Open the report in browser
        if report_path and os.path.exists(report_path):
            abs_report = os.path.abspath(report_path)
            webbrowser.open(f"file://{abs_report}")
    
    @staticmethod
    def _print_compact_summary(data: LanchesterData, plot_path: Path, report_path: Path):
        """@brief Print compact summary line."""
        if not data.df.empty:
            stats = []
            for unit_type in data.unit_types:
                type_df = data.df[data.df['unit_type'] == unit_type]
                if len(type_df) > 0:
                    win_rate = (type_df['winner'] == 'B').mean() * 100
                    stats.append(f"{unit_type}: {win_rate:.0f}% win")
            if stats:
                print(f"Results: {' | '.join(stats)}")
        print(f"Output: {plot_path}")
