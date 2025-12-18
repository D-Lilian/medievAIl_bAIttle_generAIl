# -*- coding: utf-8 -*-
"""
@package Plotting
@brief Data Science Plotting and Visualization Module

@details
Professional data science plotting module using:
- pandas DataFrames for data storage
- plotnine (ggplot2-style) for visualization
- Lanchester's Laws analysis for battle simulation
- Unit comparison and damage analysis
"""

from .data import (
    LanchesterData,
    create_empty_dataframe,
    BATTLE_COLUMNS,
    BattleResult,
    AggregatedResults,
    PlotData,
    TeamStats,
    BattleDataCollector,
)

from .collector import (
    DataCollector,
    parse_types_arg,
    parse_range_arg,
)

from .base import (
    BasePlotter,
    PLOTTERS,
    get_plotter,
    list_plotters,
    theme_battle,
    PALETTE_UNITS,
    PALETTE_TEAMS,
    PALETTE_RESULTS,
    PALETTE_COMBAT,
    UNIT_TYPES,
    # Lanchester analysis
    PlotLanchester,
    # Generic analysis
    PlotWinRate,
    PlotCasualties,
    PlotDuration,
    PlotComparison,
    PlotHeatmap,
    PlotRawData,
    # Scenario analysis
    PlotScenarioOverview,
    PlotTeamPerformance,
    PlotCasualtiesDistribution,
    PlotBattleTimeline,
    PlotWinnerAnalysis,
    # Unit analysis
    PlotUnitComparison,
    PlotDamageMatrix,
    PlotKillEfficiency,
)

from .report import PlotReportGenerator

__all__ = [
    # Data containers
    'LanchesterData',
    'create_empty_dataframe',
    'BATTLE_COLUMNS',
    'BattleResult',
    'AggregatedResults',
    'PlotData',
    'TeamStats',
    'BattleDataCollector',
    # Data collection
    'DataCollector',
    'parse_types_arg',
    'parse_range_arg',
    # Plotting infrastructure
    'BasePlotter',
    'PLOTTERS',
    'get_plotter',
    'list_plotters',
    'theme_battle',
    'PALETTE_UNITS',
    'PALETTE_TEAMS',
    'PALETTE_RESULTS',
    'PALETTE_COMBAT',
    'UNIT_TYPES',
    # Lanchester
    'PlotLanchester',
    # Generic
    'PlotWinRate',
    'PlotCasualties',
    'PlotDuration',
    'PlotComparison',
    'PlotHeatmap',
    'PlotRawData',
    # Scenario
    'PlotScenarioOverview',
    'PlotTeamPerformance',
    'PlotCasualtiesDistribution',
    'PlotBattleTimeline',
    'PlotWinnerAnalysis',
    # Unit analysis
    'PlotUnitComparison',
    'PlotDamageMatrix',
    'PlotKillEfficiency',
    # Reporting
    'PlotReportGenerator',
]