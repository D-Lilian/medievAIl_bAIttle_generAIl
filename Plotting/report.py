# -*- coding: utf-8 -*-
"""
@file       report.py
@brief      HTML Report Generator for Lanchester analysis.

@details    Generates professional HTML reports from LanchesterData with
            embedded statistics, visualizations, and Lanchester's Laws
            interpretation. Modern data science dashboard design.

@see LanchesterData for input data structure.
"""

import os
import webbrowser
from datetime import datetime
from typing import Dict, Any, Optional, List

import pandas as pd


class PlotReportGenerator:
    """
    @brief  Generates HTML reports from LanchesterData.
    
    @details Creates reports with configuration summary, Lanchester's Laws
             explanation, statistical analysis, data tables, and visualizations.
             Uses modern dashboard design with professional styling.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        @brief  Initialize the report generator.
        @param  output_dir Directory to save reports (default: 'Reports').
        """
        if output_dir is None:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.output_dir = os.path.join(project_root, 'Reports')
        else:
            self.output_dir = output_dir
            
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate(self, data, plot_path: str, stats: Optional[Dict[str, Any]] = None,
                 auto_open: bool = True) -> str:
        """
        @brief  Generate an HTML report from LanchesterData.
        @param  data LanchesterData object with pandas DataFrame.
        @param  plot_path Path to the generated plot image.
        @param  stats Optional statistical analysis results.
        @param  auto_open Whether to automatically open in browser (default: True).
        @return Path to the generated report file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(
            self.output_dir, 
            f"lanchester_report_{timestamp}.html"
        )
        
        content = self._generate_html(data, plot_path, stats or {})
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if auto_open:
            webbrowser.open(f'file://{os.path.abspath(report_path)}')
        
        return report_path

    def _get_css_styles(self) -> str:
        """@brief Generate modern CSS styles for the report."""
        return """
        :root {
            --primary: #1a1a2e;
            --primary-light: #16213e;
            --secondary: #0f3460;
            --accent: #e94560;
            --accent-light: #ff6b6b;
            --success: #00d9a5;
            --warning: #ffc107;
            --info: #00bcd4;
            --text: #2d3748;
            --text-light: #718096;
            --bg: #f7fafc;
            --card-bg: #ffffff;
            --border: #e2e8f0;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.7;
            color: var(--text);
            background: var(--bg);
            min-height: 100vh;
        }
        
        /* Header Section */
        .header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 3rem 2rem;
            margin-bottom: 2rem;
        }
        
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            letter-spacing: -0.025em;
        }
        
        .header .subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 400;
        }
        
        .header .meta {
            margin-top: 1.5rem;
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }
        
        .header .meta-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
            opacity: 0.85;
        }
        
        /* Main Container */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem 3rem;
        }
        
        /* Grid System */
        .grid {
            display: grid;
            gap: 1.5rem;
        }
        
        .grid-2 {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .grid-3 {
            grid-template-columns: repeat(3, 1fr);
        }
        
        .grid-4 {
            grid-template-columns: repeat(4, 1fr);
        }
        
        @media (max-width: 1024px) {
            .grid-4 { grid-template-columns: repeat(2, 1fr); }
            .grid-3 { grid-template-columns: repeat(2, 1fr); }
        }
        
        @media (max-width: 640px) {
            .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
        }
        
        /* Cards */
        .card {
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: var(--shadow);
            padding: 1.5rem;
            border: 1px solid var(--border);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--border);
        }
        
        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--primary);
        }
        
        .card-full {
            grid-column: 1 / -1;
        }
        
        /* Stat Cards */
        .stat-card {
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: var(--shadow);
            padding: 1.5rem;
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
        }
        
        .stat-card .stat-icon {
            width: 48px;
            height: 48px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .stat-card .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
            line-height: 1.2;
        }
        
        .stat-card .stat-label {
            font-size: 0.875rem;
            color: var(--text-light);
            margin-top: 0.25rem;
        }
        
        .stat-card.melee .stat-icon { background: rgba(233, 69, 96, 0.1); color: var(--accent); }
        .stat-card.ranged .stat-icon { background: rgba(0, 188, 212, 0.1); color: var(--info); }
        .stat-card.success .stat-icon { background: rgba(0, 217, 165, 0.1); color: var(--success); }
        .stat-card.warning .stat-icon { background: rgba(255, 193, 7, 0.1); color: var(--warning); }
        
        /* Theory Box */
        .theory-box {
            background: linear-gradient(135deg, var(--secondary) 0%, var(--primary-light) 100%);
            color: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .theory-box h2 {
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .theory-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
        }
        
        @media (max-width: 768px) {
            .theory-grid { grid-template-columns: 1fr; }
        }
        
        .law-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
        }
        
        .law-card h3 {
            font-size: 1.1rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .law-card p {
            font-size: 0.95rem;
            opacity: 0.9;
            line-height: 1.6;
        }
        
        .law-card .formula {
            background: rgba(0, 0, 0, 0.2);
            padding: 0.75rem 1rem;
            border-radius: 6px;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 0.9rem;
            margin-top: 1rem;
            text-align: center;
        }
        
        /* Section Headers */
        .section-header {
            margin: 2.5rem 0 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .section-header h2 {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--primary);
        }
        
        .section-header .badge {
            background: var(--accent);
            color: white;
            font-size: 0.75rem;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-weight: 500;
        }
        
        /* Tables */
        .table-container {
            overflow-x: auto;
            border-radius: 10px;
            border: 1px solid var(--border);
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }
        
        .data-table th {
            background: var(--primary);
            color: white;
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            white-space: nowrap;
        }
        
        .data-table th:first-child {
            border-radius: 10px 0 0 0;
        }
        
        .data-table th:last-child {
            border-radius: 0 10px 0 0;
        }
        
        .data-table td {
            padding: 0.875rem 1rem;
            border-bottom: 1px solid var(--border);
        }
        
        .data-table tr:last-child td {
            border-bottom: none;
        }
        
        .data-table tr:nth-child(even) {
            background: var(--bg);
        }
        
        .data-table tr:hover {
            background: rgba(15, 52, 96, 0.05);
        }
        
        .data-table .highlight {
            font-weight: 600;
            color: var(--primary);
        }
        
        /* Plot Container */
        .plot-container {
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: var(--shadow-lg);
            padding: 1.5rem;
            text-align: center;
            border: 1px solid var(--border);
        }
        
        .plot-container img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }
        
        /* Result Cards */
        .result-card {
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: var(--shadow);
            padding: 1.5rem;
            border-left: 4px solid var(--accent);
        }
        
        .result-card.linear { border-left-color: var(--accent); }
        .result-card.quadratic { border-left-color: var(--info); }
        .result-card.confirmed { border-left-color: var(--success); }
        .result-card.inconclusive { border-left-color: var(--warning); }
        
        .result-card h4 {
            font-size: 1.1rem;
            color: var(--primary);
            margin-bottom: 0.5rem;
        }
        
        .result-card p {
            color: var(--text-light);
            font-size: 0.95rem;
        }
        
        .result-card .metrics {
            display: flex;
            gap: 1.5rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }
        
        .result-card .metric {
            display: flex;
            flex-direction: column;
        }
        
        .result-card .metric-value {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
        }
        
        .result-card .metric-label {
            font-size: 0.8rem;
            color: var(--text-light);
        }
        
        /* Badges */
        .badge-linear {
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .badge-quadratic {
            background: linear-gradient(135deg, var(--info) 0%, #26c6da 100%);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            color: var(--text-light);
            border-top: 1px solid var(--border);
            margin-top: 3rem;
        }
        
        .footer a {
            color: var(--accent);
            text-decoration: none;
        }
        
        /* Utility Classes */
        .text-center { text-align: center; }
        .text-right { text-align: right; }
        .font-mono { font-family: 'JetBrains Mono', 'Fira Code', monospace; }
        .mt-1 { margin-top: 0.5rem; }
        .mt-2 { margin-top: 1rem; }
        .mb-1 { margin-bottom: 0.5rem; }
        .mb-2 { margin-bottom: 1rem; }
        """
    
    def _generate_html(self, data, plot_path: str, stats: Dict[str, Any]) -> str:
        """@brief Generate HTML report content."""
        
        # Get plot filename for embedding
        plot_filename = os.path.basename(str(plot_path))
        
        # Get summary DataFrame
        if hasattr(data, 'get_summary_by_type_and_n'):
            summary_df = data.get_summary_by_type_and_n()
        else:
            summary_df = pd.DataFrame()
        
        # Calculate overview stats
        total_sims = len(data.df)
        n_types = len(data.unit_types)
        n_range_str = f"{data.n_range[0]} → {data.n_range[-1]}" if data.n_range else "N/A"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lanchester Analysis Report | MedievAIl</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="header-content">
            <h1>Lanchester's Laws Analysis</h1>
            <p class="subtitle">Melee vs Ranged Combat Dynamics Simulation</p>
            <div class="meta">
                <span class="meta-item">Date: {datetime.now().strftime('%B %d, %Y at %H:%M')}</span>
                <span class="meta-item">{total_sims} simulations</span>
                <span class="meta-item">{n_types} unit type{'s' if n_types > 1 else ''}</span>
                <span class="meta-item">N range: {n_range_str}</span>
            </div>
        </div>
    </header>
    
    <main class="container">
        <!-- Theory Section -->
        <div class="theory-box">
            <h2>Lanchester's Laws Theory (N vs 2N)</h2>
            <div class="theory-grid">
                <div class="law-card">
                    <h3>Linear Law (Melee)</h3>
                    <p>In close combat, each soldier engages one enemy at a time. 
                    Team B (2N) loses N casualties before winning.</p>
                    <div class="formula">Team B casualties = N (slope ≈ 1.0)</div>
                </div>
                <div class="law-card">
                    <h3>Square Law (Ranged)</h3>
                    <p>In ranged combat, focus fire allows concentration of attacks. 
                    Team B wins with fewer casualties.</p>
                    <div class="formula">Team B casualties ≈ 0.27N (slope ≈ 0.27)</div>
                </div>
            </div>
        </div>
        
        <!-- Quick Stats -->
        <div class="section-header">
            <h2>Simulation Overview</h2>
        </div>
        
        <div class="grid grid-4">
            <div class="stat-card success">
                <div class="stat-value">{total_sims}</div>
                <div class="stat-label">Total Simulations</div>
            </div>
            <div class="stat-card melee">
                <div class="stat-value">{data.num_repetitions}</div>
                <div class="stat-label">Runs per Config</div>
            </div>
            <div class="stat-card ranged">
                <div class="stat-value">{len(data.n_range) if data.n_range else 0}</div>
                <div class="stat-label">N Values Tested</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-value font-mono" style="font-size: 1rem;">{data.ai_name}</div>
                <div class="stat-label">AI Strategy</div>
            </div>
        </div>
        
        <!-- Configuration -->
        <div class="section-header">
            <h2>Configuration</h2>
        </div>
        
        <div class="card">
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Value</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="highlight">AI Strategy</td>
                            <td><code class="font-mono">{data.ai_name}</code></td>
                            <td>Combat decision algorithm</td>
                        </tr>
                        <tr>
                            <td class="highlight">Scenario</td>
                            <td><code class="font-mono">{data.scenario_name}</code></td>
                            <td>N vs 2N army configuration</td>
                        </tr>
                        <tr>
                            <td class="highlight">Unit Types</td>
                            <td>{', '.join(f'<span class="badge-{"linear" if t == "Knight" else "quadratic"}">{t}</span>' for t in data.unit_types)}</td>
                            <td>Combat unit classes being compared</td>
                        </tr>
                        <tr>
                            <td class="highlight">N Range</td>
                            <td><code class="font-mono">[{', '.join(str(n) for n in (data.n_range or []))}]</code></td>
                            <td>Army sizes tested (Team A = N, Team B = 2N)</td>
                        </tr>
                        <tr>
                            <td class="highlight">Repetitions</td>
                            <td>{data.num_repetitions}</td>
                            <td>Statistical replicates per configuration</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Visualization -->
        <div class="section-header">
            <h2>Visualization</h2>
            <span class="badge">Interactive Plot</span>
        </div>
        
        <div class="plot-container">
            <img src="./{plot_filename}" alt="Lanchester Analysis Plot">
        </div>
        
        {self._generate_stats_section(stats)}
        
        {self._generate_data_tables(summary_df, data.unit_types)}
        
        {self._generate_interpretation(data.unit_types, stats)}
        
        <!-- Footer -->
        <footer class="footer">
            <p>Generated by <strong>MedievAIl bAIttle generAIl</strong></p>
            <p>Data Analysis powered by <a href="https://pandas.pydata.org/">pandas</a> & 
               <a href="https://plotnine.org/">plotnine</a></p>
        </footer>
    </main>
</body>
</html>
"""
        return html
    
    def _generate_stats_section(self, stats: Dict[str, Any]) -> str:
        """@brief Generate statistical analysis HTML section."""
        if not stats:
            return ""
        
        html = """
        <div class="section-header">
            <h2>Statistical Analysis</h2>
            <span class="badge">Lanchester's Laws Test</span>
        </div>
        """
        
        lanchester = stats.get('lanchester_tests', {})
        
        if lanchester:
            # Summary cards for each unit
            html += '<div class="grid grid-2 mb-2">'
            
            for unit_type, result in lanchester.items():
                slope = result.get('slope', 0)
                r2 = result.get('r2', 0)
                theoretical_linear = result.get('theoretical_linear', 1.0)
                theoretical_square = result.get('theoretical_square', 0.27)
                best_fit = result.get('best_fit', 'Unknown')
                interpretation = result.get('interpretation', '')
                
                card_class = "linear" if "Linear" in best_fit else "quadratic"
                is_confirmed = '✓' in interpretation
                
                html += f"""
                <div class="result-card {card_class} {'confirmed' if is_confirmed else ''}">
                    <h4>{unit_type} <span class="badge-{card_class}">{best_fit}</span></h4>
                    <p>{interpretation}</p>
                    <div class="metrics">
                        <div class="metric">
                            <span class="metric-value">{slope:.3f}</span>
                            <span class="metric-label">Observed Slope</span>
                        </div>
                        <div class="metric">
                            <span class="metric-value">{r2:.3f}</span>
                            <span class="metric-label">R²</span>
                        </div>
                        <div class="metric">
                            <span class="metric-value">{theoretical_linear:.2f} / {theoretical_square:.2f}</span>
                            <span class="metric-label">Theory (Lin/Sq)</span>
                        </div>
                    </div>
                </div>
                """
            
            html += '</div>'
            
            # Detailed table
            html += """
            <div class="card mt-2">
                <div class="card-header">
                    <span class="card-title">Slope Analysis Details</span>
                </div>
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Unit Type</th>
                                <th>Observed Slope</th>
                                <th>R²</th>
                                <th>Linear Theory</th>
                                <th>Square Theory</th>
                                <th>Best Match</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for unit_type, result in lanchester.items():
                slope = result.get('slope', 0)
                r2 = result.get('r2', 0)
                theoretical_linear = result.get('theoretical_linear', 1.0)
                theoretical_square = result.get('theoretical_square', 0.27)
                best_fit = result.get('best_fit', 'Unknown')
                
                badge_class = "linear" if "Linear" in best_fit else "quadratic"
                
                html += f"""
                    <tr>
                        <td class="highlight">{unit_type}</td>
                        <td class="font-mono">{slope:.4f}</td>
                        <td class="font-mono">{r2:.4f}</td>
                        <td class="font-mono">{theoretical_linear:.2f}</td>
                        <td class="font-mono">{theoretical_square:.2f}</td>
                        <td><span class="badge-{badge_class}">{best_fit}</span></td>
                    </tr>
                """
            
            html += "</tbody></table></div></div>"
        
        # Descriptive stats
        descriptive = stats.get('descriptive', {})
        if descriptive:
            html += """
            <div class="card mt-2">
                <div class="card-header">
                    <span class="card-title">Descriptive Statistics</span>
                </div>
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Unit Type</th>
                                <th>Simulations</th>
                                <th>Casualties (μ)</th>
                                <th>Casualties (σ)</th>
                                <th>Duration (μ)</th>
                                <th>2N Win Rate</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for unit_type, desc in descriptive.items():
                win_rate = desc.get('win_rate_2n', 0) * 100
                
                html += f"""
                    <tr>
                        <td class="highlight">{unit_type}</td>
                        <td>{desc.get('n_simulations', 0)}</td>
                        <td class="font-mono">{desc.get('casualties_mean', 0):.2f}</td>
                        <td class="font-mono">{desc.get('casualties_std', 0):.2f}</td>
                        <td class="font-mono">{desc.get('duration_mean', 0):.1f} ticks</td>
                        <td><strong>{win_rate:.1f}%</strong></td>
                    </tr>
                """
            
            html += "</tbody></table></div></div>"
        
        return html
    
    def _generate_data_tables(self, summary_df: pd.DataFrame, unit_types: List[str]) -> str:
        """@brief Generate data tables for each unit type from DataFrame."""
        if summary_df.empty:
            return ""
        
        html = """
        <div class="section-header">
            <h2>Detailed Data</h2>
        </div>
        """
        
        for unit_type in unit_types:
            type_df = summary_df[summary_df['unit_type'] == unit_type]
            
            if type_df.empty:
                continue
            
            is_melee = unit_type in ['Knight', 'Pikeman', 'Swordsman']
            badge_class = "linear" if is_melee else "quadratic"
            law_type = "Linear (Melee)" if is_melee else "Square (Ranged)"
            
            html += f"""
            <div class="card mt-2">
                <div class="card-header">
                    <span class="card-title">{unit_type}</span>
                    <span class="badge-{badge_class}">{law_type}</span>
                </div>
                {self._get_unit_theory_text(unit_type)}
                <div class="table-container mt-1">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>N</th>
                                <th>Team A (N)</th>
                                <th>Team B (2N)</th>
                                <th>A Casualties</th>
                                <th>B Casualties</th>
                                <th>Winner Casualties</th>
                                <th>2N Win Rate</th>
                                <th>Duration</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for _, row in type_df.iterrows():
                n = int(row['n_value'])
                a_cas = row['mean_team_a_casualties']
                b_cas = row['mean_team_b_casualties']
                winner_cas = row['mean_winner_casualties']
                b_win = row['team_b_win_rate'] * 100
                duration = row['mean_duration']
                
                html += f"""
                    <tr>
                        <td class="highlight">{n}</td>
                        <td>{n} units</td>
                        <td>{2*n} units</td>
                        <td class="font-mono">{a_cas:.1f}</td>
                        <td class="font-mono">{b_cas:.1f}</td>
                        <td class="font-mono">{winner_cas:.1f}</td>
                        <td><strong>{b_win:.0f}%</strong></td>
                        <td class="font-mono">{duration:.0f} ticks</td>
                    </tr>
                """
            
            html += "</tbody></table></div></div>"
        
        return html
    
    def _get_unit_theory_text(self, unit_type: str) -> str:
        """@brief Get theory explanation for unit type."""
        texts = {
            'Knight': """
                <p class="mt-1" style="color: var(--text-light);">
                    <strong>Theory:</strong> Knights are melee units. According to Lanchester's <strong>Linear Law</strong>,
                    in 1v1 combat each Team A soldier kills one Team B soldier. Expected slope ≈ 1.0.
                </p>""",
            'Crossbowman': """
                <p class="mt-1" style="color: var(--text-light);">
                    <strong>Theory:</strong> Crossbowmen are ranged units. According to Lanchester's <strong>Square Law</strong>,
                    focus fire allows Team B to win with fewer casualties. Expected slope ≈ 0.27.
                </p>""",
            'Pikeman': """
                <p class="mt-1" style="color: var(--text-light);">
                    <strong>Theory:</strong> Pikemen are melee units. They should follow
                    Lanchester's <strong>Linear Law</strong> with expected slope ≈ 1.0.
                </p>""",
            'Archer': """
                <p class="mt-1" style="color: var(--text-light);">
                    <strong>Theory:</strong> Archers are ranged units. According to Lanchester's <strong>Square Law</strong>,
                    they should have expected slope ≈ 0.27.
                </p>""",
        }
        return texts.get(unit_type, f'<p class="mt-1" style="color: var(--text-light);">Analysis for {unit_type}.</p>')
    
    def _generate_interpretation(self, unit_types: List[str], stats: Dict[str, Any]) -> str:
        """@brief Generate interpretation section."""
        html = """
        <div class="section-header">
            <h2>Interpretation</h2>
        </div>
        """
        
        if 'Knight' in unit_types and 'Crossbowman' in unit_types:
            html += """
            <div class="result-card confirmed">
                <h4>Melee vs Ranged Combat Comparison</h4>
                <p>This analysis compares how different unit types scale in the N vs 2N scenario.
                Lanchester's Laws predict different slopes:</p>
                <ul style="margin-top: 0.75rem; padding-left: 1.25rem; color: var(--text-light);">
                    <li><strong>Knights (Melee):</strong> Linear Law — slope ≈ 1.0 
                    (each Team A unit kills one Team B unit before dying).</li>
                    <li><strong>Crossbowmen (Ranged):</strong> Square Law — slope ≈ 0.27 
                    (focus fire allows Team B to win with fewer casualties).</li>
                </ul>
                <p style="margin-top: 0.75rem; font-style: italic; color: var(--text-light);">
                    <strong>Note:</strong> With a 2:1 advantage, Team B (2N) always wins. 
                    Observed slopes near 0 indicate the advantage is too dominant for meaningful analysis.
                </p>
            </div>
            """
        
        lanchester = stats.get('lanchester_tests', {})
        if lanchester:
            html += '<div class="grid grid-2 mt-2">'
            
            for unit_type, result in lanchester.items():
                interpretation = result.get('interpretation', '')
                best_fit = result.get('best_fit', 'Unknown')
                
                if 'confirms' in interpretation.lower():
                    card_class = 'confirmed'
                elif 'inconclusive' in interpretation.lower():
                    card_class = 'inconclusive'
                else:
                    card_class = 'linear' if best_fit == 'Linear' else 'quadratic'
                
                html += f"""
                <div class="result-card {card_class}">
                    <h4>{unit_type}</h4>
                    <p>{interpretation}</p>
                </div>
                """
            
            html += '</div>'
        
        html += """
        <div class="card mt-2">
            <div class="card-header">
                <span class="card-title">Methodology Notes</span>
            </div>
            <p style="color: var(--text-light);">
                This analysis uses <strong>linear regression</strong> to fit the relationship between initial army size (N)
                and Team B casualties. The <strong>slope</strong> of this regression is compared to theoretical predictions.
            </p>
            <p style="color: var(--text-light); margin-top: 0.5rem;">
                <span class="badge-linear">Linear Law</span> predicts slope ≈ 1.0 (melee: each Team A unit kills one Team B unit).<br>
                <span class="badge-quadratic">Square Law</span> predicts slope ≈ 0.27 (ranged: focus fire reduces Team B casualties).
            </p>
        </div>
        """
        
        return html
