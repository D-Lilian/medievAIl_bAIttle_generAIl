# -*- coding: utf-8 -*-
"""
@file results.py
@brief Tournament Results Data Structures

@details
Defines data structures for storing and analyzing tournament results.
Follows Single Responsibility Principle - only handles result storage and aggregation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

from Tournament.config import TournamentConfig


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
        for g in matrix:
            for s in matrix[g]:
                data = matrix[g][s]
                if data['total'] > 0:
                    data['win_rate'] = data['wins'] / data['total'] * 100
                else:
                    data['win_rate'] = 0.0
        
        return {k: dict(v) for k, v in matrix.items()}
    
    def get_scenarios(self) -> List[str]:
        """Get list of unique scenarios played in the tournament."""
        return list(set(match.scenario_name for match in self.matches))
