# -*- coding: utf-8 -*-
"""
@file renderers/map_renderer.py
@brief Renders the game map and units.

@details
Handles drawing the battlefield border and unit positions.
Follows Single Responsibility Principle.
"""

import curses
from typing import List

from View.renderers.base_renderer import BaseRenderer
from View.data_types import Team, ColorPair, UnitRepr
from View.state import Camera


class MapRenderer(BaseRenderer):
    """
    @brief Renders the game map and units.
    """

    def draw(self, units: List[UnitRepr], camera: Camera,
             board_w: int, board_h: int, show_ui: bool) -> None:
        """
        @brief Draw map with units.
        @param units List of unit representations
        @param camera Camera object
        @param board_w Board width
        @param board_h Board height
        @param show_ui Whether UI is shown
        """
        max_y, max_x = self.stdscr.getmaxyx()
        game_height = max_y - (5 if show_ui else 0)

        # Prepare screen for redraw; flicker is prevented by double buffering (noutrefresh/doupdate)
        self.stdscr.erase()
        self._draw_border(max_x, game_height)

        # Draw units
        for unit in units:
            if not unit.alive:
                continue

            screen_x = int((unit.x - camera.x) / camera.zoom_level) + 1
            screen_y = int((unit.y - camera.y) / camera.zoom_level) + 1

            if 1 <= screen_x < max_x - 1 and 1 <= screen_y < game_height - 1:
                char, attr = self._get_unit_display(unit)
                self.safe_addstr(screen_y, screen_x, char, attr)

    def _draw_border(self, width: int, height: int) -> None:
        """
        @brief Draw decorative border.
        @param width Border width
        @param height Border height
        """
        ui_attr = curses.color_pair(ColorPair.UI.value)

        # Corners
        self.safe_addch(0, 0, '┌', ui_attr)
        self.safe_addch(0, width - 1, '┐', ui_attr)
        self.safe_addch(height - 1, 0, '└', ui_attr)
        self.safe_addch(height - 1, width - 1, '┘', ui_attr)

        # Horizontal lines
        for x in range(1, width - 1):
            self.safe_addch(0, x, '─', ui_attr)
            self.safe_addch(height - 1, x, '─', ui_attr)

        # Vertical lines
        for y in range(1, height - 1):
            self.safe_addch(y, 0, '│', ui_attr)
            self.safe_addch(y, width - 1, '│', ui_attr)

    def _get_unit_display(self, unit: UnitRepr) -> tuple:
        """
        @brief Get character and attributes for unit.
        @param unit Unit representation
        @return Tuple of (character, attributes)
        """
        color = ColorPair.TEAM_A if unit.team == Team.A else ColorPair.TEAM_B
        attr = curses.color_pair(color.value) | curses.A_BOLD
        return unit.letter, attr
