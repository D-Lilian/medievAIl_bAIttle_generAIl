# -*- coding: utf-8 -*-
"""
@package Utils
@brief Utility modules for the battle simulation.

Includes:
- errors: Custom exceptions
- logs: Logging configuration
- map_generator: Map generation utilities
- parse_cli: Command line argument parsing
- predefined_scenarios: Scenario definitions
- save_load: Save/load functionality
- statistical: Statistical analysis tools (import from Utils.statistical)
"""

# Note: statistical module has dependencies on Plotting, so it's not
# imported here to avoid circular imports. Use:
#   from Utils.statistical import StatisticalAnalyzer, LanchesterAnalyzer

__all__ = [
    'DescriptiveStats',
    'HypothesisTestResult',
    'StatisticalAnalyzer',
    'LanchesterAnalyzer',
    'create_analysis_dataframe',
]


def __getattr__(name):
    """Lazy import to avoid circular dependencies."""
    if name in __all__:
        from Utils import statistical
        return getattr(statistical, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
