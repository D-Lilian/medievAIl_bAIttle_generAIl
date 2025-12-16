# -*- coding: utf-8 -*-
"""
@file plotters.py
@brief Plotters Module - Visualization tools for battle data

@details
Provides plotting functions for analyzing battle simulation results.
Uses matplotlib for graph generation. Follows Single Responsibility Principle
with each plotter handling a specific visualization type.

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

from Utils.battle_data import PlotData


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


class PlotLanchester(BasePlotter):
    """
    Plotter for Lanchester's Laws analysis.
    
    Creates graphs showing how casualties correlate with N for different unit types.
    According to Lanchester's Laws:
    - Linear Law (melee): Casualties scale linearly with N
    - Square Law (ranged): Casualties scale with N²
    """
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        """
        Generate Lanchester analysis plot.
        
        Shows winner casualties vs N for each unit type on the same graph,
        allowing comparison between melee (Linear Law) and ranged (Square Law) units.
        
        @param data: Dictionary mapping unit type names to PlotData
        @return: Path to saved plot file
        """
        self._setup_style()
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Lanchester's Laws Analysis", fontsize=16, fontweight='bold')
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        markers = ['o', 's', '^', 'D', 'v']
        
        # Plot 1: Winner Casualties vs N
        ax1 = axes[0, 0]
        for i, (unit_type, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.avg_winner_casualties:
                ax1.plot(
                    plot_data.n_values, 
                    plot_data.avg_winner_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=unit_type,
                    linewidth=2,
                    markersize=6
                )
        ax1.set_xlabel('N (Team A units)')
        ax1.set_ylabel('Average Winner Casualties')
        ax1.set_title('Winner Casualties vs N')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Team B Win Rate (larger army should win)
        ax2 = axes[0, 1]
        for i, (unit_type, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.team_b_win_rates:
                ax2.plot(
                    plot_data.n_values,
                    [r * 100 for r in plot_data.team_b_win_rates],
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=unit_type,
                    linewidth=2,
                    markersize=6
                )
        ax2.set_xlabel('N (Team A units)')
        ax2.set_ylabel('Team B Win Rate (%)')
        ax2.set_title('Win Rate of Larger Army (2N) vs N')
        ax2.axhline(y=100, color='gray', linestyle='--', alpha=0.5, label='Expected 100%')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 105)
        
        # Plot 3: Battle Duration
        ax3 = axes[1, 0]
        for i, (unit_type, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.avg_ticks:
                ax3.plot(
                    plot_data.n_values,
                    plot_data.avg_ticks,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=unit_type,
                    linewidth=2,
                    markersize=6
                )
        ax3.set_xlabel('N (Team A units)')
        ax3.set_ylabel('Average Battle Duration (ticks)')
        ax3.set_title('Battle Duration vs N')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Casualties Comparison (Team A vs Team B)
        ax4 = axes[1, 1]
        for i, (unit_type, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                # Team A casualties (the smaller army)
                ax4.plot(
                    plot_data.n_values,
                    plot_data.avg_team_a_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=f'{unit_type} (N)',
                    linewidth=2,
                    markersize=6,
                    linestyle='-'
                )
                # Team B casualties (the larger army)
                ax4.plot(
                    plot_data.n_values,
                    plot_data.avg_team_b_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=f'{unit_type} (2N)',
                    linewidth=2,
                    markersize=6,
                    linestyle='--'
                )
        ax4.set_xlabel('N (Team A units)')
        ax4.set_ylabel('Average Casualties')
        ax4.set_title('Casualties by Team Size')
        ax4.legend(ncol=2, fontsize=8)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        filepath = self._generate_filename("lanchester_analysis")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath


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
    'PlotLanchester': PlotLanchester,
    'PlotCasualties': PlotCasualties,
    'PlotSurvivors': PlotSurvivors,
    'PlotWinRate': PlotWinRate,
}

# Try to add ggplot-style plotters if plotnine is available
try:
    from Utils.ggplotters import (
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
    from Utils.advanced_plotters import ADVANCED_PLOTTERS
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
