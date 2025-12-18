# -*- coding: utf-8 -*-
"""
@file       base.py
@brief      Plotnine-based plotting system for battle analysis.

@details    Uses plotnine (ggplot2 grammar of graphics) with pandas DataFrames.
            All plotters accept LanchesterData objects and produce publication-quality plots.

@see LanchesterData for input data structure.
@see PLOTTERS for available plotter registry.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import warnings

import pandas as pd

from plotnine import (
    ggplot, aes, 
    geom_line, geom_point, geom_bar,
    geom_boxplot, geom_tile, geom_text,
    geom_smooth,
    labs, theme_minimal, theme, element_text, element_blank,
    element_line, element_rect, facet_wrap,
    scale_fill_manual, scale_color_manual, scale_fill_gradient2,
    ggsave,
)


## @defgroup PlotConfig Theme and Palette Configuration
## @{

## @var UNIT_TYPES
#  @brief Unit type classification (melee vs ranged).
UNIT_TYPES = {
    'Knight': 'Melee',
    'Pikeman': 'Melee',
    'Infantry': 'Melee',
    'Cavalry': 'Melee',
    'Crossbowman': 'Ranged',
    'Crossbow': 'Ranged',
    'Archer': 'Ranged',
}

## @var PALETTE_COMBAT
#  @brief Color palette for combat types.
PALETTE_COMBAT = {
    'Melee': '#c44e52',   # Red for melee
    'Ranged': '#4c72b0',  # Blue for ranged
}

## @var DAMAGE_MATRIX
#  @brief Theoretical damage dealt by attacker (row) to target (column).
#  @details Based on unit stats from Model/units.py
#           Knight: 10 Base Melee, -3 vs Cavalry
#           Pikeman: 4 Base Melee, +22 vs Cavalry  
#           Crossbowman: 5 Base Pierce, +3 vs Spearmen
DAMAGE_MATRIX = {
    'Knight': {'Knight': 7, 'Pikeman': 10, 'Crossbowman': 10},
    'Pikeman': {'Knight': 26, 'Pikeman': 4, 'Crossbowman': 4},
    'Crossbowman': {'Knight': 5, 'Pikeman': 8, 'Crossbowman': 5},
}

## @var HP_VALUES
#  @brief HP values for each unit type.
HP_VALUES = {
    'Knight': 100,
    'Pikeman': 55,
    'Crossbowman': 35,
}

## @var PALETTE_UNITS
#  @brief Color palette for unit types.
PALETTE_UNITS = {
    'Knight': '#c44e52',      # Red for melee
    'Crossbowman': '#4c72b0', # Blue for ranged
    'Crossbow': '#4c72b0',
    'Pikeman': '#55a868',     # Green for polearm
    'Archer': '#dd8452',      # Orange
    'Cavalry': '#8172b3',     # Purple
    'default': '#666666'
}

## @var PALETTE_TEAMS
#  @brief Color palette for team designations.
PALETTE_TEAMS = {
    'Team A': '#e74c3c',
    'Team B': '#3498db',
    'Team A (N)': '#e74c3c',   # Lanchester specific
    'Team B (2N)': '#3498db',  # Lanchester specific
    'A': '#e74c3c',
    'B': '#3498db'
}

## @var PALETTE_RESULTS
#  @brief Color palette for battle outcomes.
PALETTE_RESULTS = {
    'wins': '#2ecc71', 
    'losses': '#e74c3c', 
    'draws': '#95a5a6'
}


def theme_battle() -> theme:
    """@brief Custom plotnine theme for battle simulation plots."""
    return theme_minimal() + theme(
        plot_title=element_text(size=14, weight='bold', color='#2c3e50'),
        plot_subtitle=element_text(size=11, color='#7f8c8d'),
        axis_title=element_text(size=11, weight='bold'),
        axis_text=element_text(size=10),
        legend_title=element_text(size=10, weight='bold'),
        legend_text=element_text(size=9),
        legend_position='right',
        legend_background=element_rect(fill='white', alpha=0.8),
        panel_grid_minor=element_blank(),
        panel_grid_major=element_line(color='#ecf0f1', size=0.5),
        strip_text=element_text(size=11, weight='bold'),
        figure_size=(12, 8),
        plot_background=element_rect(fill='white'),
    )

## @}

## @class BasePlotter
#  @brief Abstract base class for all plotters.

class BasePlotter(ABC):
    """@brief Abstract base class for all plotters."""
    
    def __init__(self, output_dir: str = "Reports"):
        self.output_dir = Path(output_dir)
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise RuntimeError(f"Cannot create output directory '{output_dir}': {e}")
    
    @abstractmethod
    def plot(self, data: Any, **kwargs) -> Path:
        """@brief Generate and save a plot. Must be implemented by subclasses."""
        pass
    
    def _generate_filename(self, prefix: str, suffix: str = "png") -> Path:
        """@brief Generate unique filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"{prefix}_{timestamp}.{suffix}"
    
    def _save_plot(self, plot: ggplot, filename: Path, 
                   width: float = 12, height: float = 8, dpi: int = 150) -> Path:
        """@brief Save ggplot figure to disk."""
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                ggsave(plot, filename=str(filename), width=width, height=height, dpi=dpi)
            return filename
        except Exception as e:
            raise IOError(f"Failed to save plot to '{filename}': {e}")


## @defgroup LanchesterPlotters Lanchester Analysis Plotters
## @{

class PlotLanchester(BasePlotter):
    """
    @brief  Simple Lanchester's Laws plot: Winner Casualties vs N.
    
    @details 
    - Solid lines: Empirical data (mean casualties)
    - Dashed lines: Theoretical predictions (Linear/Square Law)
    - One color per unit type (same for empirical + theoretical)
    """
    
    def plot(self, data: Any, **kwargs) -> Path:
        """Generate Lanchester plot."""
        ai_name = kwargs.get('ai_name', "Unknown AI")
        
        # Get summary DataFrame
        if hasattr(data, 'get_summary_by_type_and_n'):
            df = data.get_summary_by_type_and_n()
        else:
            df = self._convert_legacy(data)
        
        if df.empty:
            warnings.warn("Empty data for Lanchester plot")
            return self._generate_filename("lanchester_empty")
        
        plot = self._create_plot(df, ai_name)
        return self._save_plot(plot, self._generate_filename("lanchester_analysis"), 
                              width=10, height=6)
    
    def _convert_legacy(self, data: dict) -> pd.DataFrame:
        """Convert legacy PlotData dict to DataFrame."""
        records = []
        for unit_type, plot_data in data.items():
            if hasattr(plot_data, 'n_values'):
                for i, n in enumerate(plot_data.n_values):
                    if i < len(plot_data.avg_team_b_casualties):
                        records.append({
                            'unit_type': unit_type,
                            'n_value': n,
                            'mean_team_b_casualties': plot_data.avg_team_b_casualties[i],
                        })
        return pd.DataFrame(records)
    
    def _create_plot(self, df: pd.DataFrame, ai_name: str) -> ggplot:
        """Create simple Lanchester plot: solid=empirical, dashed=theory."""
        import numpy as np
        from plotnine import scale_linetype_identity
        
        # Column names
        n_col = 'n_value' if 'n_value' in df.columns else 'n'
        # Use Team B casualties (the 2N army) - this is what Lanchester's Laws predict
        cas_col = 'mean_team_b_casualties' if 'mean_team_b_casualties' in df.columns else 'mean_winner_casualties'
        
        # Clean data
        df = df.copy()
        df[n_col] = pd.to_numeric(df[n_col], errors='coerce')
        df[cas_col] = pd.to_numeric(df[cas_col], errors='coerce')
        df = df.dropna(subset=[n_col, cas_col])
        
        # Get unit types and assign colors
        unit_types = df['unit_type'].unique().tolist()
        colors = {ut: PALETTE_UNITS.get(ut, '#666666') for ut in unit_types}
        
        # Theoretical curves for each unit type
        n_values = sorted(df[n_col].unique())
        n_min, n_max = min(n_values), max(n_values)
        n_theory = np.linspace(n_min, n_max, 50)
        
        theory_records = []
        for ut in unit_types:
            ut_data = df[df['unit_type'] == ut]
            empirical_max = ut_data[cas_col].max()
            
            if empirical_max == 0:
                continue
            
            # Determine combat type for this unit
            combat_type = UNIT_TYPES.get(ut, 'Unknown')
            
            if combat_type == 'Melee':
                # Linear Law: casualties ∝ N
                scale = empirical_max / n_max if n_max > 0 else 1
                theory_cas = scale * n_theory
            else:
                # Square Law: casualties ∝ √N
                scale = empirical_max / np.sqrt(n_max) if n_max > 0 else 1
                theory_cas = scale * np.sqrt(n_theory)
            
            for i, n in enumerate(n_theory):
                theory_records.append({
                    'unit_type': ut,
                    n_col: n,
                    cas_col: theory_cas[i],
                })
        
        theory_df = pd.DataFrame(theory_records)
        
        # Mark data type
        df['data_type'] = 'solid'        # Empirical = solid
        theory_df['data_type'] = 'dashed'  # Theory = dashed
        
        # Combine
        combined = pd.concat([df[[n_col, cas_col, 'unit_type', 'data_type']], 
                             theory_df], ignore_index=True)
        
        # Build plot
        plot = (
            ggplot(combined, aes(x=n_col, y=cas_col, color='unit_type', linetype='data_type'))
            + geom_line(size=1.2)
            + geom_point(data=df, mapping=aes(x=n_col, y=cas_col, color='unit_type'), 
                        size=3, inherit_aes=False)
            + scale_color_manual(values=colors)
            + scale_linetype_identity()
            + labs(
                title=f"Lanchester's Laws — {ai_name}",
                x="Initial Force Size (N)",
                y="Winner Casualties (2N side)",
                color="Unit Type"
            )
            + theme_minimal()
            + theme(
                plot_title=element_text(size=14, weight='bold'),
                axis_title=element_text(size=11),
                legend_position='right',
                legend_title=element_text(size=10, weight='bold'),
                figure_size=(10, 6),
            )
        )
        
        return plot


## @}

## @defgroup GenericPlotters Generic Plot Types
## @{

class PlotWinRate(BasePlotter):
    """@brief Plot win/loss/draw distribution."""
    
    def plot(self, data: Any, **kwargs) -> Path:
        title = kwargs.get('title', 'Battle Results Distribution')
        
        if hasattr(data, 'get_summary_by_type_and_n'):
            df = data.get_summary_by_type_and_n()
            if not df.empty:
                # Aggregate win rates by unit type
                summary = df.groupby('unit_type').agg(
                    win_rate_2n=('team_b_win_rate', 'mean'),
                    win_rate_n=('team_a_win_rate', 'mean'),
                    draw_rate=('draw_rate', 'mean')
                ).reset_index()
                
                # Melt for plotting
                melted = summary.melt(
                    id_vars='unit_type',
                    value_vars=['win_rate_2n', 'win_rate_n', 'draw_rate'],
                    var_name='result',
                    value_name='rate'
                )
                melted['rate'] *= 100
                
                plot = (
                    ggplot(melted, aes(x='unit_type', y='rate', fill='result'))
                    + geom_bar(stat='identity', position='dodge')
                    + scale_fill_manual(
                        values={'win_rate_2n': '#2ecc71', 'win_rate_n': '#e74c3c', 'draw_rate': '#95a5a6'},
                        labels={'win_rate_2n': '2N Wins', 'win_rate_n': 'N Wins', 'draw_rate': 'Draw'}
                    )
                    + labs(title=title, x="Unit Type", y="Rate (%)", fill="Outcome")
                    + theme_battle()
                )
                
                return self._save_plot(plot, self._generate_filename("winrate"))
        
        # Fallback for simple dict
        if isinstance(data, dict) and ('wins' in data or 'losses' in data):
            wins = data.get('wins', 0)
            losses = data.get('losses', 0)
            draws = data.get('draws', 0)
            total = wins + losses + draws
            
            if total == 0:
                return self._generate_filename("winrate_empty")
            
            df = pd.DataFrame([
                {'result': 'Wins', 'count': wins, 'pct': wins/total*100},
                {'result': 'Losses', 'count': losses, 'pct': losses/total*100},
                {'result': 'Draws', 'count': draws, 'pct': draws/total*100}
            ])
            
            plot = (
                ggplot(df, aes(x='result', y='pct', fill='result'))
                + geom_bar(stat='identity', width=0.6)
                + scale_fill_manual(values=PALETTE_RESULTS)
                + labs(title=title, x="Result", y="Percentage (%)")
                + theme_battle()
                + theme(legend_position='none')
            )
            
            return self._save_plot(plot, self._generate_filename("winrate"))
        
        return self._generate_filename("winrate_empty")


class PlotCasualties(BasePlotter):
    """@brief Plot casualties data for both teams."""
    
    def plot(self, data: Any, **kwargs) -> Path:
        title = kwargs.get('title', 'Casualties Analysis')
        
        if hasattr(data, 'get_summary_by_type_and_n'):
            df = data.get_summary_by_type_and_n()
            
            if not df.empty:
                # Plot both teams' casualties
                plot_df = df[['unit_type', 'n_value', 
                              'mean_team_a_casualties', 'mean_team_b_casualties']].copy()
                
                # Melt for long format
                melted = plot_df.melt(
                    id_vars=['unit_type', 'n_value'],
                    value_vars=['mean_team_a_casualties', 'mean_team_b_casualties'],
                    var_name='team',
                    value_name='casualties'
                )
                melted['team'] = melted['team'].map({
                    'mean_team_a_casualties': 'Team A',
                    'mean_team_b_casualties': 'Team B'
                })
                
                plot = (
                    ggplot(melted, aes(x='n_value', y='casualties', color='team'))
                    + geom_line(size=1.2)
                    + geom_point(size=3)
                    + facet_wrap('~unit_type', scales='free_y')
                    + scale_color_manual(values=PALETTE_TEAMS)
                    + labs(title=title, x="Initial N", y="Mean Casualties", color="Team")
                    + theme_battle()
                )
                
                return self._save_plot(plot, self._generate_filename("casualties"))
        
        return self._generate_filename("casualties_empty")


class PlotDuration(BasePlotter):
    """@brief Plot battle duration statistics."""
    
    def plot(self, data: Any, **kwargs) -> Path:
        title = kwargs.get('title', 'Battle Duration Analysis')
        
        if hasattr(data, 'df') and not data.df.empty:
            df = data.df
            
            # Boxplot of duration by unit type and N
            plot = (
                ggplot(df, aes(x='n_value', y='duration_ticks', 
                              group='n_value', fill='unit_type'))
                + geom_boxplot(alpha=0.7, outlier_alpha=0.3)
                + facet_wrap('~unit_type', scales='free')
                + labs(title=title, x="Initial N", y="Duration (ticks)", fill="Unit Type")
                + theme_battle()
                + theme(legend_position='none')
            )
            
            return self._save_plot(plot, self._generate_filename("duration"))
        
        return self._generate_filename("duration_empty")


class PlotComparison(BasePlotter):
    """@brief Multi-metric comparison plot."""
    
    def plot(self, data: Any, **kwargs) -> Path:
        title = kwargs.get('title', 'Battle Comparison')
        
        if hasattr(data, 'to_long_format'):
            df = data.to_long_format()
            
            if not df.empty:
                unit_types = df['unit_type'].unique().tolist()
                colors = [PALETTE_UNITS.get(ut, PALETTE_UNITS['default']) for ut in unit_types]
                color_map = dict(zip(unit_types, colors))
                
                plot = (
                    ggplot(df, aes(x='n_value', y='value', color='unit_type'))
                    + geom_line(size=1.2)
                    + geom_point(size=2)
                    + facet_wrap('~metric', scales='free_y', ncol=2)
                    + scale_color_manual(values=color_map)
                    + labs(title=title, x="N Value", y="Value", color="Unit Type")
                    + theme_battle()
                )
                
                return self._save_plot(plot, self._generate_filename("comparison"),
                                       width=14, height=10)
        
        return self._generate_filename("comparison_empty")


class PlotHeatmap(BasePlotter):
    """@brief Heatmap visualization for matrix data."""
    
    def plot(self, data: Any, **kwargs) -> Path:
        title = kwargs.get('title', 'Results Matrix')
        
        if hasattr(data, 'df') and not data.df.empty:
            df = data.df
            
            # Create pivot table: unit_type x n_value, values = win rate
            pivot = df.pivot_table(
                index='unit_type',
                columns='n_value',
                values='winner',
                aggfunc=lambda x: (x == 'B').mean() * 100
            ).reset_index()
            
            melted = pivot.melt(id_vars='unit_type', var_name='n', value_name='win_rate')
            
            plot = (
                ggplot(melted, aes(x='n', y='unit_type', fill='win_rate'))
                + geom_tile(color='white')
                + geom_text(aes(label='win_rate'), size=8, format_string='{:.0f}')
                + scale_fill_gradient2(low='#e74c3c', mid='#f9f9f9', high='#27ae60', midpoint=50)
                + labs(title=title, x="N Value", y="Unit Type", fill="2N Win Rate (%)")
                + theme_battle()
            )
            
            return self._save_plot(plot, self._generate_filename("heatmap"))
        
        return self._generate_filename("heatmap_empty")


class PlotRawData(BasePlotter):
    """@brief Plot raw simulation data with individual runs visible."""
    
    def plot(self, data: Any, **kwargs) -> Path:
        title = kwargs.get('title', 'Raw Simulation Results')
        
        if hasattr(data, 'df') and not data.df.empty:
            df = data.df
            
            # Scatter plot with jitter to show individual runs
            unit_types = df['unit_type'].unique().tolist()
            colors = [PALETTE_UNITS.get(ut, PALETTE_UNITS['default']) for ut in unit_types]
            color_map = dict(zip(unit_types, colors))
            
            plot = (
                ggplot(df, aes(x='n_value', y='winner_casualties', color='unit_type'))
                + geom_point(alpha=0.4, size=2)
                + geom_smooth(method='loess', se=True, alpha=0.3)
                + scale_color_manual(values=color_map)
                + labs(
                    title=title,
                    subtitle="Individual simulation runs with smoothed trend",
                    x="Initial N",
                    y="Winner Casualties",
                    color="Unit Type"
                )
                + theme_battle()
            )
            
            return self._save_plot(plot, self._generate_filename("raw_data"))
        
        return self._generate_filename("raw_data_empty")


## @}

## @defgroup ScenarioPlotters General Scenario Plotters
## @{

class PlotScenarioOverview(BasePlotter):
    """
    @brief  Overview plot for any battle scenario.
    @details Shows team performance, casualties distribution, and battle outcomes.
    """
    
    def plot(self, data: Any, **kwargs) -> Path:
        scenario_name = kwargs.get('scenario_name', 'Battle')
        
        if hasattr(data, 'df') and not data.df.empty:
            df = data.df.copy()
            
            # Create summary statistics
            summary = df.groupby('unit_type').agg(
                total_battles=('run_id', 'count'),
                team_a_wins=('winner', lambda x: (x == 'A').sum()),
                team_b_wins=('winner', lambda x: (x == 'B').sum()),
                draws=('winner', lambda x: (x == 'draw').sum()),
                avg_duration=('duration_ticks', 'mean'),
                avg_team_a_casualties=('team_a_casualties', 'mean'),
                avg_team_b_casualties=('team_b_casualties', 'mean'),
            ).reset_index()
            
            # Calculate win rates
            summary['team_a_winrate'] = summary['team_a_wins'] / summary['total_battles'] * 100
            summary['team_b_winrate'] = summary['team_b_wins'] / summary['total_battles'] * 100
            
            # Melt for stacked bar
            melted = summary.melt(
                id_vars='unit_type',
                value_vars=['team_a_winrate', 'team_b_winrate'],
                var_name='team',
                value_name='winrate'
            )
            melted['team'] = melted['team'].map({
                'team_a_winrate': 'Team A',
                'team_b_winrate': 'Team B'
            })
            
            plot = (
                ggplot(melted, aes(x='unit_type', y='winrate', fill='team'))
                + geom_bar(stat='identity', position='dodge', width=0.7)
                + scale_fill_manual(values={'Team A': '#e74c3c', 'Team B': '#3498db'})
                + labs(
                    title=f"Scenario Overview: {scenario_name}",
                    subtitle="Win rate comparison by unit type",
                    x="Unit Type",
                    y="Win Rate (%)",
                    fill="Team"
                )
                + theme_battle()
                + theme(legend_position='bottom')
            )
            
            return self._save_plot(plot, self._generate_filename("scenario_overview"))
        
        return self._generate_filename("scenario_overview_empty")


class PlotTeamPerformance(BasePlotter):
    """
    @brief  Compare team performance across battles.
    @details Bar chart showing wins, losses, casualties for each team.
    """
    
    def plot(self, data: Any, **kwargs) -> Path:
        title = kwargs.get('title', 'Team Performance Comparison')
        
        if hasattr(data, 'df') and not data.df.empty:
            df = data.df
            
            # Calculate overall stats
            total_battles = len(df)
            team_a_wins = (df['winner'] == 'A').sum()
            team_b_wins = (df['winner'] == 'B').sum()
            
            avg_a_casualties = df['team_a_casualties'].mean()
            avg_b_casualties = df['team_b_casualties'].mean()
            
            # Create comparison DataFrame
            perf_df = pd.DataFrame([
                {'metric': 'Win Rate (%)', 'Team A': team_a_wins/total_battles*100, 
                 'Team B': team_b_wins/total_battles*100},
                {'metric': 'Avg Casualties', 'Team A': avg_a_casualties, 
                 'Team B': avg_b_casualties},
            ])
            
            melted = perf_df.melt(id_vars='metric', var_name='team', value_name='value')
            
            plot = (
                ggplot(melted, aes(x='metric', y='value', fill='team'))
                + geom_bar(stat='identity', position='dodge', width=0.6)
                + scale_fill_manual(values={'Team A': '#e74c3c', 'Team B': '#3498db'})
                + labs(
                    title=title,
                    subtitle=f"Based on {total_battles} battles",
                    x="Metric",
                    y="Value",
                    fill="Team"
                )
                + theme_battle()
                + theme(legend_position='bottom')
            )
            
            return self._save_plot(plot, self._generate_filename("team_performance"))
        
        return self._generate_filename("team_performance_empty")


class PlotCasualtiesDistribution(BasePlotter):
    """
    @brief  Distribution of casualties across battles.
    @details Boxplot or violin plot showing casualty spread.
    """
    
    def plot(self, data: Any, **kwargs) -> Path:
        title = kwargs.get('title', 'Casualties Distribution')
        
        if hasattr(data, 'df') and not data.df.empty:
            df = data.df.copy()
            
            # Melt casualties into long format
            melted = pd.melt(
                df,
                id_vars=['run_id', 'unit_type'],
                value_vars=['team_a_casualties', 'team_b_casualties'],
                var_name='team',
                value_name='casualties'
            )
            melted['team'] = melted['team'].map({
                'team_a_casualties': 'Team A',
                'team_b_casualties': 'Team B'
            })
            
            plot = (
                ggplot(melted, aes(x='unit_type', y='casualties', fill='team'))
                + geom_boxplot(alpha=0.7, outlier_alpha=0.3)
                + scale_fill_manual(values={'Team A': '#e74c3c', 'Team B': '#3498db'})
                + labs(
                    title=title,
                    subtitle="Distribution of casualties per battle",
                    x="Unit Type",
                    y="Casualties",
                    fill="Team"
                )
                + theme_battle()
                + theme(legend_position='bottom')
            )
            
            return self._save_plot(plot, self._generate_filename("casualties_distribution"))
        
        return self._generate_filename("casualties_distribution_empty")


class PlotBattleTimeline(BasePlotter):
    """
    @brief  Battle duration analysis over multiple runs.
    @details Shows how battle length varies with configuration.
    """
    
    def plot(self, data: Any, **kwargs) -> Path:
        title = kwargs.get('title', 'Battle Duration Timeline')
        
        if hasattr(data, 'df') and not data.df.empty:
            df = data.df.copy()
            
            # Color by unit type
            unit_types = df['unit_type'].unique().tolist()
            colors = [PALETTE_UNITS.get(ut, PALETTE_UNITS['default']) for ut in unit_types]
            color_map = dict(zip(unit_types, colors))
            
            plot = (
                ggplot(df, aes(x='run_id', y='duration_ticks', color='unit_type'))
                + geom_line(alpha=0.5)
                + geom_point(size=2, alpha=0.7)
                + scale_color_manual(values=color_map)
                + labs(
                    title=title,
                    subtitle="Battle duration across simulation runs",
                    x="Run ID",
                    y="Duration (ticks)",
                    color="Unit Type"
                )
                + theme_battle()
                + theme(legend_position='bottom')
            )
            
            return self._save_plot(plot, self._generate_filename("battle_timeline"))
        
        return self._generate_filename("battle_timeline_empty")


class PlotWinnerAnalysis(BasePlotter):
    """
    @brief  Detailed winner analysis with casualties breakdown.
    @details Shows winner casualties vs loser casualties correlation.
    """
    
    def plot(self, data: Any, **kwargs) -> Path:
        title = kwargs.get('title', 'Winner vs Loser Analysis')
        
        if hasattr(data, 'df') and not data.df.empty:
            df = data.df.copy()
            
            # Calculate loser casualties
            df['loser_casualties'] = df.apply(
                lambda row: row['team_a_casualties'] if row['winner'] == 'B' 
                else row['team_b_casualties'] if row['winner'] == 'A' else 0,
                axis=1
            )
            
            # Filter out draws for this plot
            df_wins = df[df['winner'].isin(['A', 'B'])]
            
            if df_wins.empty:
                return self._generate_filename("winner_analysis_empty")
            
            # Color by unit type
            unit_types = df_wins['unit_type'].unique().tolist()
            colors = [PALETTE_UNITS.get(ut, PALETTE_UNITS['default']) for ut in unit_types]
            color_map = dict(zip(unit_types, colors))
            
            plot = (
                ggplot(df_wins, aes(x='winner_casualties', y='loser_casualties', 
                                   color='unit_type', shape='winner'))
                + geom_point(size=3, alpha=0.7)
                + scale_color_manual(values=color_map)
                + labs(
                    title=title,
                    subtitle="Relationship between winner and loser casualties",
                    x="Winner Casualties",
                    y="Loser Casualties",
                    color="Unit Type",
                    shape="Winner"
                )
                + theme_battle()
                + theme(legend_position='right')
            )
            
            return self._save_plot(plot, self._generate_filename("winner_analysis"))
        
        return self._generate_filename("winner_analysis_empty")


class PlotUnitComparison(BasePlotter):
    """
    @brief  Compare unit types side by side.
    @details Bar charts comparing win rate, casualties, and duration by unit type.
    """
    
    def plot(self, data: Any, **kwargs) -> Path:
        title = kwargs.get('title', 'Unit Type Comparison')
        
        if hasattr(data, 'get_summary_by_type_and_n'):
            summary = data.get_summary_by_type_and_n()
            
            if summary.empty:
                return self._generate_filename("unit_comparison_empty")
            
            # Aggregate by unit type only (mean across all N values)
            agg = summary.groupby('unit_type').agg({
                'win_rate': 'mean',
                'mean_team_a_casualties': 'mean',
                'mean_team_b_casualties': 'mean',
                'mean_duration': 'mean'
            }).reset_index()
            
            agg.columns = ['unit_type', 'Win Rate (%)', 'Team A Casualties', 
                          'Team B Casualties', 'Duration (ticks)']
            
            # Melt for plotting
            melted = agg.melt(
                id_vars='unit_type',
                var_name='metric',
                value_name='value'
            )
            
            # Get colors for unit types
            unit_types = melted['unit_type'].unique().tolist()
            colors = [PALETTE_UNITS.get(ut, PALETTE_UNITS['default']) for ut in unit_types]
            color_map = dict(zip(unit_types, colors))
            
            plot = (
                ggplot(melted, aes(x='unit_type', y='value', fill='unit_type'))
                + geom_col(position='dodge', width=0.7)
                + facet_wrap('~metric', scales='free_y', ncol=2)
                + scale_fill_manual(values=color_map)
                + labs(title=title, x="Unit Type", y="Value", fill="Unit Type")
                + theme_battle()
                + theme(
                    axis_text_x=element_text(rotation=45, hjust=1),
                    legend_position='none'
                )
            )
            
            return self._save_plot(plot, self._generate_filename("unit_comparison"),
                                   width=12, height=10)
        
        return self._generate_filename("unit_comparison_empty")


class PlotDamageMatrix(BasePlotter):
    """
    @brief  Plot theoretical damage matrix between unit types.
    @details Shows how much damage each unit type deals to others.
             Based on DAMAGE_MATRIX constants from unit stats.
    """
    
    def plot(self, data: Any = None, **kwargs) -> Path:
        title = kwargs.get('title', 'Damage Matrix (Attacker → Target)')
        
        # Build DataFrame from DAMAGE_MATRIX
        rows = []
        for attacker, targets in DAMAGE_MATRIX.items():
            for target, damage in targets.items():
                rows.append({
                    'attacker': attacker,
                    'target': target,
                    'damage': damage,
                    'hits_to_kill': HP_VALUES[target] / damage if damage > 0 else float('inf')
                })
        
        df = pd.DataFrame(rows)
        
        # Damage heatmap
        plot = (
            ggplot(df, aes(x='target', y='attacker', fill='damage'))
            + geom_tile(color='white', size=1)
            + geom_text(aes(label='damage'), size=14, color='white', fontweight='bold')
            + scale_fill_gradient(low='#3498db', high='#e74c3c', name='Damage')
            + labs(
                title=title,
                subtitle='Higher = more damage dealt',
                x='Target',
                y='Attacker'
            )
            + theme_battle()
            + theme(
                axis_text_x=element_text(size=12),
                axis_text_y=element_text(size=12),
                legend_position='right'
            )
        )
        
        return self._save_plot(plot, self._generate_filename("damage_matrix"))


class PlotKillEfficiency(BasePlotter):
    """
    @brief  Plot hits-to-kill efficiency matrix.
    @details Shows how many hits each unit needs to kill another.
    """
    
    def plot(self, data: Any = None, **kwargs) -> Path:
        title = kwargs.get('title', 'Hits to Kill (Attacker → Target)')
        
        # Build DataFrame
        rows = []
        for attacker, targets in DAMAGE_MATRIX.items():
            for target, damage in targets.items():
                htk = HP_VALUES[target] / damage if damage > 0 else 99
                rows.append({
                    'attacker': attacker,
                    'target': target,
                    'hits_to_kill': round(htk, 1)
                })
        
        df = pd.DataFrame(rows)
        
        plot = (
            ggplot(df, aes(x='target', y='attacker', fill='hits_to_kill'))
            + geom_tile(color='white', size=1)
            + geom_text(aes(label='hits_to_kill'), size=12, color='white', fontweight='bold')
            + scale_fill_gradient(low='#27ae60', high='#e74c3c', name='Hits')
            + labs(
                title=title,
                subtitle='Lower = kills faster',
                x='Target',
                y='Attacker'
            )
            + theme_battle()
            + theme(
                axis_text_x=element_text(size=12),
                axis_text_y=element_text(size=12),
                legend_position='right'
            )
        )
        
        return self._save_plot(plot, self._generate_filename("kill_efficiency"))


## @}

## @defgroup PlotterRegistry Plotter Registry
## @{

## @var PLOTTERS
#  @brief Registry mapping plotter names to classes.
PLOTTERS: Dict[str, type] = {
    # Lanchester (main analysis) - casualties vs N with theoretical curves
    'PlotLanchester': PlotLanchester,
    'lanchester': PlotLanchester,
    
    # Generic plot types
    'PlotWinRate': PlotWinRate,
    'winrate': PlotWinRate,
    'PlotCasualties': PlotCasualties,
    'casualties': PlotCasualties,
    'PlotDuration': PlotDuration,
    'duration': PlotDuration,
    'PlotComparison': PlotComparison,
    'comparison': PlotComparison,
    'PlotHeatmap': PlotHeatmap,
    'heatmap': PlotHeatmap,
    'PlotRawData': PlotRawData,
    'raw': PlotRawData,
    
    # General scenario plotters
    'PlotScenarioOverview': PlotScenarioOverview,
    'overview': PlotScenarioOverview,
    'PlotTeamPerformance': PlotTeamPerformance,
    'team': PlotTeamPerformance,
    'PlotCasualtiesDistribution': PlotCasualtiesDistribution,
    'distribution': PlotCasualtiesDistribution,
    'PlotBattleTimeline': PlotBattleTimeline,
    'timeline': PlotBattleTimeline,
    'PlotWinnerAnalysis': PlotWinnerAnalysis,
    'winner': PlotWinnerAnalysis,
    'PlotUnitComparison': PlotUnitComparison,
    'units': PlotUnitComparison,
    
    # Unit interaction plotters
    'PlotDamageMatrix': PlotDamageMatrix,
    'damage': PlotDamageMatrix,
    'PlotKillEfficiency': PlotKillEfficiency,
    'kills': PlotKillEfficiency,
}


def get_plotter(name: str, output_dir: str = "Reports") -> BasePlotter:
    """@brief Get a plotter instance by name."""
    if name not in PLOTTERS:
        available = ', '.join(sorted(set(PLOTTERS.keys())))
        raise ValueError(f"Unknown plotter: {name}. Available: {available}")
    return PLOTTERS[name](output_dir=output_dir)


def list_plotters() -> List[str]:
    """@brief List available plotter class names."""
    return [name for name in PLOTTERS.keys() if name.startswith('Plot')]

## @}