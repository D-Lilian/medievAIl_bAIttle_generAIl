# -*- coding: utf-8 -*-
"""
@file visualizers.py
@brief Essential Data Visualizations for Battle Analysis

@details
Streamlined visualizations using plotnine (ggplot2):
- Correlation heatmap
- Boxplot comparison
- Mean comparison with CI

Follows KISS principle - only essential, non-redundant visualizations.
"""

import os
import warnings
from typing import Dict
from datetime import datetime

import pandas as pd
import numpy as np

try:
    from plotnine import (
        ggplot, aes,
        geom_tile, geom_text, geom_boxplot,
        geom_point, geom_errorbar,
        labs, theme, theme_minimal,
        element_text, element_blank, element_line,
        scale_fill_gradient2, scale_fill_brewer,
        coord_fixed,
    )
    PLOTNINE_AVAILABLE = True
except ImportError:
    PLOTNINE_AVAILABLE = False

from Plotting.data import PlotData
from Analysis.statistical import (
    StatisticalAnalyzer, LanchesterAnalyzer, 
    create_analysis_dataframe, DescriptiveStats
)


def theme_publication():
    """Clean publication-ready theme."""
    return (
        theme_minimal() +
        theme(
            plot_title=element_text(size=14, face='bold', ha='center'),
            plot_subtitle=element_text(size=11, color='#555555', ha='center'),
            axis_title=element_text(size=11, face='bold'),
            axis_text=element_text(size=10),
            axis_text_x=element_text(angle=45, ha='right'),
            legend_title=element_text(size=10, face='bold'),
            panel_grid_major=element_line(color='#E5E5E5', size=0.4),
            panel_grid_minor=element_blank(),
            figure_size=(10, 7),
            dpi=150
        )
    )


class HeatmapPlotter:
    """Creates correlation heatmaps."""
    
    def __init__(self, output_dir: str = "Reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _generate_filename(self, prefix: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"{prefix}_{timestamp}.png")
    
    def correlation_heatmap(self, df: pd.DataFrame, 
                           title: str = "Correlation Matrix") -> str:
        """
        Create a correlation heatmap.
        
        @param df: DataFrame with numeric columns
        @param title: Plot title
        @return: Path to saved plot
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        corr_matrix = df[numeric_cols].corr()
        
        corr_long = corr_matrix.reset_index().melt(
            id_vars='index', var_name='variable', value_name='correlation'
        )
        corr_long.columns = ['var1', 'var2', 'correlation']
        corr_long['label'] = corr_long['correlation'].round(2).astype(str)
        
        p = (
            ggplot(corr_long, aes(x='var1', y='var2', fill='correlation')) +
            geom_tile(color='white', size=0.5) +
            geom_text(aes(label='label'), size=8, color='black') +
            scale_fill_gradient2(
                low='#D73027', mid='#FFFFBF', high='#1A9850',
                midpoint=0, limits=(-1, 1), name='r'
            ) +
            labs(title=title, x="", y="") +
            theme_publication() +
            coord_fixed()
        )
        
        filepath = self._generate_filename("correlation_heatmap")
        p.save(filepath, width=10, height=8, dpi=150, verbose=False)
        return filepath


class DistributionPlotter:
    """Creates boxplot visualizations."""
    
    def __init__(self, output_dir: str = "Reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _generate_filename(self, prefix: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"{prefix}_{timestamp}.png")
    
    def boxplot_comparison(self, df: pd.DataFrame, 
                          x_var: str, y_var: str,
                          title: str = "Distribution Comparison") -> str:
        """
        Create boxplots for group comparison.
        
        @param df: DataFrame
        @param x_var: Categorical variable for x-axis
        @param y_var: Numeric variable for y-axis
        @param title: Plot title
        @return: Path to saved plot
        """
        p = (
            ggplot(df, aes(x=x_var, y=y_var, fill=x_var)) +
            geom_boxplot(alpha=0.7, outlier_alpha=0.5) +
            scale_fill_brewer(type='qual', palette='Set2') +
            labs(
                title=title,
                x=x_var.replace('_', ' ').title(),
                y=y_var.replace('_', ' ').title()
            ) +
            theme_publication() +
            theme(legend_position='none')
        )
        
        filepath = self._generate_filename("boxplot")
        p.save(filepath, width=10, height=7, dpi=150, verbose=False)
        return filepath


class StatisticalPlotter:
    """Creates mean comparison plots with CI."""
    
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
        stats_list = []
        for group in df[x_var].unique():
            group_data = df[df[x_var] == group][y_var].dropna()
            desc = self.stat_analyzer.descriptive_stats(group_data.values)
            stats_list.append({
                x_var: group,
                'mean': desc.mean,
                'ci_lower': desc.ci_lower,
                'ci_upper': desc.ci_upper,
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


class AnalysisDashboard:
    """
    Generates essential analysis visualizations.
    
    Produces 3 core plots:
    1. Correlation heatmap
    2. Boxplot by unit type
    3. Mean comparison with CI
    """
    
    def __init__(self, output_dir: str = "Reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.heatmap = HeatmapPlotter(output_dir)
        self.distribution = DistributionPlotter(output_dir)
        self.statistical = StatisticalPlotter(output_dir)
        self.lanchester = LanchesterAnalyzer()
    
    def generate_lanchester_dashboard(self, data: Dict[str, PlotData]) -> Dict[str, str]:
        """
        Generate essential Lanchester analysis plots.
        
        @param data: Dictionary of PlotData per unit type
        @return: Dictionary of generated file paths
        """
        warnings.filterwarnings('ignore')
        
        df = create_analysis_dataframe(data)
        if df.empty:
            return {"error": "No data available"}
        
        generated = {}
        
        # 1. Correlation heatmap
        try:
            generated['correlation_heatmap'] = self.heatmap.correlation_heatmap(
                df, title="Battle Metrics Correlation"
            )
        except Exception as e:
            generated['correlation_heatmap'] = f"Error: {e}"
        
        # 2. Boxplot: Casualties by unit type
        try:
            generated['boxplot'] = self.distribution.boxplot_comparison(
                df, x_var='unit_type', y_var='team_b_casualties',
                title="Winner Casualties by Unit Type"
            )
        except Exception as e:
            generated['boxplot'] = f"Error: {e}"
        
        # 3. Mean comparison with CI
        try:
            generated['mean_comparison'] = self.statistical.mean_comparison_plot(
                df, x_var='unit_type', y_var='team_b_casualties',
                title="Mean Casualties with 95% CI"
            )
        except Exception as e:
            generated['mean_comparison'] = f"Error: {e}"
        
        return generated


# Exports
VISUALIZERS = {
    'HeatmapPlotter': HeatmapPlotter,
    'DistributionPlotter': DistributionPlotter,
    'StatisticalPlotter': StatisticalPlotter,
    'AnalysisDashboard': AnalysisDashboard,
}
