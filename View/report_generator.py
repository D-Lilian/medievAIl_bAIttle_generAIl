# -*- coding: utf-8 -*-
"""
@file report_generator.py
@brief HTML battle report generation.

@details
Generates HTML battle reports from simulation data.
Follows Single Responsibility Principle: only handles report generation.
"""

import datetime
import os
import subprocess
import sys
import webbrowser
from typing import List, Dict

from View.data_types import Team, UnitRepr, UNIT_LETTERS
from View.stats import Stats


class ReportGenerator:
    """
    @brief Generates HTML battle reports.
    """

    def __init__(self, board_width: int, board_height: int):
        """
        @brief Initialize report generator.
        @param board_width Board width
        @param board_height Board height
        """
        self.board_width = board_width
        self.board_height = board_height

    def generate(self, units: List[UnitRepr], stats: Stats) -> None:
        """
        @brief Generate HTML battle report.
        @param units List of unit representations
        @param stats Statistics object
        """
        reports_dir = os.path.join(os.getcwd(), "Reports")
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(reports_dir, f"battle_report_{timestamp}.html")

        # Generate content
        team1 = [u for u in units if u.team == Team.A]
        team2 = [u for u in units if u.team == Team.B]

        # Build map of uid -> display_id (e.g. "#1")
        uid_display_map = {}
        for i, u in enumerate(team1, 1):
            uid_display_map[u.uid] = f"#{i}"
        for i, u in enumerate(team2, 1):
            uid_display_map[u.uid] = f"#{i}"

        team_sections = self._gen_team_section(1, team1, uid_display_map) + self._gen_team_section(2, team2, uid_display_map)
        battle_map = self._gen_battle_map(team1, team2)
        breakdown = self._gen_breakdown(stats)
        legend = self._gen_legend()

        # Load template and CSS
        base_dir = os.path.join(os.path.dirname(__file__), '..', 'Utils')
        with open(os.path.join(base_dir, 'battle_report_template.html'), 'r', encoding='utf-8') as f:
            template = f.read()
        
        with open(os.path.join(base_dir, 'battle_report.css'), 'r', encoding='utf-8') as f:
            css_content = f.read()

        # Fill template
        html = template.replace('{timestamp}', timestamp)
        html = html.replace('<link rel="stylesheet" href="battle_report.css">', f'<style>{css_content}</style>')
        html = html.replace('{simulation_time}', f"{stats.simulation_time:.2f}")
        html = html.replace('{team1_units}', f"{stats.team1_alive:.2f}")
        html = html.replace('{team2_units}', f"{stats.team2_alive:.2f}")
        html = html.replace('{total_units}', f"{len(units)}")
        html = html.replace('{team_sections}', team_sections)
        html = html.replace('{battle_map}', battle_map)
        html = html.replace('{breakdown_section}', breakdown)
        html = html.replace('{legend_items}', legend)
        html = html.replace('{generation_datetime}',
                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Write HTML file only (CSS is in Utils/)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)

        # Open the generated report in the user's default browser
        self._open_report(filename)

    def _open_report(self, filename: str) -> None:
        """
        @brief Open report in browser without terminal output.
        @param filename Path to HTML file
        """
        try:
            # Use platform-specific opener while silencing stdout/stderr
            if sys.platform.startswith('linux'):
                subprocess.Popen(['xdg-open', filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif os.name == 'nt':
                # Windows: os.startfile doesn't print to terminal
                os.startfile(filename)
            else:
                # Fallback to webbrowser (may print in some environments)
                webbrowser.open('file://' + os.path.abspath(filename))
        except Exception:
            # If anything fails, silently ignore — report file was created
            pass

    def _gen_unit_html(self, i: int, unit: UnitRepr, team: int, uid_map: Dict[int, str] = None) -> str:
        """
        @brief Generate HTML for single unit.
        @param i Unit index
        @param unit Unit representation
        @param team Team number
        @param uid_map Map of unit UIDs to display IDs
        @return HTML string
        """
        hp_pct = unit.hp_percent
        hp_class = "hp-critical" if hp_pct < 25 else "hp-low" if hp_pct < 50 else ""
        status = "Alive" if unit.alive else "Dead"
        uid = f"unit-{unit.uid}"

        # Helper for stats
        def format_val(val):
            if isinstance(val, float):
                return f"{val:.2f}"
            return val

        def format_dict(d):
            if not d:
                return "None"
            return "<br>".join(f"<b>{k}:</b> {format_val(v)}" for k, v in d.items())

        # Format target name with ID if available
        display_target = unit.target_name or 'None'
        if unit.target_uid is not None and uid_map and unit.target_uid in uid_map:
            # Insert ID before (Team X) or append it
            # unit.target_name is like "Pikeman (Team A)"
            # We want "Pikeman #3 (Team A)"
            if " (" in display_target:
                parts = display_target.split(" (", 1)
                display_target = f"{parts[0]} {uid_map[unit.target_uid]} ({parts[1]}"
            else:
                display_target = f"{display_target} {uid_map[unit.target_uid]}"

        return f'''
        <div class="unit team{team}" id="{uid}" data-unit-id="{uid}">
            <div class="unit-header">
                <span class="unit-id">#{i}</span>
                <span class="unit-type">{unit.type}</span>
                <span class="unit-status {status.lower()}">{status}</span>
            </div>
            <div class="hp-bar-container">
                <div class="hp-info">
                    <span class="hp-label">♥ Health</span>
                    <span class="hp-text">{format_val(unit.hp)}/{format_val(unit.hp_max)}</span>
                </div>
                <div class="hp-bar">
                    <div class="hp-fill {hp_class}" style="width: {hp_pct:.2f}%"></div>
                </div>
            </div>
            <div class="unit-stats-grid">
                <div class="stat-item">
                    <span class="stat-icon">⌖</span>
                    <span class="stat-content">
                        <span class="stat-label">Position</span>
                        <span class="stat-value">({format_val(unit.x)}, {format_val(unit.y)})</span>
                    </span>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">⚔</span>
                    <span class="stat-content">
                        <span class="stat-label">Damage</span>
                        <span class="stat-value">{format_val(unit.damage_dealt)}</span>
                    </span>
                </div>
                <div class="stat-item stat-item-full">
                    <span class="stat-icon">◎</span>
                    <span class="stat-content">
                        <span class="stat-label">Target</span>
                        <span class="stat-value">{display_target}</span>
                    </span>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">➤</span>
                    <span class="stat-content">
                        <span class="stat-label">Speed</span>
                        <span class="stat-value">{format_val(unit.speed)}</span>
                    </span>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">☈</span>
                    <span class="stat-content">
                        <span class="stat-label">Range</span>
                        <span class="stat-value">{format_val(unit.range)}</span>
                    </span>
                </div>
            </div>
        </div>'''

    def _gen_team_section(self, team: int, units: List[UnitRepr], uid_map: Dict[int, str] = None) -> str:
        """
        @brief Generate HTML for team section.
        @param team Team number
        @param units List of units
        @param uid_map Map of unit UIDs to display IDs
        @return HTML string
        """
        units_html = "".join(self._gen_unit_html(i, u, team, uid_map) for i, u in enumerate(units, 1))
        return f'''
        <div class="team-section">
            <details open>
                <summary>Team {team} - {len(units)} units</summary>
                <div class="unit-list">{units_html}</div>
            </details>
        </div>'''

    def _gen_battle_map(self, team1: List[UnitRepr], team2: List[UnitRepr]) -> str:
        """
        @brief Generate battle map HTML.
        @param team1 Team 1 units
        @param team2 Team 2 units
        @return HTML string
        """
        dots = ""
        for i, u in enumerate(team1, 1):
            if u.alive:
                dots += f'<div class="unit-cell team1" data-unit-id="unit-{u.uid}" onclick="selectUnit(\'unit-{u.uid}\')" style="grid-column:{int(u.x)+1};grid-row:{int(u.y)+1}">{u.letter}</div>'
        for i, u in enumerate(team2, 1):
            if u.alive:
                dots += f'<div class="unit-cell team2" data-unit-id="unit-{u.uid}" onclick="selectUnit(\'unit-{u.uid}\')" style="grid-column:{int(u.x)+1};grid-row:{int(u.y)+1}">{u.letter}</div>'

        return f'''
        <div class="battle-map-container">
            <details open>
                <summary>Battlefield ({self.board_width}x{self.board_height})</summary>
                <div class="battle-map" style="--cols:{self.board_width};--rows:{self.board_height}">{dots}</div>
            </details>
        </div>'''

    def _gen_breakdown(self, stats: Stats) -> str:
        """
        @brief Generate breakdown section HTML.
        @param stats Statistics object
        @return HTML string
        """
        def table(counts: Dict[str, int], title: str, color: str) -> str:
            total = sum(counts.values())
            if total == 0:
                return f'''
                <div class="breakdown-card">
                    <h4 style="color:var({color})">{title}</h4>
                    <div class="no-units-message">No units</div>
                </div>'''
            rows = "".join(
                f'<tr><td>{t}</td><td>{c}</td><td><div class="progress-bar">'
                f'<div class="progress-fill" style="width:{c/total*100}%;background:var({color})"></div>'
                f'</div></td></tr>'
                for t, c in sorted(counts.items())
            )
            return f'''
            <div class="breakdown-card">
                <h4 style="color:var({color})">{title}</h4>
                <table class="breakdown-table">
                    <thead><tr><th>Type</th><th>Count</th><th>%</th></tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>'''

        return f'''
        <div class="breakdown-container">
            <h3>Unit Breakdown</h3>
            <div class="breakdown-grid">
                {table(stats.type_counts_team1, "Team 1", "--team1-color")}
                {table(stats.type_counts_team2, "Team 2", "--team2-color")}
            </div>
        </div>'''

    def _gen_legend(self) -> str:
        """
        @brief Generate legend HTML.
        @return HTML string
        """
        return "\n".join(
            f"<li><strong>{letter}</strong>: {unit_type}</li>"
            for unit_type, letter in sorted(UNIT_LETTERS.items())
        )
