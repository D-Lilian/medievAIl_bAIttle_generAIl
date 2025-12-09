# -*- coding: utf-8 -*-
"""
@file lanchester_plotter.py
@brief Lanchester Plotter - Visualization for Lanchester's Laws experiments

@details
Creates visualizations specifically designed to analyze Lanchester's Laws:
- Casualties vs N curves for different unit types
- Comparison of Linear Law (melee) vs Square Law (ranged)
- Statistical analysis of results

Supports multiple output formats:
- matplotlib static plots
- plotly interactive plots
- markdown reports with embedded images

"""
import sys
import os
from typing import List, Dict, Any, Tuple
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Analysis.base_plotter import BasePlotter
from Model.scenarios.base_scenario import BattleResult


class LanchesterPlotter(BasePlotter):
    """
    @brief Plotter for Lanchester's Laws experiments
    
    @details Creates visualizations showing:
    - X-axis: N (base number of units)
    - Y-axis: Casualties sustained by winning side (Team B)
    - Multiple curves for different unit types
    
    Expected behavior based on Lanchester's Laws:
    - Melee (Knight): Linear relationship (Linear Law)
    - Ranged (Crossbowman): Quadratic relationship (Square Law)
    """
    
    def __init__(self, results: List[BattleResult] = None, output_dir: str = "Reports"):
        """
        @brief Initialize the Lanchester plotter
        
        @param results List of BattleResult objects (optional)
        @param output_dir Directory for output files
        """
        super().__init__(output_dir)
        if results:
            self.load_results(results)
    
    @property
    def name(self) -> str:
        return "Lanchester's Laws Analysis"
    
    def _prepare_data(self) -> Dict[str, Dict[int, List[float]]]:
        """
        @brief Prepare data grouped by unit type and N
        
        @return Dict[unit_type -> Dict[n -> List[casualties]]]
        """
        data: Dict[str, Dict[int, List[float]]] = {}
        
        for result in self.results:
            unit_type = result.parameters.get('unit_type', 'unknown')
            n = result.parameters.get('n', 0)
            
            if unit_type not in data:
                data[unit_type] = {}
            if n not in data[unit_type]:
                data[unit_type][n] = []
            
            # We track casualties of the winning side (Team B with 2N units)
            data[unit_type][n].append(result.team_b_casualties)
        
        return data
    
    def _aggregate_data(self, data: Dict[str, Dict[int, List[float]]]) -> Dict[str, Tuple[List[int], List[float], List[float]]]:
        """
        @brief Aggregate data to get mean and std per N
        
        @param data Raw data from _prepare_data
        @return Dict[unit_type -> (n_values, mean_casualties, std_casualties)]
        """
        import statistics
        
        aggregated = {}
        
        for unit_type, n_data in data.items():
            n_values = sorted(n_data.keys())
            means = []
            stds = []
            
            for n in n_values:
                casualties = n_data[n]
                means.append(statistics.mean(casualties))
                stds.append(statistics.stdev(casualties) if len(casualties) > 1 else 0)
            
            aggregated[unit_type] = (n_values, means, stds)
        
        return aggregated
    
    def plot(self, show: bool = True, **kwargs) -> Any:
        """
        @brief Create matplotlib visualization
        
        @param show If True, display the plot
        @param kwargs Additional matplotlib options
        @return matplotlib Figure object
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError("matplotlib is required for plotting. Install with: pip install matplotlib")
        
        data = self._prepare_data()
        aggregated = self._aggregate_data(data)
        
        # Create figure with multiple subplots
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Colors for unit types
        colors = {
            'Knight': '#2980b9',
            'Crossbowman': '#c0392b',
            'Pikeman': '#27ae60',
            'melee': '#2980b9',
            'ranged': '#c0392b',
        }
        
        # Plot 1: Casualties vs N
        ax1 = axes[0]
        for unit_type, (n_values, means, stds) in aggregated.items():
            color = colors.get(unit_type, '#7f8c8d')
            ax1.errorbar(n_values, means, yerr=stds, label=unit_type, 
                        color=color, marker='o', capsize=3, linewidth=2)
        
        ax1.set_xlabel('N (Base Unit Count)', fontsize=12)
        ax1.set_ylabel('Team B Casualties (2N army)', fontsize=12)
        ax1.set_title("Lanchester's Laws: Casualties vs Army Size", fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Casualty Rate vs N (normalized)
        ax2 = axes[1]
        for unit_type, (n_values, means, stds) in aggregated.items():
            color = colors.get(unit_type, '#7f8c8d')
            # Normalize by 2N (Team B initial size)
            casualty_rates = [m / (2 * n) * 100 for m, n in zip(means, n_values)]
            ax2.plot(n_values, casualty_rates, label=unit_type, 
                    color=color, marker='s', linewidth=2)
        
        ax2.set_xlabel('N (Base Unit Count)', fontsize=12)
        ax2.set_ylabel('Team B Casualty Rate (%)', fontsize=12)
        ax2.set_title('Casualty Rate vs Army Size', fontsize=14)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if show:
            plt.show()
        
        return fig
    
    def plot_interactive(self, **kwargs) -> Any:
        """
        @brief Create interactive plotly visualization
        
        @param kwargs Additional plotly options
        @return plotly Figure object
        """
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
        except ImportError:
            raise ImportError("plotly is required for interactive plots. Install with: pip install plotly")
        
        data = self._prepare_data()
        aggregated = self._aggregate_data(data)
        
        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Casualties vs Army Size", "Casualty Rate vs Army Size")
        )
        
        colors = {
            'Knight': '#2980b9',
            'Crossbowman': '#c0392b',
            'Pikeman': '#27ae60',
            'melee': '#2980b9',
            'ranged': '#c0392b',
        }
        
        for unit_type, (n_values, means, stds) in aggregated.items():
            color = colors.get(unit_type, '#7f8c8d')
            
            # Plot 1: Casualties
            fig.add_trace(
                go.Scatter(
                    x=n_values, y=means,
                    mode='lines+markers',
                    name=unit_type,
                    line=dict(color=color, width=2),
                    error_y=dict(type='data', array=stds, visible=True)
                ),
                row=1, col=1
            )
            
            # Plot 2: Casualty Rate
            casualty_rates = [m / (2 * n) * 100 for m, n in zip(means, n_values)]
            fig.add_trace(
                go.Scatter(
                    x=n_values, y=casualty_rates,
                    mode='lines+markers',
                    name=unit_type,
                    line=dict(color=color, width=2),
                    showlegend=False
                ),
                row=1, col=2
            )
        
        fig.update_xaxes(title_text="N (Base Unit Count)", row=1, col=1)
        fig.update_xaxes(title_text="N (Base Unit Count)", row=1, col=2)
        fig.update_yaxes(title_text="Team B Casualties", row=1, col=1)
        fig.update_yaxes(title_text="Casualty Rate (%)", row=1, col=2)
        
        fig.update_layout(
            title="Lanchester's Laws Analysis",
            height=500,
            width=1100
        )
        
        return fig
    
    def save(self, filename: str = "lanchester_plot.png", **kwargs) -> str:
        """
        @brief Save the plot to a file
        
        @param filename Output filename (supports .png, .pdf, .svg, .html)
        @param kwargs Additional options
        @return Path to saved file
        """
        filepath = self.output_dir / filename
        
        if filename.endswith('.html'):
            # Save interactive plot
            fig = self.plot_interactive(**kwargs)
            fig.write_html(str(filepath))
        else:
            # Save static plot
            import matplotlib.pyplot as plt
            fig = self.plot(show=False, **kwargs)
            fig.savefig(str(filepath), dpi=150, bbox_inches='tight')
            plt.close(fig)
        
        return str(filepath)
    
    def to_markdown(self, filename: str = "lanchester_report.md", 
                    include_plot: bool = True) -> str:
        """
        @brief Generate comprehensive markdown report
        
        @param filename Output filename
        @param include_plot If True, generate and embed plot
        @return Path to saved file
        """
        filepath = self.output_dir / filename
        
        # Generate plot if requested
        plot_path = None
        if include_plot and self.results:
            plot_filename = filename.replace('.md', '_plot.png')
            plot_path = self.save(plot_filename)
        
        md = "# Lanchester's Laws Analysis Report\n\n"
        md += "## Background\n\n"
        md += "**Lanchester's Laws** describe the relationship between army size and casualties:\n\n"
        md += "- **Linear Law (Melee)**: In melee combat, casualties are proportional to the ratio of forces.\n"
        md += "- **Square Law (Ranged)**: In ranged combat, effectiveness scales with the square of the number of units.\n\n"
        md += "This experiment pits N units against 2N units to observe these relationships.\n\n"
        
        if plot_path:
            # Use relative path for the image
            plot_rel = Path(plot_path).name
            md += f"## Results Visualization\n\n![Lanchester Plot]({plot_rel})\n\n"
        
        # Summary by unit type
        md += "## Summary by Unit Type\n\n"
        md += self._generate_lanchester_summary()
        
        # Analysis
        md += "\n## Analysis\n\n"
        md += self._generate_analysis()
        
        # Raw data
        md += "\n## Raw Data (Sample)\n\n"
        md += self._generate_results_table()
        
        with open(filepath, 'w') as f:
            f.write(md)
        
        return str(filepath)
    
    def _generate_lanchester_summary(self) -> str:
        """Generate summary table for Lanchester analysis"""
        data = self._prepare_data()
        aggregated = self._aggregate_data(data)
        
        md = "| Unit Type | N Range | Avg Casualties (min-max N) | Trend |\n"
        md += "|-----------|---------|---------------------------|-------|\n"
        
        for unit_type, (n_values, means, stds) in aggregated.items():
            n_range = f"{min(n_values)}-{max(n_values)}"
            cas_range = f"{means[0]:.1f} - {means[-1]:.1f}"
            
            # Estimate trend (linear vs quadratic)
            if len(n_values) > 2:
                # Simple check: if casualties grow faster than linearly
                ratio = means[-1] / means[0] if means[0] > 0 else 1
                n_ratio = n_values[-1] / n_values[0]
                if ratio > n_ratio * 1.5:
                    trend = "Quadratic (Square Law)"
                else:
                    trend = "Linear (Linear Law)"
            else:
                trend = "Insufficient data"
            
            md += f"| {unit_type} | {n_range} | {cas_range} | {trend} |\n"
        
        return md
    
    def _generate_analysis(self) -> str:
        """Generate analysis text"""
        if not self.results:
            return "No data available for analysis.\n"
        
        data = self._prepare_data()
        
        md = ""
        for unit_type in data.keys():
            md += f"### {unit_type}\n\n"
            
            if unit_type in ['Knight', 'melee', 'Pikeman']:
                md += "Expected behavior: **Linear Law** (melee combat)\n"
                md += "- Casualties should scale approximately linearly with N\n"
                md += "- The larger army's advantage is proportional to the size difference\n\n"
            elif unit_type in ['Crossbowman', 'ranged', 'archer']:
                md += "Expected behavior: **Square Law** (ranged combat)\n"
                md += "- Casualties should scale approximately with N²\n"
                md += "- Concentration of fire amplifies the larger army's advantage\n\n"
        
        return md


if __name__ == "__main__":
    # Demo with sample data
    print("Lanchester Plotter Demo")
    print("Run the LanchesterExperiment first to generate data.")
