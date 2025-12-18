# -*- coding: utf-8 -*-
"""
@package Tournament
@brief Tournament System for Automated AI Battles

@details
This module provides a complete tournament system for running automated
battles between AI generals across multiple scenarios.

Architecture follows SOLID principles:
- Single Responsibility: Config, Runner, Results, Report are separate classes
- Open/Closed: Easy to add new generals or scenarios
- Liskov Substitution: All generals implement same interface
- Interface Segregation: Separate interfaces for running vs reporting
- Dependency Inversion: High-level modules depend on abstractions

Features:
- Automatic position alternation for fairness
- Reflexive matchups (X vs X) to detect position bugs
- Score matrices: overall, general vs general, per scenario
- HTML report generation with detailed statistics

Usage:
    from Tournament import TournamentConfig, TournamentRunner, TournamentReportGenerator
    
    # Configure tournament
    config = TournamentConfig(
        generals=["DAFT", "BRAINDEAD", "SOMEIQ"],
        scenarios=["classic", "cavalry_charge"],
        rounds_per_matchup=10,
        alternate_positions=True
    )
    
    # Run tournament
    runner = TournamentRunner(config)
    results = runner.run()
    
    # Generate report
    report_gen = TournamentReportGenerator()
    report_path = report_gen.generate(results)
"""

from Tournament.config import TournamentConfig
from Tournament.results import MatchResult, TournamentResults
from Tournament.runner import TournamentRunner
from Tournament.report import TournamentReportGenerator

__all__ = [
    'TournamentConfig',
    'MatchResult',
    'TournamentResults',
    'TournamentRunner',
    'TournamentReportGenerator',
]
