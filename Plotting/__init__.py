# -*- coding: utf-8 -*-
"""
@package Plotting
@brief Plotting and Data Collection Module for Battle Simulations

@details
This module handles all plotting-related functionality:

- Data collection from simulations
- Base plotter interface
- Matplotlib-based plotters
- ggplot2-style plotters (via plotnine)
- Report generation

Architecture follows SOLID principles:
- Single Responsibility: Each class handles one type of plotting
- Open/Closed: Easy to add new plotters
- Liskov Substitution: All plotters implement BasePlotter interface
- Interface Segregation: Separate interfaces for different plot types
- Dependency Inversion: Plotters depend on PlotData abstraction

Usage:
    from Plotting import DataCollector, get_plotter, PlotReportGenerator
    
    # Collect simulation data
    collector = DataCollector(ai_name="DAFT", num_repetitions=10)
    data = collector.collect_lanchester(["Knight", "Crossbowman"], range(5, 50, 5))
    
    # Generate plot
    plotter = get_plotter("GGPlotLanchester", output_dir="Reports")
    plot_path = plotter.plot(data.plot_data)
    
    # Generate report
    report_gen = PlotReportGenerator(output_dir="Reports")
    report_path = report_gen.generate(data, plot_path)
"""

from Plotting.data import (
    BattleResult,
    AggregatedResults,
    PlotData,
    BattleDataCollector,
)

from Plotting.collector import (
    CollectedData,
    DataCollector,
    parse_types_arg,
    parse_range_arg,
)

from Plotting.base import (
    BasePlotter,
    PLOTTERS,
    get_plotter,
)

from Plotting.scenario_plotters import (
    ScenarioPlotter,
    PlotLanchester,
    PlotClassicMedieval,
    PlotCavalryCharge,
    PlotDefensiveSiege,
    PlotCannaeEnvelopment,
    PlotRomanLegion,
    PlotBritishSquare,
    SCENARIO_PLOTTERS,
    get_scenario_plotter,
)

from Plotting.report import PlotReportGenerator

__all__ = [
    # Data structures
    'BattleResult',
    'AggregatedResults',
    'PlotData',
    'BattleDataCollector',
    
    # Data collection
    'CollectedData',
    'DataCollector',
    'parse_types_arg',
    'parse_range_arg',
    
    # Base plotting
    'BasePlotter',
    'PLOTTERS',
    'get_plotter',
    
    # Scenario-specific plotters
    'ScenarioPlotter',
    'PlotLanchester',
    'PlotClassicMedieval',
    'PlotCavalryCharge',
    'PlotDefensiveSiege',
    'PlotCannaeEnvelopment',
    'PlotRomanLegion',
    'PlotBritishSquare',
    'SCENARIO_PLOTTERS',
    'get_scenario_plotter',
    
    # Reporting
    'PlotReportGenerator',
]
