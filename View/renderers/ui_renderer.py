# -*- coding: utf-8 -*-
"""
@file renderers/ui_renderer.py
@brief Renders the UI panels and overlays.

@details
Handles drawing UI elements like stats, controls help, pause overlay,
and notifications.
Follows Single Responsibility Principle.
"""

import curses
import time
from typing import Dict

from View.renderers.base_renderer import BaseRenderer
from View.data_types import ColorPair
from View.state import Camera, ViewState
from View.stats import Stats


class UIRenderer(BaseRenderer):
    """Renders the UI panels."""

    def draw(self, state: ViewState, stats: Stats, camera: Camera,
             units_count: int) -> None:
        """Draw UI panels based on visibility flags."""
        if not state.show_ui:
            return

        max_y, max_x = self.stdscr.getmaxyx()
        ui_y = max_y - 5
        ui_attr = curses.color_pair(ColorPair.UI.value)

        # Separator
        self.safe_addstr(ui_y, 0, "─" * max_x, ui_attr)

        line = ui_y + 1

        # F1: Unit counts
        if state.show_unit_counts:
            text = (f"T1 Alive:{stats.team1_alive} Dead:{stats.team1_dead} | "
                    f"T2 Alive:{stats.team2_alive} Dead:{stats.team2_dead} | "
                    f"Total:{units_count}")
            self.safe_addstr(line, 2, text, ui_attr | curses.A_BOLD)
            line += 1

        # F3: Simulation info
        if state.show_sim_info:
            pause_str = 'PAUSE' if state.paused else 'PLAY'
            follow_str = 'AUTO' if state.auto_follow else 'MANUAL'
            text = (f"Time:{stats.simulation_time:.1f}s | {pause_str} | "
                    f"Zoom:x{camera.zoom_level} | Cam:({camera.x},{camera.y}) | "
                    f"{follow_str} | Tick:{state.tick_speed}")
            self.safe_addstr(line, 2, text)
            line += 1

        # F2: Unit types
        if state.show_unit_types:
            summary = self._build_type_summary(stats)
            if summary:
                self.safe_addstr(line, 2, summary, ui_attr)
                line += 1

        # Help line
        help_text = "P:Pause M:Zoom +/-:Tick ZQSD:Scroll(+Maj) F1-F4:Panels E:Save TAB:Report F9:2.5D ESC:Quit"
        self.safe_addstr(line, 2, help_text, ui_attr)

        # Notification overlay
        if state.notification:
            if time.time() - state.notification_time < 3.0:  # Show for 3 seconds
                self._draw_notification(state.notification)
            else:
                state.notification = None

    def _draw_notification(self, msg: str) -> None:
        """
        @brief Draw notification message.
        @param msg Message to display
        """
        max_y, max_x = self.stdscr.getmaxyx()
        cx, cy = max_x // 2 - len(msg) // 2, 2  # Top center
        
        attr = curses.color_pair(ColorPair.UI.value) | curses.A_BOLD | curses.A_REVERSE
        self.safe_addstr(cy, cx, f" {msg} ", attr)

    def _build_type_summary(self, stats: Stats) -> str:
        """
        @brief Build unit type summary string.
        @param stats Statistics object
        @return Summary string
        """
        types = ['Knight', 'Pikeman', 'Crossbowman', 'Cavalry Archer', 'Long Swordsman']
        parts = []
        for t in types:
            c1 = stats.type_counts_team1.get(t, 0)
            c2 = stats.type_counts_team2.get(t, 0)
            if c1 or c2:
                parts.append(f"{t}:{c1}/{c2}")
        return " | ".join(parts)

    def draw_pause_overlay(self) -> None:
        """
        @brief Draw pause overlay in center.
        """
        max_y, max_x = self.stdscr.getmaxyx()
        msg = "PAUSED - Press P to resume"
        cx, cy = max_x // 2 - len(msg) // 2, max_y // 2

        attr = curses.color_pair(ColorPair.UI.value) | curses.A_BOLD | curses.A_REVERSE

        # Background box
        for dy in range(-1, 2):
            for dx in range(-2, len(msg) + 2):
                self.safe_addstr(cy + dy, cx + dx, ' ', attr)

        self.safe_addstr(cy, cx, msg, attr)
