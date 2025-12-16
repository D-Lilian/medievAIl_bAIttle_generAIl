# -*- coding: utf-8 -*-
"""
@file report.py
@brief Markdown Report Generator for Plot Analysis

@details
Generates comprehensive markdown reports from simulation data collected
by the DataCollector. Provides statistical summaries and data tables.

Part of the Plotting module.
"""

import os
from datetime import datetime
from typing import Dict, Any

from Plotting.data import PlotData


class PlotReportGenerator:
    """
    Generates markdown reports for plot analysis.
    
    Creates reports with:
    - Configuration summary
    - Statistical analysis
    - Data tables per unit type
    - Lanchester's Laws interpretation
    """
    
    def __init__(self, output_dir: str = "Reports"):
        """
        Initialize the report generator.
        
        @param output_dir: Directory to save reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, data, plot_path: str) -> str:
        """
        Generate a markdown report from collected data.
        
        @param data: CollectedData from DataCollector
        @param plot_path: Path to the generated plot image
        @return: Path to the generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(
            self.output_dir, 
            f"{data.scenario_name}_report_{timestamp}.md"
        )
        
        content = self._generate_content(data, plot_path)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return report_path
    
    def _generate_content(self, data, plot_path: str) -> str:
        """Generate the markdown content."""
        lines = []
        
        # Header
        lines.extend([
            f"# {data.scenario_name} Analysis Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## Configuration",
            "",
            f"| Parameter | Value |",
            f"|-----------|-------|",
            f"| AI | {data.ai_name} |",
            f"| Scenario | {data.scenario_name} |",
            f"| Unit Types | {', '.join(data.unit_types)} |",
            f"| N Range | {data.n_range[0]} to {data.n_range[-1]} ({len(data.n_range)} values) |",
            f"| Repetitions | {data.num_repetitions} per configuration |",
            f"| Total Simulations | {len(data.unit_types) * len(data.n_range) * data.num_repetitions} |",
            "",
            "---",
            "",
            "## Lanchester's Laws",
            "",
            "This analysis tests Lanchester's Laws of combat:",
            "",
            "- **Linear Law (Melee):** In melee combat, casualties are proportional to N. ",
            "  Each soldier can only engage one enemy at a time.",
            "",
            "- **Square Law (Ranged):** In ranged combat, effectiveness scales with N². ",
            "  Multiple soldiers can focus fire on the same target.",
            "",
            "### Scenario: N vs 2N",
            "",
            "The Lanchester scenario pits N units (Team A) against 2N units (Team B).",
            "The larger army (2N) should win every time, but what's interesting is:",
            "",
            "- How many casualties does the winning side (2N) sustain?",
            "- Does casualty scaling differ between melee and ranged units?",
            "",
            "---",
            "",
        ])
        
        # Results per unit type
        lines.append("## Results by Unit Type")
        lines.append("")
        
        for unit_type in data.unit_types:
            plot_data = data.plot_data.get(unit_type)
            if not plot_data:
                continue
            
            lines.extend([
                f"### {unit_type}",
                "",
                self._get_unit_type_analysis(unit_type),
                "",
                "#### Data Table",
                "",
                "| N | Team A (N) | Team B (2N) | A Casualties | B Casualties | B Win Rate | Duration |",
                "|---|------------|-------------|--------------|--------------|------------|----------|",
            ])
            
            for i, n in enumerate(plot_data.n_values):
                if i >= len(plot_data.avg_team_a_casualties):
                    break
                    
                a_cas = plot_data.avg_team_a_casualties[i]
                b_cas = plot_data.avg_team_b_casualties[i]
                b_win = plot_data.team_b_win_rates[i] * 100
                ticks = plot_data.avg_ticks[i] if i < len(plot_data.avg_ticks) else 0
                
                lines.append(
                    f"| {n} | {n} units | {2*n} units | "
                    f"{a_cas:.1f} | {b_cas:.1f} | {b_win:.0f}% | {ticks:.0f} ticks |"
                )
            
            lines.extend(["", ""])
        
        # Summary statistics
        lines.extend([
            "---",
            "",
            "## Summary Statistics",
            "",
        ])
        
        for unit_type in data.unit_types:
            plot_data = data.plot_data.get(unit_type)
            if not plot_data or not plot_data.avg_team_b_casualties:
                continue
            
            avg_b_win = sum(plot_data.team_b_win_rates) / len(plot_data.team_b_win_rates) * 100
            avg_b_cas = sum(plot_data.avg_team_b_casualties) / len(plot_data.avg_team_b_casualties)
            max_b_cas = max(plot_data.avg_team_b_casualties)
            min_b_cas = min(plot_data.avg_team_b_casualties)
            
            lines.extend([
                f"### {unit_type}",
                "",
                f"- **Average 2N Win Rate:** {avg_b_win:.1f}%",
                f"- **Average 2N Casualties:** {avg_b_cas:.1f}",
                f"- **Min/Max 2N Casualties:** {min_b_cas:.1f} / {max_b_cas:.1f}",
                "",
            ])
        
        # Visualization
        plot_filename = os.path.basename(plot_path)
        lines.extend([
            "---",
            "",
            "## Visualization",
            "",
            f"![{data.scenario_name} Analysis](./{plot_filename})",
            "",
            "---",
            "",
            "## Interpretation",
            "",
        ])
        
        # Analysis based on unit types
        if 'Knight' in data.unit_types and 'Crossbowman' in data.unit_types:
            lines.extend([
                "### Comparing Melee vs Ranged",
                "",
                "- **Knights (Melee):** Should follow Linear Law - casualties scale linearly with N",
                "- **Crossbowmen (Ranged):** Should follow Square Law - casualties scale with N²",
                "",
                "The graph should show different curve shapes for each unit type, ",
                "demonstrating the fundamental difference between ancient/melee and modern/ranged combat.",
                "",
            ])
        
        lines.extend([
            "---",
            "",
            "*Report generated by MedievAIl bAIttle generAIl*",
            "",
        ])
        
        return "\n".join(lines)
    
    def _get_unit_type_analysis(self, unit_type: str) -> str:
        """Get unit-specific analysis text."""
        analyses = {
            'Knight': (
                "Knights are melee units. According to Lanchester's Linear Law, "
                "in melee combat each soldier can only engage one enemy at a time, "
                "so the advantage of larger numbers scales linearly."
            ),
            'Crossbowman': (
                "Crossbowmen are ranged units. According to Lanchester's Square Law, "
                "in ranged combat multiple soldiers can focus fire on the same target, "
                "so the advantage of larger numbers scales quadratically."
            ),
            'Pikeman': (
                "Pikemen are melee units with extended reach. They should generally "
                "follow Lanchester's Linear Law, though their formation mechanics "
                "may introduce some variation."
            ),
        }
        return analyses.get(unit_type, f"Analysis for {unit_type} unit type.")
