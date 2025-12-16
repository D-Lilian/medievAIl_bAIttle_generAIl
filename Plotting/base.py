# -*- coding: utf-8 -*-
"""
@file base.py
@brief Base Plotters Module - Visualization tools for battle data

@details
Provides plotting functions for analyzing battle simulation results.
Uses matplotlib for graph generation. Follows Single Responsibility Principle
with each plotter handling a specific visualization type.

Part of the Plotting module - provides base classes and registry.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict
from datetime import datetime

# Lazy import for matplotlib to avoid issues if not installed
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

from Plotting.data import PlotData

class BasePlotter(ABC):
    """
    Abstract base class for all plotters.
    
    Defines the interface for creating visualizations from battle data.
    """
    
    def __init__(self, output_dir: str = "Reports"):
        """
        Initialize the plotter.
        
        @param output_dir: Directory to save generated plots
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is required for plotting. Install with: pip install matplotlib")
    
    @abstractmethod
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        """
        Generate plot from data.
        
        @param data: Dictionary mapping unit types to PlotData
        @param kwargs: Additional plotting options
        @return: Path to saved plot file
        """
        pass
    
    def _generate_filename(self, prefix: str, extension: str = "png") -> str:
        """Generate a unique filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"{prefix}_{timestamp}.{extension}")
    
    def _setup_style(self):
        """Setup matplotlib style for consistent appearance."""
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['legend.fontsize'] = 10


# =============================================================================
# GENERIC PLOTTERS (work with any scenario)
# =============================================================================

class PlotCasualties(BasePlotter):
    """
    Simple casualties plotter.
    
    Shows casualties for both teams across parameter values.
    """
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        """Generate casualties comparison plot."""
        self._setup_style()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        markers = ['o', 's', '^', 'D']
        
        for i, (label, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax.plot(
                    plot_data.n_values,
                    plot_data.avg_team_a_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=f'{label} - Team A',
                    linewidth=2
                )
                ax.plot(
                    plot_data.n_values,
                    plot_data.avg_team_b_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=f'{label} - Team B',
                    linewidth=2,
                    linestyle='--'
                )
        
        ax.set_xlabel('N')
        ax.set_ylabel('Average Casualties')
        ax.set_title('Casualties Analysis')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        filepath = self._generate_filename("casualties_analysis")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath


class PlotSurvivors(BasePlotter):
    """
    Survivors plotter.
    
    Shows surviving units for both teams.
    """
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        """Generate survivors comparison plot."""
        self._setup_style()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = ['#2ca02c', '#d62728', '#1f77b4', '#ff7f0e']
        
        for i, (label, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax.plot(
                    plot_data.n_values,
                    plot_data.avg_team_a_survivors,
                    color=colors[i % len(colors)],
                    label=f'{label} - Team A Survivors',
                    linewidth=2,
                    marker='o'
                )
                ax.plot(
                    plot_data.n_values,
                    plot_data.avg_team_b_survivors,
                    color=colors[i % len(colors)],
                    label=f'{label} - Team B Survivors',
                    linewidth=2,
                    linestyle='--',
                    marker='s'
                )
        
        ax.set_xlabel('N')
        ax.set_ylabel('Average Survivors')
        ax.set_title('Survivors Analysis')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        filepath = self._generate_filename("survivors_analysis")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath


class PlotWinRate(BasePlotter):
    """
    Win rate plotter.
    
    Shows win rates for each team across different scenarios.
    """
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        """Generate win rate plot."""
        self._setup_style()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        for i, (label, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax.plot(
                    plot_data.n_values,
                    [r * 100 for r in plot_data.team_a_win_rates],
                    color=colors[i % len(colors)],
                    label=f'{label} - Team A Win Rate',
                    linewidth=2,
                    marker='o'
                )
                ax.plot(
                    plot_data.n_values,
                    [r * 100 for r in plot_data.team_b_win_rates],
                    color=colors[i % len(colors)],
                    label=f'{label} - Team B Win Rate',
                    linewidth=2,
                    linestyle='--',
                    marker='s'
                )
        
        ax.set_xlabel('N')
        ax.set_ylabel('Win Rate (%)')
        ax.set_title('Win Rate Analysis')
        ax.axhline(y=50, color='gray', linestyle=':', alpha=0.7, label='50% baseline')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 105)
        
        plt.tight_layout()
        
        filepath = self._generate_filename("winrate_analysis")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath


# Registry of available plotters
PLOTTERS = {
    # Generic plotters
    'PlotCasualties': PlotCasualties,
    'PlotSurvivors': PlotSurvivors,
    'PlotWinRate': PlotWinRate,
}

# Add scenario-specific plotters
try:
    from Plotting.scenario_plotters import SCENARIO_PLOTTERS
    PLOTTERS.update(SCENARIO_PLOTTERS)
except ImportError:
    pass

# Try to add ggplot-style plotters if plotnine is available
try:
    from Plotting.ggplot_plotters import (
        GGPLOTTERS,
        GGPlotLanchester,
        GGPlotCasualties, 
        GGPlotSurvivors,
        GGPlotWinRate,
        GGPlotLanchesterComparison,
    )
    PLOTTERS.update(GGPLOTTERS)
    GGPLOT_AVAILABLE = True
except ImportError:
    GGPLOT_AVAILABLE = False

# Try to add advanced plotters for data analysis
try:
    from Analysis.visualizers import ADVANCED_PLOTTERS
    PLOTTERS.update(ADVANCED_PLOTTERS)
    ADVANCED_PLOTTERS_AVAILABLE = True
except ImportError:
    ADVANCED_PLOTTERS_AVAILABLE = False


def get_plotter(name: str, output_dir: str = "Reports") -> BasePlotter:
    """
    Factory function to get a plotter by name.
    
    Supports both matplotlib-based plotters and ggplot2-style plotters.
    
    @param name: Name of the plotter
    @param output_dir: Output directory for plots
    @return: Plotter instance
    @raises ValueError: If plotter name is unknown
    """
    if name not in PLOTTERS:
        available = list(PLOTTERS.keys())
        raise ValueError(f"Unknown plotter: {name}. Available: {available}")
    
    return PLOTTERS[name](output_dir)
