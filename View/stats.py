# -*- coding: utf-8 -*-
"""
@file stats.py
@brief Statistics tracking for the terminal view.

@details
Tracks unit counts, types, and simulation metrics.
Follows Single Responsibility Principle.
"""

from dataclasses import dataclass, field
from typing import Dict

from View.data_types import Team, UnitRepr


@dataclass
class Stats:
    """
    @brief Statistics tracking (Single Responsibility).
    """
    team1_alive: int = 0  ##< Number of alive units in team 1
    team2_alive: int = 0  ##< Number of alive units in team 2
    team1_dead: int = 0   ##< Number of dead units in team 1
    team2_dead: int = 0   ##< Number of dead units in team 2
    type_counts_team1: Dict[str, int] = field(default_factory=dict)  ##< Unit type counts for team 1
    type_counts_team2: Dict[str, int] = field(default_factory=dict)  ##< Unit type counts for team 2
    simulation_time: float = 0.0  ##< Current simulation time in seconds
    fps: float = 0.0  ##< Current frames per second

    def reset(self) -> None:
        """
        @brief Reset all counters.
        """
        self.team1_alive = self.team2_alive = 0
        self.team1_dead = self.team2_dead = 0
        self.type_counts_team1.clear()
        self.type_counts_team2.clear()

    def add_unit(self, unit: UnitRepr) -> None:
        """
        @brief Update stats for a unit.
        @param unit The unit representation to add
        """
        is_team_a = unit.team == Team.A
        type_counts = self.type_counts_team1 if is_team_a else self.type_counts_team2

        if unit.alive:
            type_counts[unit.type] = type_counts.get(unit.type, 0) + 1
            if is_team_a:
                self.team1_alive += 1
            else:
                self.team2_alive += 1
        else:
            if is_team_a:
                self.team1_dead += 1
            else:
                self.team2_dead += 1
