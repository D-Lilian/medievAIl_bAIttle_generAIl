# -*- coding: utf-8 -*-
"""
@package Plotting
@brief Unified Plotting and Visualization Module with pandas DataFrames

@details
Professional data science plotting module using:
- pandas DataFrames for data storage
- plotnine (ggplot2-style) for visualization
- Lanchester's Laws analysis for battle simulation

"""

from .data import (
    # Core DataFrame container
    LanchesterData,
    create_empty_dataframe,
    BATTLE_COLUMNS,
    # Legacy classes (backward compatibility)
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
    # Generic plot types
    PlotWinRate,
    PlotCasualties,
    PlotDuration,
    PlotComparison,
    PlotHeatmap,
    PlotRawData,
    # General scenario plotters
    PlotScenarioOverview,
    PlotTeamPerformance,
    PlotCasualtiesDistribution,
    PlotBattleTimeline,
    PlotWinnerAnalysis,
)

from .report import PlotReportGenerator

__all__ = [
    # Core DataFrame container
    'LanchesterData',
    'create_empty_dataframe',
    'BATTLE_COLUMNS',
    # Legacy data structures
    'BattleResult',
    'AggregatedResults',
    'PlotData',
    'TeamStats',
    'BattleDataCollector',
    
    # Data collection
    'DataCollector',
    'parse_types_arg',
    'parse_range_arg',
    
    # Base plotting
    'BasePlotter',
    'PLOTTERS',
    'get_plotter',
    'list_plotters',
    'theme_battle',
    'PALETTE_UNITS',
    'PALETTE_TEAMS',
    'PALETTE_RESULTS',
    
    # Lanchester-specific plots
    'PlotLanchester',
    'PlotLanchesterCasualties',
    
    # Generic plot types
    'PlotWinRate',
    'PlotCasualties',
    'PlotDuration',
    'PlotComparison',
    'PlotHeatmap',
    'PlotRawData',
    
    # General scenario plotters
    'PlotScenarioOverview',
    'PlotTeamPerformance',
    'PlotCasualtiesDistribution',
    'PlotBattleTimeline',
    'PlotWinnerAnalysis',
    
    # Reporting
    'PlotReportGenerator',
]