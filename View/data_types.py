# -*- coding: utf-8 -*-
"""
@file data_types.py
@brief View data types - enums and data classes for the terminal view.

@details
Contains all data structures used for rendering units in the terminal view.
Follows Single Responsibility Principle: only data definitions, no logic.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Optional


# =============================================================================
# ENUMS
# =============================================================================

class Team(Enum):
    """
    @brief Team identifiers compatible with Model's A/B convention.
    """
    A = 1  ##< Team A identifier
    B = 2  ##< Team B identifier


class UnitStatus(Enum):
    """
    @brief Unit status for rendering.
    """
    ALIVE = auto()  ##< Unit is alive
    DEAD = auto()   ##< Unit is dead


class ColorPair(Enum):
    """
    @brief Curses color pairs.
    """
    TEAM_A = 1  ##< Color for Team A
    TEAM_B = 2  ##< Color for Team B
    UI = 3      ##< Color for UI elements
    DEAD = 4    ##< Color for dead units


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class UnitRepr:
    """
    @brief View representation of a unit (separates Model from View).

    Only contains data needed for rendering.
    """
    type: str
    team: Team
    uid: int
    letter: str
    x: float
    y: float
    hp: int
    hp_max: int
    status: UnitStatus
    damage_dealt: int = 0
    target_name: Optional[str] = None
    target_uid: Optional[int] = None
    # Optional detailed stats for reports
    armor: Optional[dict] = None
    attack: Optional[dict] = None
    range: Optional[float] = None
    reload_time: Optional[float] = None
    reload_val: Optional[float] = None
    speed: Optional[float] = None
    accuracy: Optional[float] = None

    @property
    def alive(self) -> bool:
        return self.status == UnitStatus.ALIVE

    @property
    def hp_percent(self) -> float:
        return (self.hp / self.hp_max * 100) if self.hp_max > 0 else 0.0


# =============================================================================
# UNIT LETTERS MAPPING
# =============================================================================

## @brief Mapping of unit types to display letters
UNIT_LETTERS: Dict[str, str] = {
    'Knight': 'K', 'Pikeman': 'P', 'Crossbowman': 'C',
    'Long Swordsman': 'L', 'Elite Skirmisher': 'S', 'Cavalry Archer': 'A',
    'Onager': 'O', 'Light Cavalry': 'V', 'Scorpion': 'R',
    'Capped Ram': 'M', 'Trebuchet': 'T', 'Elite War Elephant': 'E',
    'Monk': 'N', 'Castle': '#', 'Wonder': 'W'
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def resolve_letter(unit_type: str) -> str:
    """
    @brief Get display letter for unit type.
    @param unit_type The unit type name
    @return Display letter or first uppercase letter if not found
    """
    return UNIT_LETTERS.get(unit_type, unit_type[:1].upper() if unit_type else '?')


def resolve_team(team_val) -> Team:
    """
    @brief Convert various team representations to Team enum.
    @param team_val The team value to convert
    @return Team.A or Team.B
    """
    # If already a Team enum, return as is
    if isinstance(team_val, Team):
        return team_val
    # If it has a 'name' attribute, check for 'A' or 'B'
    if hasattr(team_val, 'name'):
        if team_val.name == 'A':
            return Team.A
        elif team_val.name == 'B':
            return Team.B
    # If it has a 'value' attribute, use it if it matches Team.A or Team.B
    if hasattr(team_val, 'value'):
        if getattr(team_val, 'value') == Team.A.value:
            return Team.A
        elif getattr(team_val, 'value') == Team.B.value:
            return Team.B
    # Accept integer or string representations
    if team_val in (1, 'A', 'a'):
        return Team.A
    elif team_val in (2, 'B', 'b'):
        return Team.B
    # Fallback: default to Team.A for unknown values
    return Team.A
