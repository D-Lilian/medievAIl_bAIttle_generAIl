# -*- coding: utf-8 -*-
"""
@file scenario_plotters.py
@brief Scenario-Specific Plotters - One plotter per predefined scenario

@details
Each predefined scenario has its own plotter with relevant visualizations:
- Lanchester: N vs 2N analysis (Linear vs Square Law)
- ClassicMedieval: Formation effectiveness comparison
- CavalryCharge: Charge impact analysis
- DefensiveSiege: Defensive position analysis
- CannaeEnvelopment: Flanking maneuver effectiveness
- RomanLegion: Testudo formation analysis
- BritishSquare: Anti-cavalry formation analysis

Follows Single Responsibility Principle - each plotter handles one scenario type.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, List
from datetime import datetime

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    np = None

from Plotting.data import PlotData
from Plotting.base import BasePlotter


class ScenarioPlotter(BasePlotter):
    """
    Base class for scenario-specific plotters.
    
    Provides common functionality for all scenario plotters.
    """
    
    SCENARIO_NAME = "Generic"
    SCENARIO_DESCRIPTION = "Generic battle scenario"
    
    def _create_figure(self, nrows: int = 2, ncols: int = 2, 
                       figsize: tuple = (14, 10)) -> tuple:
        """Create figure with subplots and main title."""
        self._setup_style()
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
        fig.suptitle(f"{self.SCENARIO_NAME} Analysis", fontsize=16, fontweight='bold')
        return fig, axes
    
    def _get_colors_markers(self) -> tuple:
        """Return standard colors and markers."""
        colors = ['#e74c3c', '#3498db', '#27ae60', '#9b59b6', '#f39c12', '#1abc9c']
        markers = ['o', 's', '^', 'D', 'v', 'p']
        return colors, markers


# =============================================================================
# LANCHESTER SCENARIO PLOTTER
# =============================================================================

class PlotLanchester(ScenarioPlotter):
    """
    Plotter for Lanchester's Laws analysis.
    
    Scenario: N units (Team A) vs 2N units (Team B)
    Key insight: How casualties scale with N for melee vs ranged units.
    
    Lanchester's Laws:
    - Linear Law (melee): Each soldier engages one enemy, casualties ~ N
    - Square Law (ranged): Focus fire possible, casualties ~ N²
    """
    
    SCENARIO_NAME = "Lanchester's Laws"
    SCENARIO_DESCRIPTION = "N vs 2N asymmetric battle to test combat laws"
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        """Generate Lanchester analysis with 4 panels."""
        fig, axes = self._create_figure()
        colors, markers = self._get_colors_markers()
        
        # Main plot: Winner (2N) Casualties vs N
        ax1 = axes[0, 0]
        for i, (unit_type, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.avg_winner_casualties:
                ax1.plot(
                    plot_data.n_values, plot_data.avg_winner_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=unit_type, linewidth=2.5, markersize=7
                )
        ax1.set_xlabel('N (smaller army)')
        ax1.set_ylabel('Winner (2N) Casualties')
        ax1.set_title('Key: Winner Casualties vs Army Size')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Win rate (should be 100% for 2N)
        ax2 = axes[0, 1]
        for i, (unit_type, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.team_b_win_rates:
                ax2.plot(
                    plot_data.n_values,
                    [r * 100 for r in plot_data.team_b_win_rates],
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=unit_type, linewidth=2, markersize=6
                )
        ax2.set_xlabel('N')
        ax2.set_ylabel('Win Rate (%)')
        ax2.set_title('Larger Army (2N) Win Rate')
        ax2.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 105)
        
        # Battle duration
        ax3 = axes[1, 0]
        for i, (unit_type, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.avg_ticks:
                ax3.plot(
                    plot_data.n_values, plot_data.avg_ticks,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=unit_type, linewidth=2, markersize=6
                )
        ax3.set_xlabel('N')
        ax3.set_ylabel('Duration (ticks)')
        ax3.set_title('Battle Duration')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Both teams casualties
        ax4 = axes[1, 1]
        for i, (unit_type, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax4.plot(
                    plot_data.n_values, plot_data.avg_team_a_casualties,
                    color=colors[i % len(colors)], label=f'{unit_type} (N)',
                    linewidth=2, linestyle='-'
                )
                ax4.plot(
                    plot_data.n_values, plot_data.avg_team_b_casualties,
                    color=colors[i % len(colors)], label=f'{unit_type} (2N)',
                    linewidth=2, linestyle='--'
                )
        ax4.set_xlabel('N')
        ax4.set_ylabel('Casualties')
        ax4.set_title('Casualties by Team')
        ax4.legend(fontsize=8, ncol=2)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filepath = self._generate_filename("lanchester_analysis")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        return filepath


# =============================================================================
# CLASSIC MEDIEVAL BATTLE PLOTTER
# =============================================================================

class PlotClassicMedieval(ScenarioPlotter):
    """
    Plotter for Classic Medieval Battle (100v100, Agincourt style).
    
    Analyzes symmetric battles with classic medieval formations.
    Focus: Unit composition effectiveness, formation impact.
    """
    
    SCENARIO_NAME = "Classic Medieval Battle"
    SCENARIO_DESCRIPTION = "100v100 symmetric battle with medieval formations"
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        """Generate classic battle analysis."""
        fig, axes = self._create_figure()
        colors, markers = self._get_colors_markers()
        
        # Win rates comparison
        ax1 = axes[0, 0]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.team_a_win_rates:
                ax1.plot(
                    plot_data.n_values,
                    [r * 100 for r in plot_data.team_a_win_rates],
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax1.set_xlabel('Configuration')
        ax1.set_ylabel('Win Rate (%)')
        ax1.set_title('Win Rate by Configuration')
        ax1.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50% baseline')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Casualties comparison
        ax2 = axes[0, 1]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax2.plot(
                    plot_data.n_values, plot_data.avg_team_a_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=f'{config} - A', linewidth=2
                )
                ax2.plot(
                    plot_data.n_values, plot_data.avg_team_b_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=f'{config} - B', linewidth=2, linestyle='--'
                )
        ax2.set_xlabel('Configuration')
        ax2.set_ylabel('Casualties')
        ax2.set_title('Casualties by Team')
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        
        # Survivors
        ax3 = axes[1, 0]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax3.plot(
                    plot_data.n_values, plot_data.avg_team_a_survivors,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2
                )
        ax3.set_xlabel('Configuration')
        ax3.set_ylabel('Survivors')
        ax3.set_title('Team A Survivors')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Duration
        ax4 = axes[1, 1]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.avg_ticks:
                ax4.plot(
                    plot_data.n_values, plot_data.avg_ticks,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax4.set_xlabel('Configuration')
        ax4.set_ylabel('Duration (ticks)')
        ax4.set_title('Battle Duration')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filepath = self._generate_filename("classic_medieval_analysis")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        return filepath


# =============================================================================
# CAVALRY CHARGE PLOTTER
# =============================================================================

class PlotCavalryCharge(ScenarioPlotter):
    """
    Plotter for Cavalry Charge scenario (150v150, offensive wedge).
    
    Analyzes charge effectiveness and impact damage.
    Focus: Initial charge damage, pursuit phase, cavalry vs infantry.
    """
    
    SCENARIO_NAME = "Cavalry Charge"
    SCENARIO_DESCRIPTION = "150v150 offensive wedge formation"
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        """Generate cavalry charge analysis."""
        fig, axes = self._create_figure()
        colors, markers = self._get_colors_markers()
        
        # Charge effectiveness (casualties inflicted)
        ax1 = axes[0, 0]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax1.plot(
                    plot_data.n_values, plot_data.avg_team_b_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2.5, markersize=7
                )
        ax1.set_xlabel('Cavalry Count')
        ax1.set_ylabel('Enemy Casualties')
        ax1.set_title('Charge Impact: Enemy Casualties')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Cavalry losses
        ax2 = axes[0, 1]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax2.plot(
                    plot_data.n_values, plot_data.avg_team_a_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax2.set_xlabel('Cavalry Count')
        ax2.set_ylabel('Cavalry Losses')
        ax2.set_title('Cavalry Casualties During Charge')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Kill/Death ratio
        ax3 = axes[1, 0]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                kd_ratio = []
                for j in range(len(plot_data.n_values)):
                    a_cas = plot_data.avg_team_a_casualties[j] if j < len(plot_data.avg_team_a_casualties) else 1
                    b_cas = plot_data.avg_team_b_casualties[j] if j < len(plot_data.avg_team_b_casualties) else 0
                    kd_ratio.append(b_cas / max(a_cas, 0.1))
                ax3.plot(
                    plot_data.n_values, kd_ratio,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax3.set_xlabel('Cavalry Count')
        ax3.set_ylabel('K/D Ratio')
        ax3.set_title('Kill/Death Ratio')
        ax3.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Win rate
        ax4 = axes[1, 1]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.team_a_win_rates:
                ax4.plot(
                    plot_data.n_values,
                    [r * 100 for r in plot_data.team_a_win_rates],
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax4.set_xlabel('Cavalry Count')
        ax4.set_ylabel('Win Rate (%)')
        ax4.set_title('Cavalry Victory Rate')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 105)
        
        plt.tight_layout()
        filepath = self._generate_filename("cavalry_charge_analysis")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        return filepath


# =============================================================================
# DEFENSIVE SIEGE PLOTTER
# =============================================================================

class PlotDefensiveSiege(ScenarioPlotter):
    """
    Plotter for Defensive Siege scenario (120v120, shield wall).
    
    Analyzes defensive formation effectiveness.
    Focus: Defender casualties, attacker break-through rate.
    """
    
    SCENARIO_NAME = "Defensive Siege"
    SCENARIO_DESCRIPTION = "120v120 shield wall defensive formation"
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        """Generate defensive siege analysis."""
        fig, axes = self._create_figure()
        colors, markers = self._get_colors_markers()
        
        # Defender survival
        ax1 = axes[0, 0]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax1.plot(
                    plot_data.n_values, plot_data.avg_team_a_survivors,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2.5, markersize=7
                )
        ax1.set_xlabel('Defender Count')
        ax1.set_ylabel('Survivors')
        ax1.set_title('Defender Survival')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Attacker casualties
        ax2 = axes[0, 1]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax2.plot(
                    plot_data.n_values, plot_data.avg_team_b_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax2.set_xlabel('Defender Count')
        ax2.set_ylabel('Attacker Casualties')
        ax2.set_title('Attackers Repelled')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Defense efficiency (attacker casualties / defender casualties)
        ax3 = axes[1, 0]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                efficiency = []
                for j in range(len(plot_data.n_values)):
                    a_cas = plot_data.avg_team_a_casualties[j] if j < len(plot_data.avg_team_a_casualties) else 1
                    b_cas = plot_data.avg_team_b_casualties[j] if j < len(plot_data.avg_team_b_casualties) else 0
                    efficiency.append(b_cas / max(a_cas, 0.1))
                ax3.plot(
                    plot_data.n_values, efficiency,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax3.set_xlabel('Defender Count')
        ax3.set_ylabel('Defense Efficiency')
        ax3.set_title('Defense Efficiency Ratio')
        ax3.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Defender win rate
        ax4 = axes[1, 1]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.team_a_win_rates:
                ax4.plot(
                    plot_data.n_values,
                    [r * 100 for r in plot_data.team_a_win_rates],
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax4.set_xlabel('Defender Count')
        ax4.set_ylabel('Win Rate (%)')
        ax4.set_title('Defender Victory Rate')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 105)
        
        plt.tight_layout()
        filepath = self._generate_filename("defensive_siege_analysis")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        return filepath


# =============================================================================
# CANNAE ENVELOPMENT PLOTTER
# =============================================================================

class PlotCannaeEnvelopment(ScenarioPlotter):
    """
    Plotter for Cannae Envelopment scenario (180v180, hammer & anvil).
    
    Analyzes flanking maneuver effectiveness.
    Focus: Encirclement success, pincer movement timing.
    """
    
    SCENARIO_NAME = "Cannae Envelopment"
    SCENARIO_DESCRIPTION = "180v180 hammer and anvil tactics"
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        """Generate Cannae envelopment analysis."""
        fig, axes = self._create_figure()
        colors, markers = self._get_colors_markers()
        
        # Encirclement success (enemy casualties)
        ax1 = axes[0, 0]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax1.plot(
                    plot_data.n_values, plot_data.avg_team_b_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2.5, markersize=7
                )
        ax1.set_xlabel('Flanking Force Size')
        ax1.set_ylabel('Enemy Casualties')
        ax1.set_title('Encirclement Effectiveness')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Own casualties
        ax2 = axes[0, 1]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax2.plot(
                    plot_data.n_values, plot_data.avg_team_a_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax2.set_xlabel('Flanking Force Size')
        ax2.set_ylabel('Own Casualties')
        ax2.set_title('Cost of Maneuver')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Battle duration (successful encirclement should be faster)
        ax3 = axes[1, 0]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.avg_ticks:
                ax3.plot(
                    plot_data.n_values, plot_data.avg_ticks,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax3.set_xlabel('Flanking Force Size')
        ax3.set_ylabel('Duration (ticks)')
        ax3.set_title('Time to Victory')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Win rate
        ax4 = axes[1, 1]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.team_a_win_rates:
                ax4.plot(
                    plot_data.n_values,
                    [r * 100 for r in plot_data.team_a_win_rates],
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax4.set_xlabel('Flanking Force Size')
        ax4.set_ylabel('Win Rate (%)')
        ax4.set_title('Encirclement Success Rate')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 105)
        
        plt.tight_layout()
        filepath = self._generate_filename("cannae_envelopment_analysis")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        return filepath


# =============================================================================
# ROMAN LEGION PLOTTER
# =============================================================================

class PlotRomanLegion(ScenarioPlotter):
    """
    Plotter for Roman Legion scenario (100v100, testudo formation).
    
    Analyzes testudo defensive formation against ranged attacks.
    Focus: Arrow damage mitigation, formation cohesion.
    """
    
    SCENARIO_NAME = "Roman Legion"
    SCENARIO_DESCRIPTION = "100v100 testudo formation tactics"
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        """Generate Roman Legion testudo analysis."""
        fig, axes = self._create_figure()
        colors, markers = self._get_colors_markers()
        
        # Formation survival
        ax1 = axes[0, 0]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax1.plot(
                    plot_data.n_values, plot_data.avg_team_a_survivors,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2.5, markersize=7
                )
        ax1.set_xlabel('Legion Size')
        ax1.set_ylabel('Survivors')
        ax1.set_title('Testudo Survival Rate')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Casualties comparison
        ax2 = axes[0, 1]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax2.plot(
                    plot_data.n_values, plot_data.avg_team_a_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=f'{config} (Legion)', linewidth=2
                )
                ax2.plot(
                    plot_data.n_values, plot_data.avg_team_b_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=f'{config} (Enemy)', linewidth=2, linestyle='--'
                )
        ax2.set_xlabel('Legion Size')
        ax2.set_ylabel('Casualties')
        ax2.set_title('Casualties Comparison')
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        
        # Duration
        ax3 = axes[1, 0]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.avg_ticks:
                ax3.plot(
                    plot_data.n_values, plot_data.avg_ticks,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax3.set_xlabel('Legion Size')
        ax3.set_ylabel('Duration (ticks)')
        ax3.set_title('Battle Duration')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Win rate
        ax4 = axes[1, 1]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.team_a_win_rates:
                ax4.plot(
                    plot_data.n_values,
                    [r * 100 for r in plot_data.team_a_win_rates],
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax4.set_xlabel('Legion Size')
        ax4.set_ylabel('Win Rate (%)')
        ax4.set_title('Legion Victory Rate')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 105)
        
        plt.tight_layout()
        filepath = self._generate_filename("roman_legion_analysis")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        return filepath


# =============================================================================
# BRITISH SQUARE PLOTTER
# =============================================================================

class PlotBritishSquare(ScenarioPlotter):
    """
    Plotter for British Square scenario (120v120, hollow square).
    
    Analyzes hollow square anti-cavalry formation.
    Focus: Defense against cavalry charges, formation integrity.
    """
    
    SCENARIO_NAME = "British Square"
    SCENARIO_DESCRIPTION = "120v120 hollow square anti-cavalry formation"
    
    def plot(self, data: Dict[str, PlotData], **kwargs) -> str:
        """Generate British Square anti-cavalry analysis."""
        fig, axes = self._create_figure()
        colors, markers = self._get_colors_markers()
        
        # Infantry survival against cavalry
        ax1 = axes[0, 0]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax1.plot(
                    plot_data.n_values, plot_data.avg_team_a_survivors,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2.5, markersize=7
                )
        ax1.set_xlabel('Square Size')
        ax1.set_ylabel('Infantry Survivors')
        ax1.set_title('Square Formation Survival')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Cavalry casualties (square should kill cavalry)
        ax2 = axes[0, 1]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ax2.plot(
                    plot_data.n_values, plot_data.avg_team_b_casualties,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax2.set_xlabel('Square Size')
        ax2.set_ylabel('Cavalry Casualties')
        ax2.set_title('Cavalry Repelled')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Defense ratio
        ax3 = axes[1, 0]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values:
                ratio = []
                for j in range(len(plot_data.n_values)):
                    a_cas = plot_data.avg_team_a_casualties[j] if j < len(plot_data.avg_team_a_casualties) else 1
                    b_cas = plot_data.avg_team_b_casualties[j] if j < len(plot_data.avg_team_b_casualties) else 0
                    ratio.append(b_cas / max(a_cas, 0.1))
                ax3.plot(
                    plot_data.n_values, ratio,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax3.set_xlabel('Square Size')
        ax3.set_ylabel('Kill Ratio')
        ax3.set_title('Anti-Cavalry Efficiency')
        ax3.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Win rate
        ax4 = axes[1, 1]
        for i, (config, plot_data) in enumerate(data.items()):
            if plot_data.n_values and plot_data.team_a_win_rates:
                ax4.plot(
                    plot_data.n_values,
                    [r * 100 for r in plot_data.team_a_win_rates],
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    label=config, linewidth=2, markersize=6
                )
        ax4.set_xlabel('Square Size')
        ax4.set_ylabel('Win Rate (%)')
        ax4.set_title('Square Victory Rate')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 105)
        
        plt.tight_layout()
        filepath = self._generate_filename("british_square_analysis")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        return filepath


# =============================================================================
# REGISTRY
# =============================================================================

# Map scenario names to their plotters
SCENARIO_PLOTTERS = {
    # Lanchester (special N vs 2N scenario)
    'Lanchester': PlotLanchester,
    'lanchester': PlotLanchester,
    
    # Predefined scenarios
    'classic_medieval_battle': PlotClassicMedieval,
    'ClassicMedieval': PlotClassicMedieval,
    'classic': PlotClassicMedieval,
    
    'cavalry_charge': PlotCavalryCharge,
    'CavalryCharge': PlotCavalryCharge,
    
    'defensive_siege': PlotDefensiveSiege,
    'DefensiveSiege': PlotDefensiveSiege,
    
    'cannae_envelopment': PlotCannaeEnvelopment,
    'CannaeEnvelopment': PlotCannaeEnvelopment,
    'cannae': PlotCannaeEnvelopment,
    
    'roman_legion': PlotRomanLegion,
    'RomanLegion': PlotRomanLegion,
    'testudo': PlotRomanLegion,
    
    'british_square': PlotBritishSquare,
    'BritishSquare': PlotBritishSquare,
    'hollow_square': PlotBritishSquare,
}


def get_scenario_plotter(scenario_name: str, output_dir: str = "Reports") -> ScenarioPlotter:
    """
    Get the appropriate plotter for a scenario.
    
    @param scenario_name: Name of the scenario
    @param output_dir: Output directory for plots
    @return: Plotter instance
    @raises ValueError: If scenario is unknown
    """
    if scenario_name not in SCENARIO_PLOTTERS:
        available = list(set(SCENARIO_PLOTTERS.values()))
        names = [p.SCENARIO_NAME for p in available]
        raise ValueError(f"Unknown scenario: {scenario_name}. Available: {names}")
    
    return SCENARIO_PLOTTERS[scenario_name](output_dir)
