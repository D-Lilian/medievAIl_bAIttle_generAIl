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
            print("Error: PlotLanchester requires 'Lanchester' scenario (N vs 2N).")
            print(f"Usage: ./battle plot {ai} PlotLanchester Lanchester '[types]' 'range(...)'")
            return {"error": "PlotLanchester requires Lanchester scenario"}
        
        if is_lanchester_scenario and not is_lanchester_plotter:
            print("Error: 'Lanchester' scenario should only be used with PlotLanchester.")
            print("For other plots, use a different scenario (e.g., 'classic', 'shield_wall').")
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
        data_path = Path(PlotController.DEFAULT_OUTPUT_DIR) / "data.csv"
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
        
        @details Lanchester's Laws for N vs 2N scenario:
        - Linear Law (Melee): Team B casualties = N (slope ≈ 1.0)
        - Square Law (Ranged): Team B casualties ≈ 0.27*N (slope ≈ 0.27)
        
        Both predict linear scaling, but with different slopes.
        We fit a linear model and compare the slope to theoretical predictions.
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
        
        # Theoretical slopes for N vs 2N scenario
        # Linear Law (Melee): casualties = N → slope = 1.0
        # Square Law (Ranged): casualties = 2N - sqrt(4N² - N²) = 2N - N*sqrt(3) ≈ 0.27N → slope ≈ 0.27
        THEORETICAL_SLOPE_LINEAR = 1.0
        THEORETICAL_SLOPE_SQUARE = 2.0 - np.sqrt(3)  # ≈ 0.268
        
        # Test Lanchester laws for each unit type
        # Use Team B casualties (2N side) for analysis
        for unit_type in data.unit_types:
            type_data = summary[summary['unit_type'] == unit_type]
            
            if len(type_data) < 2:
                continue
            
            n_values = type_data['n_value'].values
            casualties = type_data['mean_team_b_casualties'].values
            
            # Skip if all casualties are zero or constant (no variance)
            if np.std(casualties) == 0 or len(n_values) < 2:
                results['lanchester_tests'][unit_type] = {
                    'slope': 0.0,
                    'r2': 0.0,
                    'theoretical_linear': THEORETICAL_SLOPE_LINEAR,
                    'theoretical_square': THEORETICAL_SLOPE_SQUARE,
                    'best_fit': "N/A (constant casualties)",
                    'interpretation': f"Casualties are constant ({casualties[0]:.1f}) - 2:1 advantage too dominant."
                }
                continue
            
            # Fit linear model: casualties = slope * N + intercept
            try:
                slope, intercept = np.polyfit(n_values, casualties, 1)
                linear_pred = slope * n_values + intercept
                ss_res = np.sum((casualties - linear_pred)**2)
                ss_tot = np.sum((casualties - np.mean(casualties))**2)
                r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            except Exception:
                slope, intercept, r2 = 0, 0, 0
            
            # Compare slope to theoretical predictions
            error_linear = abs(slope - THEORETICAL_SLOPE_LINEAR)
            error_square = abs(slope - THEORETICAL_SLOPE_SQUARE)
            
            if error_linear < error_square:
                best_fit = "Linear Law"
            else:
                best_fit = "Square Law"
            
            results['lanchester_tests'][unit_type] = {
                'slope': float(slope),
                'intercept': float(intercept),
                'r2': float(r2),
                'theoretical_linear': THEORETICAL_SLOPE_LINEAR,
                'theoretical_square': THEORETICAL_SLOPE_SQUARE,
                'best_fit': best_fit,
                'slope_error': float(min(error_linear, error_square)),
                'interpretation': PlotController._interpret_lanchester(unit_type, slope, r2, THEORETICAL_SLOPE_LINEAR, THEORETICAL_SLOPE_SQUARE)
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
    def _interpret_lanchester(unit_type: str, slope: float, r2: float, 
                              theoretical_linear: float, theoretical_square: float) -> str:
        """
        @brief Generate interpretation of Lanchester test results.
        
        @details Compares observed slope to theoretical predictions:
        - Linear Law (Melee): slope ≈ 1.0 (each Team A unit kills one Team B unit)
        - Square Law (Ranged): slope ≈ 0.27 (focus fire reduces casualties)
        """
        is_melee = unit_type.lower() in ['knight', 'pikeman', 'infantry', 'melee']
        is_ranged = unit_type.lower() in ['crossbowman', 'crossbow', 'archer', 'ranged']
        
        # Check if slope is close to zero (2:1 advantage too dominant)
        if slope < 0.05:
            return "Slope ≈ 0: The 2:1 numerical advantage is overwhelming. Team B wins with minimal casualties."
        
        # Determine which law the data matches
        error_linear = abs(slope - theoretical_linear)
        error_square = abs(slope - theoretical_square)
        
        if error_linear < error_square:
            observed_law = "Linear Law"
            expected_slope = theoretical_linear
        else:
            observed_law = "Square Law"
            expected_slope = theoretical_square
        
        # Generate interpretation
        if is_melee and observed_law == "Linear Law":
            return f"✓ Slope={slope:.3f} (expected ≈{expected_slope:.2f}). Melee unit follows Linear Law as expected."
        elif is_ranged and observed_law == "Square Law":
            return f"✓ Slope={slope:.3f} (expected ≈{expected_slope:.2f}). Ranged unit follows Square Law as expected."
        elif is_melee and observed_law == "Square Law":
            return f"⚠ Slope={slope:.3f}. Melee unit shows Square Law behavior (R²={r2:.3f})."
        elif is_ranged and observed_law == "Linear Law":
            return f"⚠ Slope={slope:.3f}. Ranged unit shows Linear Law behavior (R²={r2:.3f})."
        else:
            return f"Slope={slope:.3f}, R²={r2:.3f}. Closest to {observed_law}."
    
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
