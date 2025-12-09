#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file run_lanchester.py
@brief CLI for running Lanchester's Laws experiments

@details
Command line interface for running Lanchester scenarios and generating
visualizations. Supports multiple output formats and experiment configurations.

@usage
    # Run experiment with Knights and Crossbowmen, N from 5 to 50
    python run_lanchester.py --types Knight Crossbowman --n-range 5 50 --step 5
    
    # Generate interactive HTML plot
    python run_lanchester.py --types Knight Crossbowman --n-range 5 30 --output html
    
    # Generate markdown report
    python run_lanchester.py --types Knight --n-range 10 100 --step 10 --report

"""
import argparse
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model.scenarios.lanchester_scenario import LanchesterScenario, LanchesterExperiment
from Analysis.lanchester_plotter import LanchesterPlotter


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Run Lanchester's Laws experiments and generate visualizations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Quick test with small N
    python run_lanchester.py --types Knight --n-range 5 20 --step 5
    
    # Compare melee vs ranged
    python run_lanchester.py --types Knight Crossbowman --n-range 5 50 --step 5
    
    # Full experiment with report
    python run_lanchester.py --types Knight Crossbowman Pikeman --n-range 5 100 --step 5 --reps 3 --report
        """
    )
    
    parser.add_argument(
        '--types', '-t',
        nargs='+',
        default=['Knight', 'Crossbowman'],
        help='Unit types to test (default: Knight Crossbowman)'
    )
    
    parser.add_argument(
        '--n-range', '-n',
        nargs=2,
        type=int,
        default=[5, 30],
        metavar=('MIN', 'MAX'),
        help='Range of N values (default: 5 30)'
    )
    
    parser.add_argument(
        '--step', '-s',
        type=int,
        default=5,
        help='Step size for N (default: 5)'
    )
    
    parser.add_argument(
        '--reps', '-r',
        type=int,
        default=1,
        help='Number of repetitions per configuration (default: 1)'
    )
    
    parser.add_argument(
        '--output', '-o',
        choices=['png', 'html', 'both', 'none'],
        default='png',
        help='Output format for plots (default: png)'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate markdown report'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='Reports/Lanchester',
        help='Output directory (default: Reports/Lanchester)'
    )
    
    parser.add_argument(
        '--tick-speed',
        type=int,
        default=100,
        help='Simulation tick speed (default: 100)'
    )
    
    parser.add_argument(
        '--save-data',
        action='store_true',
        help='Save raw results to JSON'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress output'
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build N range
    n_range = range(args.n_range[0], args.n_range[1] + 1, args.step)
    
    if not args.quiet:
        print("=" * 60)
        print("Lanchester's Laws Experiment")
        print("=" * 60)
        print(f"Unit types: {args.types}")
        print(f"N range: {args.n_range[0]} to {args.n_range[1]} (step {args.step})")
        print(f"Repetitions: {args.reps}")
        print(f"Total simulations: {len(args.types) * len(list(n_range)) * args.reps}")
        print("-" * 60)
    
    # Run experiment
    experiment = LanchesterExperiment()
    
    if args.quiet:
        # Suppress print in LanchesterExperiment
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            results = experiment.run(
                unit_types=args.types,
                n_range=n_range,
                repetitions=args.reps,
                tick_speed=args.tick_speed
            )
    else:
        results = experiment.run(
            unit_types=args.types,
            n_range=n_range,
            repetitions=args.reps,
            tick_speed=args.tick_speed
        )
    
    if not args.quiet:
        print("-" * 60)
        print(f"Completed {len(results)} simulations")
    
    # Create plotter
    plotter = LanchesterPlotter(output_dir=str(output_dir))
    plotter.load_results(results)
    
    # Save raw data if requested
    if args.save_data:
        json_path = plotter.save_results_json("lanchester_results.json")
        if not args.quiet:
            print(f"Saved results to: {json_path}")
    
    # Generate plots
    if args.output in ['png', 'both']:
        try:
            png_path = plotter.save("lanchester_plot.png")
            if not args.quiet:
                print(f"Saved PNG plot to: {png_path}")
        except ImportError as e:
            print(f"Warning: Could not generate PNG plot: {e}")
    
    if args.output in ['html', 'both']:
        try:
            html_path = plotter.save("lanchester_plot.html")
            if not args.quiet:
                print(f"Saved HTML plot to: {html_path}")
        except ImportError as e:
            print(f"Warning: Could not generate HTML plot: {e}")
    
    # Generate report if requested
    if args.report:
        try:
            report_path = plotter.to_markdown("lanchester_report.md")
            if not args.quiet:
                print(f"Saved report to: {report_path}")
        except Exception as e:
            print(f"Warning: Could not generate report: {e}")
    
    if not args.quiet:
        print("=" * 60)
        print("Experiment complete!")
    
    return results


if __name__ == "__main__":
    main()
