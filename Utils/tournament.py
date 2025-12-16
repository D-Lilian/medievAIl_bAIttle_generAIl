# -*- coding: utf-8 -*-
"""
@file tournament.py
@brief Tournament System - Automated battle tournament management

@details
Provides infrastructure for running automated tournaments between AI generals,
collecting results, and generating comprehensive reports with score matrices.

Features:
- Automatic position alternation to ensure fairness
- Reflexive matchups (X vs X) to detect player position bugs
- Score matrices: overall, general vs general, per scenario, general vs scenario
- HTML report generation with detailed statistics

"""
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict
from Model.generals import General
from Controller.simulation_controller import SimulationController
from Model.strategies import (
    StrategieBrainDead,
    StrategieDAFT,
    StrategieCrossbowmanSomeIQ,
    StrategieKnightSomeIQ,
    StrategiePikemanSomeIQ,
    StrategieStartSomeIQ,
)
from Model.units import UnitType

from Utils.predefined_scenarios import PredefinedScenarios


@dataclass
class MatchResult:
    """Result of a single match between two generals."""
    general_a: str  # Name of general playing as Team A
    general_b: str  # Name of general playing as Team B
    scenario_name: str
    winner: Optional[str]  # 'A', 'B', or None (draw)
    ticks: int
    team_a_survivors: int
    team_b_survivors: int
    team_a_casualties: int
    team_b_casualties: int
    is_draw: bool = False
    
    @property
    def winner_name(self) -> Optional[str]:
        """Get the name of the winning general."""
        if self.winner == 'A':
            return self.general_a
        elif self.winner == 'B':
            return self.general_b
        return None


@dataclass
class TournamentConfig:
    """Configuration for a tournament."""
    generals: List[str]
    scenarios: List[str]
    rounds_per_matchup: int = 10
    alternate_positions: bool = True
    max_ticks: int = 600  # Max ticks before declaring a draw (2 min at 5 ticks/s)
    

@dataclass
class TournamentResults:
    """Complete results from a tournament."""
    config: TournamentConfig
    matches: List[MatchResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_match(self, result: MatchResult):
        """Add a match result."""
        self.matches.append(result)
    
    def get_overall_scores(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate overall score for each general across all opponents and scenarios.
        Returns dict: general_name -> {wins, losses, draws, total, win_rate}
        """
        scores = defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0, 'total': 0})
        
        for match in self.matches:
            # Count for general_a (played as Team A)
            scores[match.general_a]['total'] += 1
            if match.is_draw:
                scores[match.general_a]['draws'] += 1
            elif match.winner == 'A':
                scores[match.general_a]['wins'] += 1
            else:
                scores[match.general_a]['losses'] += 1
            
            # Count for general_b (played as Team B)
            scores[match.general_b]['total'] += 1
            if match.is_draw:
                scores[match.general_b]['draws'] += 1
            elif match.winner == 'B':
                scores[match.general_b]['wins'] += 1
            else:
                scores[match.general_b]['losses'] += 1
        
        # Calculate win rates
        for general, data in scores.items():
            if data['total'] > 0:
                data['win_rate'] = data['wins'] / data['total'] * 100
            else:
                data['win_rate'] = 0.0
        
        return dict(scores)
    
    def get_general_vs_general_matrix(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Calculate general vs general scores across all scenarios.
        Returns dict: general1 -> general2 -> {wins, losses, draws, total, win_rate}
        """
        matrix = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0, 'total': 0}))
        
        for match in self.matches:
            # When general_a plays against general_b
            matrix[match.general_a][match.general_b]['total'] += 1
            if match.is_draw:
                matrix[match.general_a][match.general_b]['draws'] += 1
            elif match.winner == 'A':
                matrix[match.general_a][match.general_b]['wins'] += 1
            else:
                matrix[match.general_a][match.general_b]['losses'] += 1
        
        # Calculate win rates
        for g1 in matrix:
            for g2 in matrix[g1]:
                data = matrix[g1][g2]
                if data['total'] > 0:
                    data['win_rate'] = data['wins'] / data['total'] * 100
                else:
                    data['win_rate'] = 0.0
        
        return {k: dict(v) for k, v in matrix.items()}
    
    def get_general_vs_general_per_scenario(self, scenario: str) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Calculate general vs general matrix for a specific scenario.
        """
        matrix = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0, 'total': 0}))
        
        for match in self.matches:
            if match.scenario_name != scenario:
                continue
                
            matrix[match.general_a][match.general_b]['total'] += 1
            if match.is_draw:
                matrix[match.general_a][match.general_b]['draws'] += 1
            elif match.winner == 'A':
                matrix[match.general_a][match.general_b]['wins'] += 1
            else:
                matrix[match.general_a][match.general_b]['losses'] += 1
        
        # Calculate win rates
        for g1 in matrix:
            for g2 in matrix[g1]:
                data = matrix[g1][g2]
                if data['total'] > 0:
                    data['win_rate'] = data['wins'] / data['total'] * 100
                else:
                    data['win_rate'] = 0.0
        
        return {k: dict(v) for k, v in matrix.items()}
    
    def get_general_vs_scenario_matrix(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Calculate general performance across scenarios (across all opponents).
        Returns dict: general -> scenario -> {wins, losses, draws, total, win_rate}
        """
        matrix = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0, 'total': 0}))
        
        for match in self.matches:
            # Count for general_a
            matrix[match.general_a][match.scenario_name]['total'] += 1
            if match.is_draw:
                matrix[match.general_a][match.scenario_name]['draws'] += 1
            elif match.winner == 'A':
                matrix[match.general_a][match.scenario_name]['wins'] += 1
            else:
                matrix[match.general_a][match.scenario_name]['losses'] += 1
            
            # Count for general_b
            matrix[match.general_b][match.scenario_name]['total'] += 1
            if match.is_draw:
                matrix[match.general_b][match.scenario_name]['draws'] += 1
            elif match.winner == 'B':
                matrix[match.general_b][match.scenario_name]['wins'] += 1
            else:
                matrix[match.general_b][match.scenario_name]['losses'] += 1
        
        # Calculate win rates
        for general in matrix:
            for scenario in matrix[general]:
                data = matrix[general][scenario]
                if data['total'] > 0:
                    data['win_rate'] = data['wins'] / data['total'] * 100
                else:
                    data['win_rate'] = 0.0
        
        return {k: dict(v) for k, v in matrix.items()}
    
    def get_scenarios(self) -> List[str]:
        """Get list of unique scenarios played."""
        return list(set(m.scenario_name for m in self.matches))


class TournamentRunner:
    """
    Orchestrates running a complete tournament between AI generals.
    
    Handles:
    - All pairwise matchups including reflexive (X vs X)
    - Position alternation for fairness
    - Multiple rounds per matchup
    - Result collection
    """
    
    # Available generals
    AVAILABLE_GENERALS = ['BRAINDEAD', 'DAFT', 'SOMEIQ']
    
    # Available scenarios
    SCENARIO_MAP = {
        'classical_medieval_battle': PredefinedScenarios.classic_medieval_battle,
        'defensive_siege': PredefinedScenarios.defensive_siege,
        'cavalry_charge': PredefinedScenarios.cavalry_charge,
        'cannae_envelopment': PredefinedScenarios.cannae_envelopment,
        'british_square': PredefinedScenarios.british_square,
    }
    
    def __init__(self, config: TournamentConfig):
        """
        Initialize tournament runner.
        
        @param config: Tournament configuration
        """
        self.config = config
        self.results = TournamentResults(config=config)
        self.simulation_controller = SimulationController()
    
    def run(self) -> TournamentResults:
        """
        Run the complete tournament.
        
        For each scenario and each pair of generals (including X vs X),
        runs the specified number of rounds, alternating positions if configured.
        
        @return: Complete tournament results
        """
        total_matchups = (
            len(self.config.generals) ** 2 * 
            len(self.config.scenarios) * 
            self.config.rounds_per_matchup
        )
        
        print(f"\n{'='*60}")
        print(f"TOURNAMENT START")
        print(f"{'='*60}")
        print(f"Generals: {self.config.generals}")
        print(f"Scenarios: {self.config.scenarios}")
        print(f"Rounds per matchup: {self.config.rounds_per_matchup}")
        print(f"Alternate positions: {self.config.alternate_positions}")
        print(f"Total matches: {total_matchups}")
        print(f"{'='*60}\n")
        
        match_count = 0
        
        for scenario_name in self.config.scenarios:
            print(f"\n--- Scenario: {scenario_name} ---")
            
            if scenario_name not in self.SCENARIO_MAP:
                print(f"  WARNING: Unknown scenario '{scenario_name}', skipping")
                continue
            
            for general_a_name in self.config.generals:
                for general_b_name in self.config.generals:
                    print(f"  {general_a_name} vs {general_b_name}: ", end='', flush=True)
                    
                    wins_a = 0
                    wins_b = 0
                    draws = 0
                    
                    for round_num in range(self.config.rounds_per_matchup):
                        # Alternate positions every other round if configured
                        if self.config.alternate_positions and round_num % 2 == 1:
                            result = self._run_match(
                                general_b_name, general_a_name, 
                                scenario_name, swap_result=True
                            )
                        else:
                            result = self._run_match(
                                general_a_name, general_b_name, 
                                scenario_name
                            )
                        
                        self.results.add_match(result)
                        match_count += 1
                        
                        if result.is_draw:
                            draws += 1
                            print('D', end='', flush=True)
                        elif result.winner == 'A':
                            wins_a += 1
                            print('A', end='', flush=True)
                        else:
                            wins_b += 1
                            print('B', end='', flush=True)
                    
                    print(f" | {general_a_name}: {wins_a}, {general_b_name}: {wins_b}, Draws: {draws}")
        
        print(f"\n{'='*60}")
        print(f"TOURNAMENT COMPLETE - {match_count} matches played")
        print(f"{'='*60}\n")
        
        return self.results
    
    def _run_match(self, general_a_name: str, general_b_name: str, 
                   scenario_name: str, swap_result: bool = False) -> MatchResult:
        """
        Run a single match.
        
        @param general_a_name: Name of general for Team A
        @param general_b_name: Name of general for Team B
        @param scenario_name: Name of scenario to use
        @param swap_result: If True, swap the general names in result (for position alternation)
        @return: Match result
        """
        # Create fresh scenario
        scenario = self.SCENARIO_MAP[scenario_name]()
        
        # Create generals
        general_a = self._create_general(general_a_name, scenario.units_a, scenario.units_b)
        general_b = self._create_general(general_b_name, scenario.units_b, scenario.units_a)
        
        scenario.general_a = general_a
        scenario.general_b = general_b
        
        # Store initial counts
        initial_a = len(scenario.units_a)
        initial_b = len(scenario.units_b)
        
        # Run simulation using SimulationController
        self.simulation_controller.initialize_simulation(
            scenario,
            tick_speed=5,
            paused=False,
            unlocked=True
        )
        
        # Run synchronously (not in thread) for tournament
        output = self.simulation_controller.simulation.simulate()
        
        # Collect results
        ticks = output.get('ticks', 0)
        survivors_a = sum(1 for u in scenario.units_a if u.hp > 0)
        survivors_b = sum(1 for u in scenario.units_b if u.hp > 0)
        casualties_a = initial_a - survivors_a
        casualties_b = initial_b - survivors_b
        
        # Determine winner
        is_draw = False
        if survivors_a > 0 and survivors_b == 0:
            winner = 'A'
        elif survivors_b > 0 and survivors_a == 0:
            winner = 'B'
        else:
            # Draw (timeout or both teams have survivors/both eliminated)
            winner = None
            is_draw = True
        
        # Handle position swap for alternation
        if swap_result:
            # Swap back the names to reflect original matchup
            result_general_a = general_b_name
            result_general_b = general_a_name
            # Also swap winner perspective
            if winner == 'A':
                winner = 'B'
            elif winner == 'B':
                winner = 'A'
            # Swap stats
            survivors_a, survivors_b = survivors_b, survivors_a
            casualties_a, casualties_b = casualties_b, casualties_a
        else:
            result_general_a = general_a_name
            result_general_b = general_b_name
        
        return MatchResult(
            general_a=result_general_a,
            general_b=result_general_b,
            scenario_name=scenario_name,
            winner=winner,
            ticks=ticks,
            team_a_survivors=survivors_a,
            team_b_survivors=survivors_b,
            team_a_casualties=casualties_a,
            team_b_casualties=casualties_b,
            is_draw=is_draw
        )
    
    def _create_general(self, name: str, units_a, units_b) -> General:
        """Create a general with the specified AI strategy."""
        name_up = name.upper()
        
        if name_up == 'BRAINDEAD':
            strategy_map = {
                UnitType.CROSSBOWMAN: StrategieBrainDead(None),
                UnitType.KNIGHT: StrategieBrainDead(None),
                UnitType.PIKEMAN: StrategieBrainDead(None),
            }
            return General(unitsA=units_a, unitsB=units_b, sS=None, sT=strategy_map)
        
        elif name_up == 'DAFT':
            strategy_map = {
                UnitType.CROSSBOWMAN: StrategieDAFT(None),
                UnitType.KNIGHT: StrategieDAFT(None),
                UnitType.PIKEMAN: StrategieDAFT(None),
            }
            return General(unitsA=units_a, unitsB=units_b, sS=None, sT=strategy_map)
        
        elif name_up == 'SOMEIQ':
            strategy_map = {
                UnitType.CROSSBOWMAN: StrategieCrossbowmanSomeIQ(),
                UnitType.KNIGHT: StrategieKnightSomeIQ(),
                UnitType.PIKEMAN: StrategiePikemanSomeIQ(),
            }
            start_strategy = StrategieStartSomeIQ()
            return General(unitsA=units_a, unitsB=units_b, sS=start_strategy, sT=strategy_map)
        
        else:
            raise ValueError(f"Unknown general: {name}. Available: {self.AVAILABLE_GENERALS}")


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
            <h1>🏆 Tournament Report</h1>
            <p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </header>
        
        <section class="config">
            <h2>Tournament Configuration</h2>
            <div class="config-grid">
                <div class="config-item">
                    <span class="label">Generals:</span>
                    <span class="value">{', '.join(generals)}</span>
                </div>
                <div class="config-item">
                    <span class="label">Scenarios:</span>
                    <span class="value">{', '.join(scenarios)}</span>
                </div>
                <div class="config-item">
                    <span class="label">Rounds per Matchup:</span>
                    <span class="value">{results.config.rounds_per_matchup}</span>
                </div>
                <div class="config-item">
                    <span class="label">Position Alternation:</span>
                    <span class="value">{'Yes' if results.config.alternate_positions else 'No'}</span>
                </div>
                <div class="config-item">
                    <span class="label">Total Matches:</span>
                    <span class="value">{len(results.matches)}</span>
                </div>
            </div>
        </section>
        
        <section class="overall">
            <h2>📊 Overall Standings</h2>
            <p class="description">General scores across all opponents and scenarios (percentage of victories)</p>
            {self._generate_overall_table(overall, generals)}
        </section>
        
        <section class="gvg">
            <h2>⚔️ General vs General (All Scenarios)</h2>
            <p class="description">Win rate when row general plays as Team A against column general</p>
            {self._generate_matrix_table(gvg, generals, generals)}
        </section>
        
        <section class="per-scenario">
            <h2>📋 General vs General (Per Scenario)</h2>
            {self._generate_per_scenario_matrices(results, generals, scenarios)}
        </section>
        
        <section class="gvs">
            <h2>🗺️ General vs Scenario</h2>
            <p class="description">General performance on each scenario (across all opponents)</p>
            {self._generate_gvs_table(gvs, generals, scenarios)}
        </section>
        
        <section class="reflexive">
            <h2>🔄 Reflexive Matchups (X vs X)</h2>
            <p class="description">Self-play results - should be ~50% with position alternation to verify no player-position bias</p>
            {self._generate_reflexive_table(results, generals)}
        </section>
        
        <footer>
            <p>MedievAIl bAIttle generAIl - Tournament System</p>
        </footer>
    </div>
</body>
</html>'''
        
        return html
    
    def _get_css(self) -> str:
        """Get CSS styles for the report."""
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
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-color);
            color: var(--primary-color);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        
        header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .timestamp {
            opacity: 0.8;
        }
        
        section {
            background: var(--card-bg);
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        section h2 {
            color: var(--primary-color);
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--accent-color);
        }
        
        .description {
            color: var(--secondary-color);
            margin-bottom: 20px;
            font-style: italic;
        }
        
        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .config-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 15px;
            background: var(--bg-color);
            border-radius: 5px;
        }
        
        .config-item .label {
            font-weight: bold;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        th, td {
            padding: 12px 15px;
            text-align: center;
            border: 1px solid #ddd;
        }
        
        th {
            background: var(--primary-color);
            color: white;
            font-weight: bold;
        }
        
        tr:nth-child(even) {
            background: var(--bg-color);
        }
        
        tr:hover {
            background: #e3e8ed;
        }
        
        .win-rate {
            font-weight: bold;
        }
        
        .win-rate.high {
            color: var(--success-color);
        }
        
        .win-rate.medium {
            color: var(--warning-color);
        }
        
        .win-rate.low {
            color: var(--danger-color);
        }
        
        .matrix-cell {
            min-width: 80px;
        }
        
        .self-play {
            background: #f0f0f0 !important;
            font-style: italic;
        }
        
        .scenario-section {
            margin-top: 25px;
            padding: 20px;
            background: var(--bg-color);
            border-radius: 8px;
        }
        
        .scenario-section h3 {
            color: var(--secondary-color);
            margin-bottom: 15px;
        }
        
        footer {
            text-align: center;
            padding: 20px;
            color: var(--secondary-color);
            font-size: 0.9rem;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: bold;
        }
        
        .badge.gold {
            background: linear-gradient(135deg, #ffd700, #ffb347);
            color: #5d4e37;
        }
        
        .badge.silver {
            background: linear-gradient(135deg, #c0c0c0, #a8a8a8);
            color: #333;
        }
        
        .badge.bronze {
            background: linear-gradient(135deg, #cd7f32, #b87333);
            color: white;
        }
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
                <h3>📍 {scenario}</h3>
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
