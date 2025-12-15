# -*- coding: utf-8 -*-
"""
@file renderers/debug_renderer.py
@brief Renders the debug overlay.

@details
Shows debug information about units when enabled.
Follows Single Responsibility Principle.
"""

import curses
from typing import List

from View.renderers.base_renderer import BaseRenderer
from View.data_types import Team, ColorPair, UnitRepr


class DebugRenderer(BaseRenderer):
    """
    @brief Renders debug overlay.
    """

    def draw(self, units: List[UnitRepr], show: bool) -> None:
        """
        @brief Draw debug info if enabled.
        @param units List of units to debug
        @param show Whether to show debug overlay
        """
        if not show:
            return

        max_y, max_x = self.stdscr.getmaxyx()
        x_pos = max_x - 50

        self.safe_addstr(1, x_pos, "═══ DEBUG ═══",
                         curses.color_pair(ColorPair.UI.value) | curses.A_BOLD)

        for i, unit in enumerate(units[:6]):
            status = "ALV" if unit.alive else "DED"
            text = f"{status} {unit.type[:10]:10} HP:{unit.hp:3}/{unit.hp_max:3} DMG:{unit.damage_dealt:3}"
            color = ColorPair.TEAM_A if unit.team == Team.A else ColorPair.TEAM_B
            if not unit.alive:
                color = ColorPair.DEAD
            self.safe_addstr(2 + i, x_pos, text[:48], curses.color_pair(color.value))
