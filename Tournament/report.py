# -*- coding: utf-8 -*-
"""
@file report.py
@brief Tournament Report Generator

@details
Generates HTML reports from tournament results.
Follows Single Responsibility Principle - only handles report generation.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from Tournament.results import TournamentResults
from Tournament.config import TournamentConfig
from Tournament.runner import TournamentRunner

# Path to CSS file (same directory as this module)
CSS_FILE_PATH = Path(__file__).parent / "tournament_report.css"

class TournamentReportGenerator:
    """
    Generates HTML reports from tournament results.
    
    Creates comprehensive reports with:
    - Overall standings
    - General vs General matrix
    - Per-scenario matrices
    - General vs Scenario performance
    """
    
    def __init__(self, output_dir: str = "Reports"):
        """
        Initialize report generator.
        
        @param output_dir: Directory for output files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, results: TournamentResults) -> str:
        """
        Generate HTML tournament report.
        
        @param results: Tournament results
        @return: Path to generated report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"tournament_report_{timestamp}.html")
        
        html = self._generate_html(results)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\nTournament report generated: {filename}")
        return filename
    
    def _generate_html(self, results: TournamentResults) -> str:
        """Generate the HTML content."""
        overall = results.get_overall_scores()
        gvg = results.get_general_vs_general_matrix()
        gvs = results.get_general_vs_scenario_matrix()
        scenarios = results.get_scenarios()
        generals = results.config.generals
        
        # Calculate performance metrics
        perf_stats = self._calculate_performance_stats(results)
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tournament Report - {results.timestamp[:10]}</title>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Tournament Report</h1>
            <p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </header>
        
        {self._generate_executive_summary(results, overall, generals, perf_stats)}
        
        <section class="config">
            <h2>Configuration</h2>
            <div class="config-grid">
                <div class="config-item">
                    <span class="label">Generals</span>
                    <span class="value">{', '.join(generals)}</span>
                </div>
                <div class="config-item">
                    <span class="label">Scenarios</span>
                    <span class="value">{', '.join(scenarios)}</span>
                </div>
                <div class="config-item">
                    <span class="label">Rounds/Matchup</span>
                    <span class="value">{results.config.rounds_per_matchup}</span>
                </div>
                <div class="config-item">
                    <span class="label">Position Alternation</span>
                    <span class="value">{'Yes' if results.config.alternate_positions else 'No'}</span>
                </div>
                <div class="config-item">
                    <span class="label">Total Matches</span>
                    <span class="value">{len(results.matches)}</span>
                </div>
            </div>
        </section>
        
        <section class="overall">
            <h2>Overall Standings</h2>
            {self._generate_overall_table(overall, generals)}
            {self._generate_winrate_chart(overall, generals)}
        </section>
        
        <section class="performance">
            <h2>Performance Metrics</h2>
            <p class="description">Average casualties and battle duration per general</p>
            {self._generate_performance_table(perf_stats, generals)}
        </section>
        
        <section class="gvg">
            <h2>General vs General Matrix</h2>
            <p class="description">Win rate when row general plays as Team A against column general</p>
            {self._generate_matrix_table(gvg, generals, generals)}
        </section>
        
        <section class="per-scenario">
            <h2>Per-Scenario Analysis</h2>
            {self._generate_per_scenario_matrices(results, generals, scenarios)}
        </section>
        
        <section class="gvs">
            <h2>General vs Scenario</h2>
            <p class="description">General performance on each scenario</p>
            {self._generate_gvs_table(gvs, generals, scenarios)}
        </section>
        
        <section class="reflexive">
            <h2>Reflexive Matchups (X vs X)</h2>
            <p class="description">Self-play fairness check - deviation from 50% indicates position bias</p>
            {self._generate_reflexive_table(results, generals)}
        </section>
        
        <footer>
            <p>MedievAIl bAIttle generAIl - Tournament System</p>
        </footer>
    </div>
</body>
</html>'''
        
        return html
    
    def _calculate_performance_stats(self, results: TournamentResults) -> Dict:
        """Calculate performance statistics per general."""
        stats = {}
        for general in results.config.generals:
            matches_as_a = [m for m in results.matches if m.general_a == general]
            matches_as_b = [m for m in results.matches if m.general_b == general]
            
            casualties_inflicted = []
            casualties_taken = []
            durations = []
            
            for m in matches_as_a:
                casualties_inflicted.append(m.team_b_casualties)
                casualties_taken.append(m.team_a_casualties)
                durations.append(m.ticks)
            
            for m in matches_as_b:
                casualties_inflicted.append(m.team_a_casualties)
                casualties_taken.append(m.team_b_casualties)
                durations.append(m.ticks)
            
            stats[general] = {
                'avg_casualties_inflicted': sum(casualties_inflicted) / len(casualties_inflicted) if casualties_inflicted else 0,
                'avg_casualties_taken': sum(casualties_taken) / len(casualties_taken) if casualties_taken else 0,
                'avg_duration': sum(durations) / len(durations) if durations else 0,
                'total_matches': len(casualties_inflicted)
            }
            
            # K/D ratio
            if stats[general]['avg_casualties_taken'] > 0:
                stats[general]['kd_ratio'] = stats[general]['avg_casualties_inflicted'] / stats[general]['avg_casualties_taken']
            else:
                stats[general]['kd_ratio'] = float('inf')
        
        return stats
    
    def _generate_executive_summary(self, results: TournamentResults, 
                                    overall: Dict, generals: List[str],
                                    perf_stats: Dict) -> str:
        """Generate executive summary section."""
        sorted_generals = sorted(
            generals, 
            key=lambda g: overall.get(g, {}).get('win_rate', 0), 
            reverse=True
        )
        
        winner = sorted_generals[0] if sorted_generals else "N/A"
        winner_rate = overall.get(winner, {}).get('win_rate', 0)
        total_matches = len(results.matches)
        
        # Best K/D ratio
        best_kd = max(generals, key=lambda g: perf_stats.get(g, {}).get('kd_ratio', 0))
        best_kd_val = perf_stats.get(best_kd, {}).get('kd_ratio', 0)
        
        return f'''
        <section class="summary">
            <h2>Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card winner">
                    <div class="card-icon">1st</div>
                    <div class="card-content">
                        <div class="card-value">{winner}</div>
                        <div class="card-label">Tournament Winner</div>
                        <div class="card-detail">{winner_rate:.1f}% win rate</div>
                    </div>
                </div>
                <div class="summary-card">
                    <div class="card-icon">N</div>
                    <div class="card-content">
                        <div class="card-value">{total_matches}</div>
                        <div class="card-label">Total Matches</div>
                        <div class="card-detail">{len(generals)} generals</div>
                    </div>
                </div>
                <div class="summary-card">
                    <div class="card-icon">K/D</div>
                    <div class="card-content">
                        <div class="card-value">{best_kd}</div>
                        <div class="card-label">Best K/D Ratio</div>
                        <div class="card-detail">{best_kd_val:.2f}</div>
                    </div>
                </div>
            </div>
        </section>
        '''
    
    def _generate_winrate_chart(self, overall: Dict, generals: List[str]) -> str:
        """Generate CSS-based bar chart for win rates."""
        sorted_generals = sorted(
            generals, 
            key=lambda g: overall.get(g, {}).get('win_rate', 0), 
            reverse=True
        )
        
        bars = []
        colors = ['#27ae60', '#3498db', '#9b59b6', '#e74c3c', '#f39c12', '#1abc9c']
        
        for i, general in enumerate(sorted_generals):
            rate = overall.get(general, {}).get('win_rate', 0)
            color = colors[i % len(colors)]
            bars.append(f'''
                <div class="bar-row">
                    <div class="bar-label">{general}</div>
                    <div class="bar-container">
                        <div class="bar" style="width: {rate}%; background: {color};"></div>
                        <span class="bar-value">{rate:.1f}%</span>
                    </div>
                </div>
            ''')
        
        return f'''
        <div class="chart-container">
            <h4>Win Rate Distribution</h4>
            {''.join(bars)}
        </div>
        '''
    
    def _generate_performance_table(self, perf_stats: Dict, generals: List[str]) -> str:
        """Generate performance metrics table."""
        rows = []
        
        # Sort by K/D ratio
        sorted_generals = sorted(
            generals,
            key=lambda g: perf_stats.get(g, {}).get('kd_ratio', 0),
            reverse=True
        )
        
        for general in sorted_generals:
            stats = perf_stats.get(general, {})
            kd = stats.get('kd_ratio', 0)
            kd_display = f"{kd:.2f}" if kd != float('inf') else "INF"
            kd_class = 'high' if kd > 1.5 else ('medium' if kd > 0.8 else 'low')
            
            rows.append(f'''
                <tr>
                    <td><strong>{general}</strong></td>
                    <td>{stats.get('avg_casualties_inflicted', 0):.1f}</td>
                    <td>{stats.get('avg_casualties_taken', 0):.1f}</td>
                    <td class="win-rate {kd_class}">{kd_display}</td>
                    <td>{stats.get('avg_duration', 0):.0f}</td>
                </tr>
            ''')
        
        return f'''
        <table>
            <thead>
                <tr>
                    <th>General</th>
                    <th>Avg Kills</th>
                    <th>Avg Deaths</th>
                    <th>K/D Ratio</th>
                    <th>Avg Duration (ticks)</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        '''
    
    def _get_css(self) -> str:
        """Load CSS styles from external file."""
        try:
            with open(CSS_FILE_PATH, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to minimal inline CSS if file not found
            return self._get_fallback_css()
    
    def _get_fallback_css(self) -> str:
        """Minimal fallback CSS if external file is missing."""
        return '''
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #34495e;
            --accent-color: #3498db;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: sans-serif; background: var(--bg-color); color: var(--primary-color); line-height: 1.6; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header { text-align: center; padding: 30px; background: var(--primary-color); color: white; border-radius: 10px; margin-bottom: 30px; }
        section { background: var(--card-bg); border-radius: 10px; padding: 25px; margin-bottom: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px 15px; text-align: center; border: 1px solid #ddd; }
        th { background: var(--primary-color); color: white; }
        .win-rate.high { color: var(--success-color); }
        .win-rate.medium { color: var(--warning-color); }
        .win-rate.low { color: var(--danger-color); }
        '''
    
    def _generate_overall_table(self, overall: Dict, generals: List[str]) -> str:
        """Generate overall standings table."""
        # Sort by win rate
        sorted_generals = sorted(
            generals, 
            key=lambda g: overall.get(g, {}).get('win_rate', 0), 
            reverse=True
        )
        
        rows = []
        for rank, general in enumerate(sorted_generals, 1):
            data = overall.get(general, {'wins': 0, 'losses': 0, 'draws': 0, 'total': 0, 'win_rate': 0})
            
            badge = ''
            if rank == 1:
                badge = '<span class="badge gold">🥇</span>'
            elif rank == 2:
                badge = '<span class="badge silver">🥈</span>'
            elif rank == 3:
                badge = '<span class="badge bronze">🥉</span>'
            
            win_class = self._get_win_class(data['win_rate'])
            
            rows.append(f'''
                <tr>
                    <td>{rank} {badge}</td>
                    <td><strong>{general}</strong></td>
                    <td>{data['wins']}</td>
                    <td>{data['losses']}</td>
                    <td>{data['draws']}</td>
                    <td>{data['total']}</td>
                    <td class="win-rate {win_class}">{data['win_rate']:.1f}%</td>
                </tr>
            ''')
        
        return f'''
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>General</th>
                    <th>Wins</th>
                    <th>Losses</th>
                    <th>Draws</th>
                    <th>Total</th>
                    <th>Win Rate</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        '''
    
    def _generate_matrix_table(self, matrix: Dict, row_labels: List[str], 
                                col_labels: List[str]) -> str:
        """Generate a matrix table (general vs general)."""
        header_cells = ''.join(f'<th>{g}</th>' for g in col_labels)
        
        rows = []
        for row_gen in row_labels:
            cells = [f'<th>{row_gen}</th>']
            for col_gen in col_labels:
                data = matrix.get(row_gen, {}).get(col_gen, {'win_rate': 0, 'total': 0})
                win_rate = data.get('win_rate', 0)
                total = data.get('total', 0)
                
                win_class = self._get_win_class(win_rate)
                self_class = 'self-play' if row_gen == col_gen else ''
                
                if total > 0:
                    cells.append(f'<td class="matrix-cell {self_class} win-rate {win_class}">{win_rate:.1f}%</td>')
                else:
                    cells.append(f'<td class="matrix-cell {self_class}">-</td>')
            
            rows.append(f'<tr>{"".join(cells)}</tr>')
        
        return f'''
        <table>
            <thead>
                <tr>
                    <th>↓ As Team A / Opponent →</th>
                    {header_cells}
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        '''
    
    def _generate_per_scenario_matrices(self, results: TournamentResults, 
                                         generals: List[str], 
                                         scenarios: List[str]) -> str:
        """Generate matrix tables for each scenario."""
        sections = []
        
        for scenario in scenarios:
            matrix = results.get_general_vs_general_per_scenario(scenario)
            table = self._generate_matrix_table(matrix, generals, generals)
            
            sections.append(f'''
            <div class="scenario-section">
                <h3>{scenario}</h3>
                {table}
            </div>
            ''')
        
        return ''.join(sections)
    
    def _generate_gvs_table(self, gvs: Dict, generals: List[str], 
                            scenarios: List[str]) -> str:
        """Generate general vs scenario table."""
        header_cells = ''.join(f'<th>{s}</th>' for s in scenarios)
        
        rows = []
        for general in generals:
            cells = [f'<th>{general}</th>']
            for scenario in scenarios:
                data = gvs.get(general, {}).get(scenario, {'win_rate': 0, 'total': 0})
                win_rate = data.get('win_rate', 0)
                total = data.get('total', 0)
                
                win_class = self._get_win_class(win_rate)
                
                if total > 0:
                    cells.append(f'<td class="win-rate {win_class}">{win_rate:.1f}%</td>')
                else:
                    cells.append('<td>-</td>')
            
            rows.append(f'<tr>{"".join(cells)}</tr>')
        
        return f'''
        <table>
            <thead>
                <tr>
                    <th>General / Scenario</th>
                    {header_cells}
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        '''
    
    def _generate_reflexive_table(self, results: TournamentResults, 
                                   generals: List[str]) -> str:
        """Generate table for reflexive matchups (X vs X)."""
        rows = []
        
        for general in generals:
            # Filter matches where same general plays both sides
            reflexive_matches = [
                m for m in results.matches 
                if m.general_a == general and m.general_b == general
            ]
            
            if not reflexive_matches:
                continue
            
            wins_a = sum(1 for m in reflexive_matches if m.winner == 'A')
            wins_b = sum(1 for m in reflexive_matches if m.winner == 'B')
            draws = sum(1 for m in reflexive_matches if m.is_draw)
            total = len(reflexive_matches)
            
            rate_a = wins_a / total * 100 if total > 0 else 0
            rate_b = wins_b / total * 100 if total > 0 else 0
            
            # Check for bias (should be close to 50/50)
            bias_class = 'high' if abs(rate_a - 50) <= 10 else 'low'
            
            rows.append(f'''
                <tr>
                    <td><strong>{general}</strong></td>
                    <td>{total}</td>
                    <td>{wins_a} ({rate_a:.1f}%)</td>
                    <td>{wins_b} ({rate_b:.1f}%)</td>
                    <td>{draws}</td>
                    <td class="win-rate {bias_class}">{abs(rate_a - 50):.1f}%</td>
                </tr>
            ''')
        
        if not rows:
            return '<p>No reflexive matchups recorded.</p>'
        
        return f'''
        <table>
            <thead>
                <tr>
                    <th>General</th>
                    <th>Total Matches</th>
                    <th>Wins as Team A</th>
                    <th>Wins as Team B</th>
                    <th>Draws</th>
                    <th>Bias from 50%</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        <p class="description" style="margin-top: 15px;">
            <strong>Note:</strong> Bias from 50% indicates potential player-position advantage. 
            Values close to 0% indicate fair gameplay. High values suggest a bug favoring one position.
        </p>
        '''
    
    def _get_win_class(self, win_rate: float) -> str:
        """Get CSS class based on win rate."""
        if win_rate >= 60:
            return 'high'
        elif win_rate >= 40:
            return 'medium'
        else:
            return 'low'


def run_tournament(generals: List[str] = None, scenarios: List[str] = None,
                   rounds: int = 10, alternate: bool = True) -> TournamentResults:
    """
    Convenience function to run a tournament.
    
    @param generals: List of general names (default: all available)
    @param scenarios: List of scenario names (default: all available)
    @param rounds: Rounds per matchup
    @param alternate: Whether to alternate positions
    @return: Tournament results
    """
    if generals is None:
        generals = TournamentRunner.AVAILABLE_GENERALS
    
    if scenarios is None:
        scenarios = list(TournamentRunner.SCENARIO_MAP.keys())
    
    config = TournamentConfig(
        generals=generals,
        scenarios=scenarios,
        rounds_per_matchup=rounds,
        alternate_positions=alternate
    )
    
    runner = TournamentRunner(config)
    results = runner.run()
    
    # Generate report
    report_gen = TournamentReportGenerator()
    report_gen.generate(results)
    
    return results
