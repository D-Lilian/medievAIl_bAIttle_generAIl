# -*- coding: utf-8 -*-
"""
@file state.py
@brief View state management - Camera and ViewState classes.

@details
Manages the state of the terminal view including camera position,
zoom level, UI visibility, and pause state.
Follows Single Responsibility Principle.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Camera:
    """
    @brief Camera position and zoom management.
    @details Single Responsibility: only handles camera logic.
    """
    x: int = 0  ##< Camera x position
    y: int = 0  ##< Camera y position
    zoom_level: int = 1  ##< Current zoom level (1-3)
    scroll_speed_normal: int = 5  ##< Normal scroll speed
    scroll_speed_fast: int = 15  ##< Fast scroll speed (shift)

    def move(self, dx: int, dy: int, fast: bool = False) -> None:
        """
        @brief Move camera by delta, optionally fast.
        @param dx Delta x movement
        @param dy Delta y movement
        @param fast Whether to use fast speed
        """
        speed = self.scroll_speed_fast if fast else self.scroll_speed_normal
        self.x += dx * speed * self.zoom_level
        self.y += dy * speed * self.zoom_level

    def toggle_zoom(self) -> None:
        """
        @brief Cycle through zoom levels 1-2-3.
        """
        self.zoom_level = (self.zoom_level % 3) + 1

    def clamp(self, board_w: int, board_h: int, term_w: int, term_h: int, ui_h: int = 0) -> None:
        """
        @brief Constrain camera within board bounds.
        @param board_w Board width
        @param board_h Board height
        @param term_w Terminal width
        @param term_h Terminal height
        @param ui_h UI height offset
        """
        visible_w = int(term_w * self.zoom_level)
        visible_h = int((term_h - ui_h) * self.zoom_level)
        self.x = max(0, min(self.x, max(0, board_w - visible_w)))
        self.y = max(0, min(self.y, max(0, board_h - visible_h)))


@dataclass
class ViewState:
    """
    @brief Centralized view state (KISS: single source of truth).
    """
    paused: bool = False  ##< Whether simulation is paused
    show_ui: bool = True  ##< Whether to show UI panels
    show_debug: bool = False  ##< Whether to show debug overlay
    show_unit_counts: bool = True   ##< F1: Show unit counts panel
    show_unit_types: bool = True    ##< F2: Show unit types panel
    show_sim_info: bool = True      ##< F3: Show simulation info panel
    auto_follow: bool = False  ##< Whether camera auto-follows units
    tick_speed: int = 5  ##< Simulation tick speed
    notification: Optional[str] = None  ##< Temporary notification message
    notification_time: float = 0.0  ##< Time when notification was set

    def toggle_all_panels(self) -> None:
        """
        @brief F4: Toggle all UI panels at once.
        """
        all_on = self.show_unit_counts and self.show_unit_types and self.show_sim_info
        self.show_unit_counts = not all_on
        self.show_unit_types = not all_on
        self.show_sim_info = not all_on
        self.show_ui = not all_on
