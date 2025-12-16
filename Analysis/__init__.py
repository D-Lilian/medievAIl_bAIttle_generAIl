# -*- coding: utf-8 -*-
"""
@package Analysis
@brief Statistical Analysis and Advanced Visualization Module

@details
This module provides comprehensive statistical analysis tools for battle simulations:

- Statistical tests (t-tests, ANOVA, chi-square, Mann-Whitney U)
- Effect size calculations (Cohen's d, eta-squared)
- Lanchester's Laws fitting and validation
- Advanced visualizations (heatmaps, boxplots, correlation matrices)

Architecture follows SOLID principles:
- Single Responsibility: Each class handles one type of analysis
- Open/Closed: Easy to extend with new statistical tests
- Liskov Substitution: All analyzers share common interface
- Interface Segregation: Separate interfaces for stats vs visualization
- Dependency Inversion: High-level modules depend on abstractions

Usage:
    from Analysis import StatisticalAnalyzer, LanchesterAnalyzer, AnalysisDashboard
    
    # Run statistical tests
    analyzer = StatisticalAnalyzer()
    result = analyzer.independent_t_test(group_a, group_b)
    
    # Analyze Lanchester laws
    lanchester = LanchesterAnalyzer()
    results = lanchester.test_lanchester_law(plot_data)
    
    # Generate dashboard
    dashboard = AnalysisDashboard(output_dir="Reports")
    plots = dashboard.generate_lanchester_dashboard(plot_data)
"""

from Analysis.statistical import (
    DescriptiveStats,
    HypothesisTestResult,
    StatisticalAnalyzer,
    LanchesterAnalyzer,
    create_analysis_dataframe,
)

from Analysis.visualizers import (
    HeatmapPlotter,
    DistributionPlotter,
    StatisticalPlotter,
    AnalysisDashboard,
    VISUALIZERS,
)

__all__ = [
    # Statistical Analysis
    'DescriptiveStats',
    'HypothesisTestResult',
    'StatisticalAnalyzer',
    'LanchesterAnalyzer',
    'create_analysis_dataframe',
    
    # Visualization
    'HeatmapPlotter',
    'DistributionPlotter',
    'StatisticalPlotter',
    'AnalysisDashboard',
    'VISUALIZERS',
]
