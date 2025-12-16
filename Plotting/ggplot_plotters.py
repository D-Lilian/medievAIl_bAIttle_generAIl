# -*- coding: utf-8 -*-
"""
@file ggplot_plotters.py
@brief ggplot2-style Plotters using plotnine

@details
Provides beautiful, publication-quality visualizations using plotnine,
the Python implementation of R's ggplot2. Follows the Grammar of Graphics
for declarative, layered plot construction.

Part of the Plotting module.
"""

import os
import warnings
from abc import ABC, abstractmethod
from typing import Dict, List
from datetime import datetime

import pandas as pd
import numpy as np

# Import plotnine (ggplot2 for Python)
try:
    from plotnine import (
        ggplot, aes, 
        geom_line, geom_point, geom_ribbon, geom_smooth, geom_bar,
        geom_text, geom_hline, geom_vline, geom_area,
        facet_wrap, facet_grid,
        labs, theme, theme_minimal, theme_bw, theme_classic,
        element_text, element_blank, element_rect, element_line,
        scale_color_brewer, scale_fill_brewer, scale_color_manual, scale_fill_manual,
        scale_x_continuous, scale_y_continuous,
        position_dodge, coord_flip,
        ggsave
    )
    PLOTNINE_AVAILABLE = True
except ImportError:
    PLOTNINE_AVAILABLE = False

from Plotting.data import PlotData


# Custom theme inspired by ggplot2's theme_minimal with enhancements
def theme_medieval():
    """Custom theme for medieval battle analysis."""
    return (
        theme_minimal() +
        theme(
            plot_title=element_text(size=16, face='bold', ha='center'),
            plot_subtitle=element_text(size=12, color='#666666', ha='center'),
            axis_title=element_text(size=11, face='bold'),
            axis_text=element_text(size=10),
            legend_title=element_text(size=11, face='bold'),
            legend_text=element_text(size=10),
            legend_position='right',
            panel_grid_major=element_line(color='#E0E0E0', size=0.5),
            panel_grid_minor=element_blank(),
            strip_text=element_text(size=11, face='bold'),
            figure_size=(12, 8),
            dpi=150
        )
    )


# Color palettes
PALETTE_UNITS = {
    'Knight': '#E74C3C',       # Red - aggressive melee
    'Crossbowman': '#3498DB',  # Blue - tactical ranged
    'Pikeman': '#27AE60',      # Green - defensive
    'Melee': '#E74C3C',
    'Ranged': '#3498DB',
}

PALETTE_TEAMS = {
    'Team A (N)': '#1ABC9C',   # Teal
    'Team B (2N)': '#9B59B6',  # Purple
}


class BaseGGPlotter(ABC):
    """
    Abstract base class for ggplot2-style plotters.
    """
    
    def __init__(self, output_dir: str = "Reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        if not PLOTNINE_AVAILABLE:
            raise ImportError(
                "plotnine is required for ggplot2-style plotting. "
                "Install with: pip install plotnine"
            )
    
    @abstractmethod
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        """Generate plot from data."""
        pass
    
    def _generate_filename(self, prefix: str, extension: str = "png") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"{prefix}_{timestamp}.{extension}")
    
    def _prepare_dataframe(self, data: Dict[str, PlotData]) -> pd.DataFrame:
        """Convert PlotData dict to a tidy DataFrame for ggplot."""
        rows = []
        for unit_type, plot_data in data.items():
            for i, n in enumerate(plot_data.n_values):
                if i >= len(plot_data.avg_team_a_casualties):
                    continue
                rows.append({
                    'unit_type': unit_type,
                    'n': n,
                    'team_a_casualties': plot_data.avg_team_a_casualties[i],
                    'team_b_casualties': plot_data.avg_team_b_casualties[i],
                    'team_a_survivors': plot_data.avg_team_a_survivors[i] if i < len(plot_data.avg_team_a_survivors) else 0,
                    'team_b_survivors': plot_data.avg_team_b_survivors[i] if i < len(plot_data.avg_team_b_survivors) else 0,
                    'team_a_win_rate': plot_data.team_a_win_rates[i] * 100 if i < len(plot_data.team_a_win_rates) else 0,
                    'team_b_win_rate': plot_data.team_b_win_rates[i] * 100 if i < len(plot_data.team_b_win_rates) else 0,
                    'avg_ticks': plot_data.avg_ticks[i] if i < len(plot_data.avg_ticks) else 0,
                    'winner_casualties': plot_data.avg_winner_casualties[i] if i < len(plot_data.avg_winner_casualties) else 0,
                })
        return pd.DataFrame(rows)


class GGPlotLanchester(BaseGGPlotter):
    """
    Beautiful Lanchester's Laws visualization using ggplot2 grammar.
    
    Creates a multi-panel figure showing:
    1. Winner casualties vs N (key insight for Lanchester's Laws)
    2. Win rate of larger army
    3. Battle duration
    4. Casualties comparison by team
    """
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        """Generate publication-quality Lanchester analysis."""
        
        # Suppress plotnine warnings
        warnings.filterwarnings('ignore', category=UserWarning)
        
        df = self._prepare_dataframe(data)
        
        if df.empty:
            raise ValueError("No data to plot")
        
        # Get unit types for color mapping
        unit_types = df['unit_type'].unique().tolist()
        colors = [PALETTE_UNITS.get(ut, '#666666') for ut in unit_types]
        
        # Create individual plots
        plots = []
        
        # Plot 1: Winner (2N) Casualties vs N - THE KEY LANCHESTER INSIGHT
        p1 = (
            ggplot(df, aes(x='n', y='team_b_casualties', color='unit_type')) +
            geom_line(size=1.2) +
            geom_point(size=3, alpha=0.8) +
            scale_color_manual(values=colors) +
            labs(
                title="Lanchester's Laws: Winner Casualties",
                subtitle="How many casualties does the larger army (2N) sustain?",
                x="N (smaller army size)",
                y="Average Casualties (2N side)",
                color="Unit Type"
            ) +
            theme_medieval()
        )
        plots.append(('winner_casualties', p1))
        
        # Plot 2: Win Rate of Larger Army
        p2 = (
            ggplot(df, aes(x='n', y='team_b_win_rate', color='unit_type')) +
            geom_line(size=1.2) +
            geom_point(size=3, alpha=0.8) +
            geom_hline(yintercept=100, linetype='dashed', color='gray', alpha=0.7) +
            scale_color_manual(values=colors) +
            scale_y_continuous(limits=(0, 105)) +
            labs(
                title="Larger Army Win Rate",
                subtitle="2N army should win 100% (gray line)",
                x="N (smaller army size)",
                y="Win Rate (%)",
                color="Unit Type"
            ) +
            theme_medieval()
        )
        plots.append(('win_rate', p2))
        
        # Plot 3: Battle Duration
        p3 = (
            ggplot(df, aes(x='n', y='avg_ticks', color='unit_type')) +
            geom_line(size=1.2) +
            geom_point(size=3, alpha=0.8) +
            scale_color_manual(values=colors) +
            labs(
                title="Battle Duration",
                subtitle="How long do battles last as army size increases?",
                x="N (smaller army size)",
                y="Average Duration (ticks)",
                color="Unit Type"
            ) +
            theme_medieval()
        )
        plots.append(('duration', p3))
        
        # Plot 4: Casualties Comparison - Long format for faceting
        df_long = pd.melt(
            df,
            id_vars=['unit_type', 'n'],
            value_vars=['team_a_casualties', 'team_b_casualties'],
            var_name='team',
            value_name='casualties'
        )
        df_long['team'] = df_long['team'].map({
            'team_a_casualties': 'Team A (N)',
            'team_b_casualties': 'Team B (2N)'
        })
        
        p4 = (
            ggplot(df_long, aes(x='n', y='casualties', color='team', linetype='unit_type')) +
            geom_line(size=1.0) +
            geom_point(size=2.5, alpha=0.7) +
            scale_color_manual(values=['#1ABC9C', '#9B59B6']) +
            labs(
                title="Casualties by Team",
                subtitle="Comparing N (smaller) vs 2N (larger) army losses",
                x="N (smaller army size)",
                y="Average Casualties",
                color="Team",
                linetype="Unit Type"
            ) +
            theme_medieval()
        )
        plots.append(('casualties_comparison', p4))
        
        # Save individual plots and create combined view
        saved_paths = []
        for name, plot in plots:
            path = self._generate_filename(f"lanchester_{name}")
            plot.save(path, width=10, height=7, dpi=150, verbose=False)
            saved_paths.append(path)
        
        # Create combined 2x2 panel plot
        combined_path = self._create_combined_plot(df, colors)
        
        return combined_path
    
    def _create_combined_plot(self, df: pd.DataFrame, colors: List[str]) -> str:
        """Create a combined faceted plot."""
        
        # Reshape data for faceting
        df_plot = df.copy()
        
        # Create metrics in long format
        metrics_data = []
        for _, row in df.iterrows():
            metrics_data.extend([
                {
                    'unit_type': row['unit_type'],
                    'n': row['n'],
                    'metric': 'Winner Casualties',
                    'value': row['team_b_casualties']
                },
                {
                    'unit_type': row['unit_type'],
                    'n': row['n'],
                    'metric': 'Win Rate (%)',
                    'value': row['team_b_win_rate']
                },
                {
                    'unit_type': row['unit_type'],
                    'n': row['n'],
                    'metric': 'Battle Duration',
                    'value': row['avg_ticks']
                },
                {
                    'unit_type': row['unit_type'],
                    'n': row['n'],
                    'metric': 'Loser Casualties',
                    'value': row['team_a_casualties']
                },
            ])
        
        df_metrics = pd.DataFrame(metrics_data)
        
        # Order facets logically
        df_metrics['metric'] = pd.Categorical(
            df_metrics['metric'],
            categories=['Winner Casualties', 'Loser Casualties', 'Win Rate (%)', 'Battle Duration'],
            ordered=True
        )
        
        p = (
            ggplot(df_metrics, aes(x='n', y='value', color='unit_type')) +
            geom_line(size=1.0) +
            geom_point(size=2.5, alpha=0.8) +
            facet_wrap('~metric', scales='free_y', ncol=2) +
            scale_color_manual(values=colors) +
            labs(
                title="Lanchester's Laws Analysis",
                subtitle="N units vs 2N units - Testing Linear (melee) vs Square (ranged) Laws",
                x="N (smaller army size)",
                y="Value",
                color="Unit Type"
            ) +
            theme_medieval() +
            theme(figure_size=(14, 10))
        )
        
        filepath = self._generate_filename("lanchester_analysis")
        p.save(filepath, width=14, height=10, dpi=150, verbose=False)
        
        return filepath


class GGPlotCasualties(BaseGGPlotter):
    """
    Elegant casualties visualization with confidence ribbons.
    """
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        df = self._prepare_dataframe(data)
        
        # Long format for team comparison
        df_long = pd.melt(
            df,
            id_vars=['unit_type', 'n'],
            value_vars=['team_a_casualties', 'team_b_casualties'],
            var_name='team',
            value_name='casualties'
        )
        df_long['team'] = df_long['team'].map({
            'team_a_casualties': 'Team A (N)',
            'team_b_casualties': 'Team B (2N)'
        })
        
        p = (
            ggplot(df_long, aes(x='n', y='casualties', color='team')) +
            geom_line(size=1.2) +
            geom_point(size=3) +
            facet_wrap('~unit_type', scales='free_y') +
            scale_color_manual(values=['#1ABC9C', '#9B59B6']) +
            labs(
                title="Casualties Analysis by Unit Type",
                subtitle="Comparing losses between smaller (N) and larger (2N) armies",
                x="N (smaller army size)",
                y="Average Casualties",
                color="Team"
            ) +
            theme_medieval()
        )
        
        filepath = self._generate_filename("gg_casualties")
        p.save(filepath, width=12, height=8, dpi=150, verbose=False)
        
        return filepath


class GGPlotSurvivors(BaseGGPlotter):
    """
    Survivors visualization with area ribbons.
    """
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        df = self._prepare_dataframe(data)
        
        # Add initial army sizes for context
        df['team_a_initial'] = df['n']
        df['team_b_initial'] = df['n'] * 2
        
        # Calculate survival rates
        df['team_a_survival_rate'] = (df['team_a_survivors'] / df['n']) * 100
        df['team_b_survival_rate'] = (df['team_b_survivors'] / (df['n'] * 2)) * 100
        
        # Long format
        df_long = pd.melt(
            df,
            id_vars=['unit_type', 'n'],
            value_vars=['team_a_survival_rate', 'team_b_survival_rate'],
            var_name='team',
            value_name='survival_rate'
        )
        df_long['team'] = df_long['team'].map({
            'team_a_survival_rate': 'Team A (N)',
            'team_b_survival_rate': 'Team B (2N)'
        })
        
        unit_types = df['unit_type'].unique().tolist()
        colors = [PALETTE_UNITS.get(ut, '#666666') for ut in unit_types]
        
        p = (
            ggplot(df_long, aes(x='n', y='survival_rate', fill='team', color='team')) +
            geom_area(alpha=0.3, position='identity') +
            geom_line(size=1) +
            facet_wrap('~unit_type') +
            scale_color_manual(values=['#1ABC9C', '#9B59B6']) +
            scale_fill_manual(values=['#1ABC9C', '#9B59B6']) +
            scale_y_continuous(limits=(0, 105)) +
            labs(
                title="Survival Rate Analysis",
                subtitle="Percentage of army surviving after battle",
                x="N (smaller army size)",
                y="Survival Rate (%)",
                color="Team",
                fill="Team"
            ) +
            theme_medieval()
        )
        
        filepath = self._generate_filename("gg_survivors")
        p.save(filepath, width=12, height=8, dpi=150, verbose=False)
        
        return filepath


class GGPlotWinRate(BaseGGPlotter):
    """
    Win rate visualization with reference lines.
    """
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        df = self._prepare_dataframe(data)
        
        unit_types = df['unit_type'].unique().tolist()
        colors = [PALETTE_UNITS.get(ut, '#666666') for ut in unit_types]
        
        p = (
            ggplot(df, aes(x='n', y='team_b_win_rate', color='unit_type', fill='unit_type')) +
            geom_ribbon(aes(ymin=95, ymax='team_b_win_rate'), alpha=0.2) +
            geom_line(size=1.5) +
            geom_point(size=4, alpha=0.9) +
            geom_hline(yintercept=100, linetype='dashed', color='#2C3E50', size=0.8) +
            geom_hline(yintercept=50, linetype='dotted', color='#7F8C8D', size=0.5) +
            scale_color_manual(values=colors) +
            scale_fill_manual(values=colors) +
            scale_y_continuous(limits=(0, 105), breaks=[0, 25, 50, 75, 100]) +
            labs(
                title="Win Rate of Larger Army (2N)",
                subtitle="Expected: 100% (dashed line) | Random: 50% (dotted line)",
                x="N (smaller army size)",
                y="Win Rate (%)",
                color="Unit Type",
                fill="Unit Type"
            ) +
            theme_medieval()
        )
        
        filepath = self._generate_filename("gg_winrate")
        p.save(filepath, width=12, height=7, dpi=150, verbose=False)
        
        return filepath


class GGPlotLanchesterComparison(BaseGGPlotter):
    """
    Direct comparison of Lanchester's Laws between unit types.
    
    Shows linear vs square law behavior in a single, clear visualization.
    """
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        df = self._prepare_dataframe(data)
        
        if df.empty:
            raise ValueError("No data to plot")
        
        # Calculate casualty ratio: winner casualties / loser casualties
        df['casualty_ratio'] = df['team_b_casualties'] / (df['team_a_casualties'] + 0.01)
        
        # Normalize casualties to percentage of initial army
        df['winner_casualty_pct'] = (df['team_b_casualties'] / (df['n'] * 2)) * 100
        df['loser_casualty_pct'] = (df['team_a_casualties'] / df['n']) * 100
        
        unit_types = df['unit_type'].unique().tolist()
        colors = [PALETTE_UNITS.get(ut, '#666666') for ut in unit_types]
        
        # Main insight: Winner casualty percentage vs N
        p = (
            ggplot(df, aes(x='n', y='winner_casualty_pct', color='unit_type')) +
            geom_line(size=1.5) +
            geom_point(size=4, alpha=0.9) +
            scale_color_manual(values=colors) +
            labs(
                title="Lanchester's Laws: Casualty Scaling",
                subtitle="Winner (2N) casualty rate as a percentage of initial army size",
                x="N (smaller army size)",
                y="Winner Casualties (% of 2N)",
                color="Unit Type",
                caption="Linear Law (melee): flat or linear growth | Square Law (ranged): slower growth"
            ) +
            theme_medieval() +
            theme(
                plot_caption=element_text(size=9, color='#666666', ha='right')
            )
        )
        
        filepath = self._generate_filename("gg_lanchester_comparison")
        p.save(filepath, width=12, height=8, dpi=150, verbose=False)
        
        return filepath


# Registry of ggplot-style plotters
GGPLOTTERS = {
    'GGPlotLanchester': GGPlotLanchester,
    'GGPlotCasualties': GGPlotCasualties,
    'GGPlotSurvivors': GGPlotSurvivors,
    'GGPlotWinRate': GGPlotWinRate,
    'GGPlotLanchesterComparison': GGPlotLanchesterComparison,
}


def get_ggplotter(name: str, output_dir: str = "Reports") -> BaseGGPlotter:
    """
    Factory function to get a ggplot-style plotter by name.
    
    @param name: Name of the plotter
    @param output_dir: Output directory for plots
    @return: Plotter instance
    """
    if name not in GGPLOTTERS:
        available = list(GGPLOTTERS.keys())
        raise ValueError(f"Unknown ggplotter: {name}. Available: {available}")
    
    return GGPLOTTERS[name](output_dir)
