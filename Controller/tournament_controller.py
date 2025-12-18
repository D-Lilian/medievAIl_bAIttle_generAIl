# -*- coding: utf-8 -*-
"""
@file tournament_controller.py
@brief Tournament Controller - Manages tournament execution

@details
Handles tournament configuration, execution and report generation.
Follows Single Responsibility Principle - only orchestrates tournament flow.
"""

from typing import List, Optional

from Tournament import TournamentConfig, TournamentRunner, TournamentReportGenerator


class TournamentController:
    """
    Controller for tournament execution.

    Simplifies the tournament workflow by handling:
    - Configuration parsing from CLI args
    - Tournament execution
    - Report generation
    - Results display
    """

    # Default values
    DEFAULT_ROUNDS = 10

    @staticmethod
    def run_tournament(args) -> Optional[str]:
        """
        Run a tournament from CLI arguments.

        @param args: CLI arguments with ais, scenarios, N, no_alternate
        @return: Path to generated report, or None on error
        """
        # Parse configuration
        generals = getattr(args, "ais", None) or TournamentRunner.AVAILABLE_GENERALS
        scenarios = getattr(args, "scenarios", None) or list(
            TournamentRunner.SCENARIO_MAP.keys()
        )
        rounds = getattr(args, "N", TournamentController.DEFAULT_ROUNDS)
        alternate = not getattr(args, "no_alternate", False)

        # Calculate total matches
        num_matchups = len(generals) * len(generals) * len(scenarios)
        total_matches = num_matchups * rounds * (2 if alternate else 1)

        # Display compact config (Lanchester style)
        print(f"\nTournament: {', '.join(generals)} | {', '.join(scenarios)} | {rounds}x = {total_matches} matches")

        # Create config
        config = TournamentConfig(
            generals=generals,
            scenarios=scenarios,
            rounds_per_matchup=rounds,
            alternate_positions=alternate,
        )

        # Run tournament
        runner = TournamentRunner(config)
        results = runner.run()

        # Generate report
        report_gen = TournamentReportGenerator()
        report_path = report_gen.generate(results)

        # Print compact summary
        TournamentController._print_compact_standings(results, generals, report_path)

        # Auto-open report in browser
        if report_path:
            import webbrowser
            import os
            webbrowser.open(f"file://{os.path.abspath(report_path)}")

        return report_path

    @staticmethod
    def _print_compact_standings(results, generals: List[str], report_path: str):
        """Print compact tournament standings (Lanchester style)."""
        overall = results.get_overall_scores()

        sorted_generals = sorted(
            generals, key=lambda g: overall.get(g, {}).get("win_rate", 0), reverse=True
        )

        # Build compact ranking line
        rankings = []
        for rank, general in enumerate(sorted_generals, 1):
            data = overall.get(general, {"win_rate": 0, "wins": 0, "total": 0})
            rankings.append(f"{rank}. {general} {data['win_rate']:.0f}%")
        
        print(f"\nDone. {' | '.join(rankings)}")
        print(f"✓ Report: {report_path}")
