# -*- coding: utf-8 -*-
"""
@file advanced_plotters.py
@brief Advanced Data Visualization for Battle Analysis

@details
Professional-grade visualizations using plotnine (ggplot2) including:
- Heatmaps and correlation matrices
- Boxplots and violin plots
- Grouped barplots
- Faceted analysis
- Statistical annotations
- Multi-panel dashboards

Designed for data analysts requiring publication-quality figures.

"""

import os
import warnings
from typing import Dict, List, Optional
from datetime import datetime

import pandas as pd
import numpy as np

# Import plotnine
try:
    from plotnine import (
        ggplot, aes,
        geom_tile, geom_text, geom_boxplot, geom_violin,
        geom_bar, geom_col, geom_errorbar, geom_point, geom_line,
        geom_hline, geom_vline, geom_segment, geom_label,
        geom_density, geom_histogram, geom_jitter, geom_crossbar,
        facet_wrap, facet_grid,
        labs, theme, theme_minimal, theme_bw,
        element_text, element_blank, element_rect, element_line,
        scale_fill_gradient2, scale_fill_gradient, scale_fill_manual,
        scale_color_manual, scale_fill_brewer, scale_color_brewer,
        scale_x_discrete, scale_y_continuous, scale_y_discrete,
        coord_flip, coord_fixed,
        position_dodge, position_fill, position_stack,
        guides, guide_legend, guide_colorbar,
        annotate,
        stat_summary,
    )
    PLOTNINE_AVAILABLE = True
except ImportError:
    PLOTNINE_AVAILABLE = False

from Utils.battle_data import PlotData
from Utils.statistical_analysis import (
    StatisticalAnalyzer, LanchesterAnalyzer, 
    create_analysis_dataframe, DescriptiveStats
)


# =============================================================================
# THEMES AND PALETTES
# =============================================================================

def theme_publication():
    """Professional publication-ready theme."""
    return (
        theme_minimal() +
        theme(
            plot_title=element_text(size=14, face='bold', ha='center'),
            plot_subtitle=element_text(size=11, color='#555555', ha='center'),
            axis_title=element_text(size=11, face='bold'),
            axis_text=element_text(size=10),
            axis_text_x=element_text(angle=45, ha='right'),
            legend_title=element_text(size=10, face='bold'),
            legend_text=element_text(size=9),
            legend_position='right',
            panel_grid_major=element_line(color='#E5E5E5', size=0.4),
            panel_grid_minor=element_blank(),
            strip_text=element_text(size=10, face='bold'),
            strip_background=element_rect(fill='#F0F0F0', color='#CCCCCC'),
            figure_size=(12, 8),
            dpi=150
        )
    )


PALETTE_DIVERGING = ['#D73027', '#F46D43', '#FDAE61', '#FEE08B', 
                     '#FFFFBF', '#D9EF8B', '#A6D96A', '#66BD63', '#1A9850']

PALETTE_SEQUENTIAL = ['#FFF5EB', '#FDD0A2', '#FDAE6B', '#FD8D3C', 
                      '#F16913', '#D94801', '#A63603', '#7F2704']

PALETTE_CATEGORICAL = ['#E74C3C', '#3498DB', '#27AE60', '#9B59B6', 
                       '#F39C12', '#1ABC9C', '#E67E22', '#2C3E50']

PALETTE_UNITS = {
    'Knight': '#E74C3C',
    'Crossbowman': '#3498DB', 
    'Pikeman': '#27AE60',
    'Melee': '#E74C3C',
    'Ranged': '#3498DB',
}


# =============================================================================
# HEATMAP VISUALIZATIONS
# =============================================================================

class HeatmapPlotter:
    """
    Creates heatmap visualizations including correlation matrices.
    """
    
    def __init__(self, output_dir: str = "Reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _generate_filename(self, prefix: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"{prefix}_{timestamp}.png")
    
    def correlation_heatmap(self, df: pd.DataFrame, 
                           title: str = "Correlation Matrix") -> str:
        """
        Create a correlation heatmap with annotations.
        
        @param df: DataFrame with numeric columns
        @param title: Plot title
        @return: Path to saved plot
        """
        # Calculate correlation matrix
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        corr_matrix = df[numeric_cols].corr()
        
        # Convert to long format for ggplot
        corr_long = corr_matrix.reset_index().melt(
            id_vars='index', 
            var_name='variable', 
            value_name='correlation'
        )
        corr_long.columns = ['var1', 'var2', 'correlation']
        
        # Round for annotation
        corr_long['label'] = corr_long['correlation'].round(2).astype(str)
        
        p = (
            ggplot(corr_long, aes(x='var1', y='var2', fill='correlation')) +
            geom_tile(color='white', size=0.5) +
            geom_text(aes(label='label'), size=8, color='black') +
            scale_fill_gradient2(
                low='#D73027', mid='#FFFFBF', high='#1A9850',
                midpoint=0, limits=(-1, 1),
                name='Correlation'
            ) +
            labs(
                title=title,
                subtitle="Pearson correlation coefficients",
                x="", y=""
            ) +
            theme_publication() +
            theme(
                axis_text_x=element_text(angle=45, ha='right'),
                figure_size=(10, 8)
            ) +
            coord_fixed()
        )
        
        filepath = self._generate_filename("correlation_heatmap")
        p.save(filepath, width=10, height=8, dpi=150, verbose=False)
        
        return filepath
    
    def metric_heatmap(self, df: pd.DataFrame, 
                       x_var: str, y_var: str, value_var: str,
                       title: str = "Metric Heatmap") -> str:
        """
        Create a heatmap for a specific metric.
        
        @param df: DataFrame
        @param x_var: Column for x-axis
        @param y_var: Column for y-axis  
        @param value_var: Column for values (fill)
        @param title: Plot title
        @return: Path to saved plot
        """
        # Aggregate if needed
        pivot_data = df.groupby([x_var, y_var])[value_var].mean().reset_index()
        pivot_data['label'] = pivot_data[value_var].round(1).astype(str)
        
        p = (
            ggplot(pivot_data, aes(x=x_var, y=y_var, fill=value_var)) +
            geom_tile(color='white', size=0.5) +
            geom_text(aes(label='label'), size=9, color='black') +
            scale_fill_gradient(
                low='#FFF5EB', high='#D94801',
                name=value_var.replace('_', ' ').title()
            ) +
            labs(title=title, x=x_var.replace('_', ' ').title(), 
                 y=y_var.replace('_', ' ').title()) +
            theme_publication() +
            theme(axis_text_x=element_text(angle=45, ha='right'))
        )
        
        filepath = self._generate_filename("metric_heatmap")
        p.save(filepath, width=10, height=7, dpi=150, verbose=False)
        
        return filepath


# =============================================================================
# BOXPLOT AND DISTRIBUTION VISUALIZATIONS
# =============================================================================

class DistributionPlotter:
    """
    Creates distribution visualizations (boxplots, violins, histograms).
    """
    
    def __init__(self, output_dir: str = "Reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _generate_filename(self, prefix: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"{prefix}_{timestamp}.png")
    
    def boxplot_comparison(self, df: pd.DataFrame, 
                          x_var: str, y_var: str,
                          fill_var: Optional[str] = None,
                          title: str = "Distribution Comparison") -> str:
        """
        Create grouped boxplots for comparison.
        
        @param df: DataFrame
        @param x_var: Categorical variable for x-axis
        @param y_var: Numeric variable for y-axis
        @param fill_var: Optional grouping variable for fill
        @param title: Plot title
        @return: Path to saved plot
        """
        if fill_var:
            p = (
                ggplot(df, aes(x=x_var, y=y_var, fill=fill_var)) +
                geom_boxplot(alpha=0.7, outlier_alpha=0.5) +
                scale_fill_brewer(type='qual', palette='Set2') +
                labs(
                    title=title,
                    x=x_var.replace('_', ' ').title(),
                    y=y_var.replace('_', ' ').title(),
                    fill=fill_var.replace('_', ' ').title()
                ) +
                theme_publication()
            )
        else:
            p = (
                ggplot(df, aes(x=x_var, y=y_var)) +
                geom_boxplot(fill='#3498DB', alpha=0.7, outlier_alpha=0.5) +
                labs(
                    title=title,
                    x=x_var.replace('_', ' ').title(),
                    y=y_var.replace('_', ' ').title()
                ) +
                theme_publication()
            )
        
        filepath = self._generate_filename("boxplot")
        p.save(filepath, width=10, height=7, dpi=150, verbose=False)
        
        return filepath
    
    def violin_plot(self, df: pd.DataFrame,
                   x_var: str, y_var: str,
                   fill_var: Optional[str] = None,
                   title: str = "Distribution Density") -> str:
        """
        Create violin plots with embedded boxplots.
        
        @param df: DataFrame
        @param x_var: Categorical variable for x-axis
        @param y_var: Numeric variable for y-axis
        @param fill_var: Optional grouping variable
        @param title: Plot title
        @return: Path to saved plot
        """
        if fill_var:
            aes_map = aes(x=x_var, y=y_var, fill=fill_var)
        else:
            aes_map = aes(x=x_var, y=y_var)
        
        p = (
            ggplot(df, aes_map) +
            geom_violin(alpha=0.6, trim=True) +
            geom_boxplot(width=0.15, alpha=0.8, outlier_alpha=0.3) +
            scale_fill_brewer(type='qual', palette='Set2') +
            labs(
                title=title,
                subtitle="Violin plot with embedded boxplot",
                x=x_var.replace('_', ' ').title(),
                y=y_var.replace('_', ' ').title()
            ) +
            theme_publication()
        )
        
        filepath = self._generate_filename("violin")
        p.save(filepath, width=10, height=7, dpi=150, verbose=False)
        
        return filepath
    
    def histogram_density(self, df: pd.DataFrame,
                         var: str, group_var: Optional[str] = None,
                         bins: int = 30,
                         title: str = "Distribution") -> str:
        """
        Create histogram with density overlay.
        
        @param df: DataFrame
        @param var: Variable to plot
        @param group_var: Optional grouping variable
        @param bins: Number of histogram bins
        @param title: Plot title
        @return: Path to saved plot
        """
        if group_var:
            p = (
                ggplot(df, aes(x=var, fill=group_var)) +
                geom_histogram(aes(y='..density..'), alpha=0.5, bins=bins, 
                              position='identity') +
                geom_density(aes(color=group_var), size=1) +
                scale_fill_brewer(type='qual', palette='Set2') +
                scale_color_brewer(type='qual', palette='Set2') +
                labs(
                    title=title,
                    x=var.replace('_', ' ').title(),
                    y="Density"
                ) +
                theme_publication()
            )
        else:
            p = (
                ggplot(df, aes(x=var)) +
                geom_histogram(aes(y='..density..'), fill='#3498DB', 
                              alpha=0.7, bins=bins) +
                geom_density(color='#E74C3C', size=1.2) +
                labs(
                    title=title,
                    x=var.replace('_', ' ').title(),
                    y="Density"
                ) +
                theme_publication()
            )
        
        filepath = self._generate_filename("histogram")
        p.save(filepath, width=10, height=6, dpi=150, verbose=False)
        
        return filepath


# =============================================================================
# BARPLOT VISUALIZATIONS  
# =============================================================================

class BarPlotter:
    """
    Creates various barplot visualizations.
    """
    
    def __init__(self, output_dir: str = "Reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _generate_filename(self, prefix: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"{prefix}_{timestamp}.png")
    
    def grouped_barplot(self, df: pd.DataFrame,
                       x_var: str, y_var: str, group_var: str,
                       title: str = "Grouped Comparison",
                       error_bars: bool = True) -> str:
        """
        Create grouped barplot with optional error bars.
        
        @param df: DataFrame
        @param x_var: Categorical x variable
        @param y_var: Numeric y variable
        @param group_var: Grouping variable
        @param title: Plot title
        @param error_bars: Whether to show error bars
        @return: Path to saved plot
        """
        # Aggregate data
        agg_df = df.groupby([x_var, group_var]).agg({
            y_var: ['mean', 'std', 'count']
        }).reset_index()
        agg_df.columns = [x_var, group_var, 'mean', 'std', 'n']
        agg_df['se'] = agg_df['std'] / np.sqrt(agg_df['n'])
        agg_df['ci'] = 1.96 * agg_df['se']
        
        p = (
            ggplot(agg_df, aes(x=x_var, y='mean', fill=group_var)) +
            geom_col(position=position_dodge(width=0.8), alpha=0.8, width=0.7)
        )
        
        if error_bars:
            p = p + geom_errorbar(
                aes(ymin='mean - ci', ymax='mean + ci'),
                position=position_dodge(width=0.8),
                width=0.2,
                size=0.5
            )
        
        p = (p +
            scale_fill_brewer(type='qual', palette='Set2') +
            labs(
                title=title,
                subtitle="Mean ± 95% CI" if error_bars else None,
                x=x_var.replace('_', ' ').title(),
                y=y_var.replace('_', ' ').title(),
                fill=group_var.replace('_', ' ').title()
            ) +
            theme_publication()
        )
        
        filepath = self._generate_filename("grouped_barplot")
        p.save(filepath, width=10, height=7, dpi=150, verbose=False)
        
        return filepath
    
    def stacked_barplot(self, df: pd.DataFrame,
                       x_var: str, y_var: str, stack_var: str,
                       title: str = "Stacked Distribution",
                       normalize: bool = False) -> str:
        """
        Create stacked barplot.
        
        @param df: DataFrame
        @param x_var: Categorical x variable
        @param y_var: Numeric y variable
        @param stack_var: Stacking variable
        @param title: Plot title
        @param normalize: If True, show proportions (100% stacked)
        @return: Path to saved plot
        """
        agg_df = df.groupby([x_var, stack_var])[y_var].sum().reset_index()
        
        position = position_fill() if normalize else position_stack()
        
        p = (
            ggplot(agg_df, aes(x=x_var, y=y_var, fill=stack_var)) +
            geom_col(position=position, alpha=0.85) +
            scale_fill_brewer(type='qual', palette='Set2') +
            labs(
                title=title,
                x=x_var.replace('_', ' ').title(),
                y="Proportion" if normalize else y_var.replace('_', ' ').title(),
                fill=stack_var.replace('_', ' ').title()
            ) +
            theme_publication()
        )
        
        if normalize:
            p = p + scale_y_continuous(labels=lambda x: [f'{v:.0%}' for v in x])
        
        filepath = self._generate_filename("stacked_barplot")
        p.save(filepath, width=10, height=7, dpi=150, verbose=False)
        
        return filepath
    
    def horizontal_barplot(self, df: pd.DataFrame,
                          x_var: str, y_var: str,
                          title: str = "Ranked Comparison",
                          sort: bool = True) -> str:
        """
        Create horizontal barplot (good for rankings).
        
        @param df: DataFrame
        @param x_var: Categorical variable (will be on y-axis)
        @param y_var: Numeric variable (will be on x-axis)
        @param title: Plot title
        @param sort: Whether to sort by value
        @return: Path to saved plot
        """
        agg_df = df.groupby(x_var)[y_var].mean().reset_index()
        
        if sort:
            agg_df = agg_df.sort_values(y_var, ascending=True)
            agg_df[x_var] = pd.Categorical(agg_df[x_var], 
                                           categories=agg_df[x_var].tolist(), 
                                           ordered=True)
        
        p = (
            ggplot(agg_df, aes(x=x_var, y=y_var)) +
            geom_col(fill='#3498DB', alpha=0.8) +
            geom_text(aes(label=y_var), 
                     format_string='{:.1f}', 
                     ha='left', 
                     nudge_y=agg_df[y_var].max() * 0.02,
                     size=9) +
            coord_flip() +
            labs(
                title=title,
                x="",
                y=y_var.replace('_', ' ').title()
            ) +
            theme_publication() +
            theme(axis_text_y=element_text(angle=0, ha='right'))
        )
        
        filepath = self._generate_filename("horizontal_barplot")
        p.save(filepath, width=10, height=max(6, len(agg_df) * 0.5), dpi=150, verbose=False)
        
        return filepath


# =============================================================================
# STATISTICAL SUMMARY VISUALIZATIONS
# =============================================================================

class StatisticalPlotter:
    """
    Creates visualizations with statistical annotations.
    """
    
    def __init__(self, output_dir: str = "Reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.stat_analyzer = StatisticalAnalyzer()
    
    def _generate_filename(self, prefix: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"{prefix}_{timestamp}.png")
    
    def mean_comparison_plot(self, df: pd.DataFrame,
                            x_var: str, y_var: str,
                            title: str = "Mean Comparison with CI") -> str:
        """
        Create point plot with means and confidence intervals.
        
        @param df: DataFrame
        @param x_var: Grouping variable
        @param y_var: Numeric variable
        @param title: Plot title
        @return: Path to saved plot
        """
        # Calculate statistics per group
        stats_list = []
        for group in df[x_var].unique():
            group_data = df[df[x_var] == group][y_var].dropna()
            desc = self.stat_analyzer.descriptive_stats(group_data.values)
            stats_list.append({
                x_var: group,
                'mean': desc.mean,
                'ci_lower': desc.ci_lower,
                'ci_upper': desc.ci_upper,
                'se': desc.se,
                'n': desc.n
            })
        
        stats_df = pd.DataFrame(stats_list)
        
        p = (
            ggplot(stats_df, aes(x=x_var, y='mean')) +
            geom_point(size=4, color='#E74C3C') +
            geom_errorbar(aes(ymin='ci_lower', ymax='ci_upper'), 
                         width=0.2, size=0.8, color='#E74C3C') +
            geom_text(aes(label='n'), 
                     format_string='n={:.0f}',
                     va='bottom',
                     nudge_y=stats_df['ci_upper'].max() * 0.05,
                     size=9) +
            labs(
                title=title,
                subtitle="Mean ± 95% Confidence Interval",
                x=x_var.replace('_', ' ').title(),
                y=y_var.replace('_', ' ').title()
            ) +
            theme_publication()
        )
        
        filepath = self._generate_filename("mean_comparison")
        p.save(filepath, width=10, height=7, dpi=150, verbose=False)
        
        return filepath
    
    def effect_size_plot(self, comparisons: List[Dict]) -> str:
        """
        Create forest plot for effect sizes.
        
        @param comparisons: List of comparison dicts with 'comparison', 
                           'effect_size', 'ci_lower', 'ci_upper'
        @return: Path to saved plot
        """
        df = pd.DataFrame(comparisons)
        
        # Add CI if not present (approximate)
        if 'ci_lower' not in df.columns:
            df['ci_lower'] = df['effect_size'] - 0.3
            df['ci_upper'] = df['effect_size'] + 0.3
        
        df['comparison'] = pd.Categorical(df['comparison'], 
                                          categories=df['comparison'].tolist()[::-1],
                                          ordered=True)
        
        p = (
            ggplot(df, aes(x='comparison', y='effect_size')) +
            geom_hline(yintercept=0, linetype='dashed', color='gray', alpha=0.7) +
            geom_hline(yintercept=-0.2, linetype='dotted', color='#FFA500', alpha=0.5) +
            geom_hline(yintercept=0.2, linetype='dotted', color='#FFA500', alpha=0.5) +
            geom_hline(yintercept=-0.8, linetype='dotted', color='#E74C3C', alpha=0.5) +
            geom_hline(yintercept=0.8, linetype='dotted', color='#E74C3C', alpha=0.5) +
            geom_point(size=4, color='#2C3E50') +
            geom_errorbar(aes(ymin='ci_lower', ymax='ci_upper'), 
                         width=0.2, size=0.8, color='#2C3E50') +
            coord_flip() +
            labs(
                title="Effect Size Comparison (Cohen's d)",
                subtitle="Dotted lines: small (±0.2) and large (±0.8) effect thresholds",
                x="",
                y="Effect Size (Cohen's d)"
            ) +
            theme_publication() +
            theme(axis_text_y=element_text(angle=0))
        )
        
        filepath = self._generate_filename("effect_size")
        p.save(filepath, width=10, height=max(5, len(df) * 0.6), dpi=150, verbose=False)
        
        return filepath


# =============================================================================
# COMPREHENSIVE ANALYSIS DASHBOARD
# =============================================================================

class AnalysisDashboard:
    """
    Creates comprehensive multi-panel analysis dashboards.
    """
    
    def __init__(self, output_dir: str = "Reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.heatmap = HeatmapPlotter(output_dir)
        self.distribution = DistributionPlotter(output_dir)
        self.barplot = BarPlotter(output_dir)
        self.statistical = StatisticalPlotter(output_dir)
        self.lanchester = LanchesterAnalyzer()
        self.stat_analyzer = StatisticalAnalyzer()
    
    def generate_lanchester_dashboard(self, data: Dict[str, PlotData]) -> Dict[str, str]:
        """
        Generate comprehensive Lanchester analysis dashboard.
        
        @param data: Dictionary of PlotData per unit type
        @return: Dictionary of generated file paths
        """
        warnings.filterwarnings('ignore')
        
        # Convert to DataFrame
        df = create_analysis_dataframe(data)
        
        if df.empty:
            return {"error": "No data available for analysis"}
        
        generated_files = {}
        
        # 1. Correlation heatmap
        try:
            generated_files['correlation_heatmap'] = self.heatmap.correlation_heatmap(
                df, title="Battle Metrics Correlation Matrix"
            )
        except Exception as e:
            generated_files['correlation_heatmap'] = f"Error: {e}"
        
        # 2. Boxplot: Casualties by unit type
        try:
            generated_files['boxplot_casualties'] = self.distribution.boxplot_comparison(
                df, x_var='unit_type', y_var='team_b_casualties',
                title="Winner (2N) Casualties Distribution by Unit Type"
            )
        except Exception as e:
            generated_files['boxplot_casualties'] = f"Error: {e}"
        
        # 3. Barplot: Mean casualties comparison
        if len(df['unit_type'].unique()) > 1:
            try:
                # Create a comparison DataFrame
                summary_df = df.groupby('unit_type').agg({
                    'team_b_casualties': 'mean',
                    'team_a_casualties': 'mean',
                    'avg_duration': 'mean'
                }).reset_index()
                
                # Melt for grouped comparison
                melt_df = summary_df.melt(
                    id_vars='unit_type',
                    value_vars=['team_a_casualties', 'team_b_casualties'],
                    var_name='team',
                    value_name='casualties'
                )
                melt_df['team'] = melt_df['team'].map({
                    'team_a_casualties': 'Team A (N)',
                    'team_b_casualties': 'Team B (2N)'
                })
                
                generated_files['barplot_casualties'] = self.barplot.grouped_barplot(
                    melt_df, x_var='unit_type', y_var='casualties', group_var='team',
                    title="Mean Casualties by Unit Type and Team"
                )
            except Exception as e:
                generated_files['barplot_casualties'] = f"Error: {e}"
        
        # 4. Mean comparison with CI
        try:
            generated_files['mean_comparison'] = self.statistical.mean_comparison_plot(
                df, x_var='unit_type', y_var='team_b_casualties',
                title="Mean Winner Casualties with 95% CI"
            )
        except Exception as e:
            generated_files['mean_comparison'] = f"Error: {e}"
        
        # 5. Histogram of battle durations
        try:
            generated_files['histogram_duration'] = self.distribution.histogram_density(
                df, var='avg_duration', group_var='unit_type',
                title="Battle Duration Distribution by Unit Type"
            )
        except Exception as e:
            generated_files['histogram_duration'] = f"Error: {e}"
        
        # 6. Casualty rate heatmap (by N and unit type)
        try:
            generated_files['casualty_heatmap'] = self.heatmap.metric_heatmap(
                df, x_var='n', y_var='unit_type', value_var='team_b_casualty_rate',
                title="Winner Casualty Rate by Army Size and Unit Type"
            )
        except Exception as e:
            generated_files['casualty_heatmap'] = f"Error: {e}"
        
        # 7. Statistical analysis results
        try:
            lanchester_results = self.lanchester.test_lanchester_law(data)
            comparison_results = self.lanchester.compare_unit_types(data)
            generated_files['statistical_analysis'] = {
                'lanchester_test': lanchester_results,
                'comparison': comparison_results
            }
        except Exception as e:
            generated_files['statistical_analysis'] = f"Error: {e}"
        
        return generated_files
    
    def generate_summary_report(self, data: Dict[str, PlotData]) -> str:
        """
        Generate a text summary of statistical findings.
        
        @param data: Dictionary of PlotData per unit type
        @return: Summary text
        """
        df = create_analysis_dataframe(data)
        
        lines = [
            "=" * 70,
            "STATISTICAL ANALYSIS SUMMARY",
            "=" * 70,
            "",
        ]
        
        # Descriptive statistics per unit type
        lines.append("DESCRIPTIVE STATISTICS")
        lines.append("-" * 40)
        
        for unit_type in df['unit_type'].unique():
            unit_data = df[df['unit_type'] == unit_type]['team_b_casualties']
            desc = self.stat_analyzer.descriptive_stats(unit_data.values)
            
            lines.extend([
                f"\n{unit_type}:",
                f"  N observations: {desc.n}",
                f"  Mean ± SD: {desc.mean:.2f} ± {desc.std:.2f}",
                f"  95% CI: [{desc.ci_lower:.2f}, {desc.ci_upper:.2f}]",
                f"  Median [IQR]: {desc.median:.2f} [{desc.q1:.2f}, {desc.q3:.2f}]",
                f"  Range: [{desc.min_val:.2f}, {desc.max_val:.2f}]",
            ])
        
        # Lanchester Law tests
        lines.extend([
            "",
            "",
            "LANCHESTER'S LAW ANALYSIS",
            "-" * 40,
        ])
        
        lanchester_results = self.lanchester.test_lanchester_law(data)
        for unit_type, result in lanchester_results.items():
            matches = "✓" if result['matches_theory'] else "✗"
            lines.extend([
                f"\n{unit_type}:",
                f"  Expected: {result['expected_law']}",
                f"  Observed: {result['actual_law']}",
                f"  Best fit: {result['best_fit']} (R² = {result['best_r2']:.4f})",
                f"  Matches theory: {matches}",
                f"  Linear R²: {result['r2_linear']:.4f}",
                f"  Quadratic R²: {result['r2_quadratic']:.4f}",
            ])
        
        # Statistical comparisons
        if len(df['unit_type'].unique()) >= 2:
            lines.extend([
                "",
                "",
                "STATISTICAL COMPARISONS",
                "-" * 40,
            ])
            
            comparison = self.lanchester.compare_unit_types(data)
            
            if 'pairwise_comparisons' in comparison:
                for comp in comparison['pairwise_comparisons']:
                    sig = "**" if comp['significant'] else ""
                    lines.extend([
                        f"\n{comp['comparison']}:{sig}",
                        f"  t = {comp['t_statistic']:.3f}, p = {comp['p_value']:.4f}",
                        f"  Effect size (d): {comp['effect_size']:.3f}",
                        f"  {comp['interpretation']}",
                    ])
            
            if 'anova' in comparison:
                anova = comparison['anova']
                lines.extend([
                    "",
                    "ANOVA (all groups):",
                    f"  F = {anova['f_statistic']:.3f}, p = {anova['p_value']:.4f}",
                    f"  Effect size (η²): {anova['eta_squared']:.3f}",
                    f"  {anova['interpretation']}",
                ])
        
        lines.extend([
            "",
            "=" * 70,
            "END OF REPORT",
            "=" * 70,
        ])
        
        return "\n".join(lines)


# =============================================================================
# REGISTRY
# =============================================================================

ADVANCED_PLOTTERS = {
    'HeatmapPlotter': HeatmapPlotter,
    'DistributionPlotter': DistributionPlotter,
    'BarPlotter': BarPlotter,
    'StatisticalPlotter': StatisticalPlotter,
    'AnalysisDashboard': AnalysisDashboard,
}
