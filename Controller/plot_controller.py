# -*- coding: utf-8 -*-
"""
@file plot_controller.py
@brief Plot Controller - Manages plotting and statistical analysis

@details
Handles plot generation, data collection, and statistical analysis.
Follows Single Responsibility Principle - only orchestrates plotting workflow.
"""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any

from Plotting import (
    DataCollector, 
    parse_types_arg, 
    parse_range_arg,
    PLOTTERS, 
    get_plotter,
    PlotReportGenerator
)


class PlotController:
    """
    Controller for plot generation and analysis.
    
    Handles:
    - Data collection from simulations
    - Plot generation with various plotters
    - Statistical analysis (optional)
    - Report generation
    """
    
    DEFAULT_OUTPUT_DIR = "Reports"
    
    @staticmethod
    def run_plot(args) -> Dict[str, Optional[str]]:
        """
        Run plot command from CLI arguments.
        
        @param args: CLI arguments
        @return: Dictionary with paths to generated files
        """
        # Parse arguments
        ai = args.ai
        plotter_name = args.plotter
        scenario = args.scenario
        types_str = args.types
        range_str = args.range_expr
        num_reps = args.N
        do_stats = getattr(args, "stats", False) or plotter_name.startswith("Advanced")
        
        # Parse types and range
        unit_types = parse_types_arg(types_str)
        n_range = parse_range_arg(range_str)
        
        # Display configuration
        PlotController._print_config(ai, plotter_name, scenario, unit_types, n_range, num_reps, do_stats)
        
        # Validate plotter
        if plotter_name not in PLOTTERS:
            print(f"\nError: Unknown plotter '{plotter_name}'")
            print(f"Available: {list(PLOTTERS.keys())}")
            return {"error": "Unknown plotter"}
        
        # Step 1: Collect data
        print(f"\n[Step 1/4] Collecting simulation data...")
        collector = DataCollector(ai_name=ai, num_repetitions=num_reps)
        
        if scenario.lower() == "lanchester":
            data = collector.collect_lanchester(unit_types, n_range)
        else:
            print(f"Error: Unknown scenario '{scenario}'")
            return {"error": "Unknown scenario"}
        
        # Step 2: Generate plot
        print(f"\n[Step 2/4] Generating plot with {plotter_name}...")
        plotter = get_plotter(plotter_name, output_dir=PlotController.DEFAULT_OUTPUT_DIR)
        plot_path = plotter.plot(data.plot_data)
        print(f"  Plot saved: {plot_path}")
        
        # Step 3: Statistical analysis
        stats_path = None
        if do_stats:
            stats_path = PlotController._run_statistical_analysis(data, unit_types)
        else:
            print(f"\n[Step 3/4] Skipping statistical analysis (use --stats to enable)")
        
        # Step 4: Generate report
        print(f"\n[Step 4/4] Generating markdown report...")
        report_gen = PlotReportGenerator(output_dir=PlotController.DEFAULT_OUTPUT_DIR)
        report_path = report_gen.generate(data, plot_path)
        print(f"  Report saved: {report_path}")
        
        # Print summary
        PlotController._print_summary(plot_path, report_path, stats_path)
        
        return {
            "plot": plot_path,
            "report": report_path,
            "stats": stats_path
        }
    
    @staticmethod
    def _print_config(ai: str, plotter: str, scenario: str, 
                      unit_types: List[str], n_range: range, 
                      num_reps: int, do_stats: bool):
        """Print configuration summary."""
        print(f"\n{'=' * 60}")
        print(f"PLOT COMMAND - {'FULL ANALYSIS' if do_stats else 'STANDARD'}")
        print(f"{'=' * 60}")
        print(f"  AI:          {ai}")
        print(f"  Plotter:     {plotter}")
        print(f"  Scenario:    {scenario}")
        print(f"  Types:       {unit_types}")
        n_list = list(n_range)
        range_str = f"{n_list[:3]}...{n_list[-1]}" if len(n_list) > 3 else str(n_list)
        print(f"  Range:       {range_str}")
        print(f"  Repetitions: {num_reps}")
        print(f"  Statistics:  {do_stats}")
        print(f"{'=' * 60}")
    
    @staticmethod
    def _run_statistical_analysis(data, unit_types: List[str]) -> Optional[str]:
        """Run statistical analysis and generate report."""
        print(f"\n[Step 3/4] Performing statistical analysis...")
        
        try:
            from Analysis import LanchesterAnalyzer, create_analysis_dataframe, AnalysisDashboard
            
            analyzer = LanchesterAnalyzer()
            
            # Test Lanchester laws
            print("  - Testing Lanchester Laws...")
            lanchester_results = analyzer.test_lanchester_law(data.plot_data)
            for unit_type, result in lanchester_results.items():
                print(f"    {unit_type}: {result['best_fit']} (R²={result['best_r2']:.3f})")
            
            # Compare unit types
            comparison = None
            if len(unit_types) >= 2:
                print("  - Comparing unit types...")
                comparison = analyzer.compare_unit_types(data.plot_data)
            
            # Create DataFrame
            df = create_analysis_dataframe(data.plot_data)
            
            # Generate markdown report
            print("  - Generating statistical report...")
            stats_path = PlotController._write_stats_report(
                lanchester_results, comparison, df
            )
            print(f"  Report: {stats_path}")
            
            # Generate visualizations
            print("  - Generating visualizations...")
            dashboard = AnalysisDashboard(output_dir=PlotController.DEFAULT_OUTPUT_DIR)
            plots = dashboard.generate_lanchester_dashboard(data.plot_data)
            for name, path in plots.items():
                if not str(path).startswith("Error"):
                    print(f"    {name}: {path}")
            
            return stats_path
            
        except ImportError as e:
            print(f"  Warning: Missing packages: {e}")
            return None
        except Exception as e:
            print(f"  Warning: Analysis failed: {e}")
            return None
    
    @staticmethod
    def _write_stats_report(lanchester_results: Dict, comparison: Optional[Dict], 
                            df) -> str:
        """Write statistical report to markdown file."""
        os.makedirs(PlotController.DEFAULT_OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(PlotController.DEFAULT_OUTPUT_DIR, f"stats_report_{timestamp}.md")
        
        with open(path, "w") as f:
            f.write("# Statistical Analysis Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Lanchester results
            f.write("## Lanchester Law Analysis\n\n")
            for unit_type, result in lanchester_results.items():
                f.write(f"### {unit_type}\n\n")
                f.write(f"- **Best Fit**: {result['best_fit']}\n")
                f.write(f"- **R² (Linear)**: {result['r2_linear']:.4f}\n")
                f.write(f"- **R² (Quadratic)**: {result['r2_quadratic']:.4f}\n")
                f.write(f"- **Conclusion**: {result['conclusion']}\n\n")
            
            # Comparisons
            if comparison and "pairwise_comparisons" in comparison:
                f.write("## Unit Type Comparisons\n\n")
                f.write("| Comparison | p-value | Effect Size | Significant |\n")
                f.write("|------------|---------|-------------|-------------|\n")
                for comp in comparison["pairwise_comparisons"]:
                    sig = "Yes" if comp["significant"] else "No"
                    f.write(f"| {comp['comparison']} | {comp['p_value']:.4f} | {comp['effect_size']:.3f} | {sig} |\n")
                f.write("\n")
            
            # Summary stats
            f.write("## Summary Statistics\n\n```\n")
            f.write(df.describe().to_string())
            f.write("\n```\n")
        
        return path
    
    @staticmethod
    def _print_summary(plot_path: str, report_path: str, stats_path: Optional[str]):
        """Print final summary."""
        print(f"\n{'=' * 60}")
        print("COMPLETE")
        print(f"{'=' * 60}")
        print(f"  Plot:   {plot_path}")
        print(f"  Report: {report_path}")
        if stats_path:
            print(f"  Stats:  {stats_path}")
        print(f"{'=' * 60}\n")
