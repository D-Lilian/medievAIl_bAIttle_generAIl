# -*- coding: utf-8 -*-
"""
@file input_handler.py
@brief Keyboard input handling for the terminal view.

@details
Handles all keyboard input and translates it to actions.
Follows Single Responsibility Principle: only processes input.
"""

import curses
from typing import Optional, Callable

from View.state import Camera, ViewState


class InputHandler:
    """
    @brief Handles all keyboard input.
    @details Single Responsibility: only processes input, returns actions.
    """

    # Key mappings for cleaner code
    QUIT_KEYS = {27}  # ESC only
    PAUSE_KEYS = {ord('p'), ord('P')}
    ZOOM_KEYS = {ord('m'), ord('M')}
    AUTO_FOLLOW_KEYS = {ord('a'), ord('A')}
    DEBUG_KEY = 4  # Ctrl+D
    UI_TOGGLE_KEYS = {ord('f'), ord('F')}
    REPORT_KEY = ord('\t')
    SPEED_UP_KEYS = {ord('+'), ord('=')}
    SPEED_DOWN_KEYS = {ord('-'), ord('_')}

    def __init__(self, stdscr, state: ViewState, camera: Camera,
                 board_width: int, board_height: int):
        """
        @brief Initialize input handler.
        @param stdscr Curses window
        @param state View state reference
        @param camera Camera reference
        @param board_width Board width
        @param board_height Board height
        """
        self.stdscr = stdscr
        self.state = state
        self.camera = camera
        self.board_width = board_width
        self.board_height = board_height
        self.on_report_requested: Optional[Callable] = None
        self.on_quick_save: Optional[Callable] = None

    def process(self) -> bool:
        """
        @brief Process keyboard input.
        @return False to quit, True to continue
        """
        try:
            key = self.stdscr.getch()
        except (KeyboardInterrupt, curses.error):
            return True

        if key == -1:
            return True

        # Quit
        if key in self.QUIT_KEYS:
            return False

        # Pause
        if key in self.PAUSE_KEYS:
            self.state.paused = not self.state.paused
            return True

        # Speed adjustment
        if key in self.SPEED_UP_KEYS:
            self.state.tick_speed = min(240, self.state.tick_speed + 5)
            return True
        if key in self.SPEED_DOWN_KEYS:
            self.state.tick_speed = max(1, self.state.tick_speed - 5)
            return True

        # Zoom
        if key in self.ZOOM_KEYS:
            self.camera.toggle_zoom()
            self._clamp_camera()
            return True

        # Auto-follow
        if key in self.AUTO_FOLLOW_KEYS:
            self.state.auto_follow = not self.state.auto_follow
            return True

        # Debug
        if key == self.DEBUG_KEY:
            self.state.show_debug = not self.state.show_debug
            return True

        # UI toggle
        if key in self.UI_TOGGLE_KEYS:
            self.state.show_ui = not self.state.show_ui
            return True

        # F1-F4 panel toggles
        if key == curses.KEY_F1:
            self.state.show_unit_counts = not self.state.show_unit_counts
            return True
        if key == curses.KEY_F2:
            self.state.show_unit_types = not self.state.show_unit_types
            return True
        if key == curses.KEY_F3:
            self.state.show_sim_info = not self.state.show_sim_info
            return True
        if key == curses.KEY_F4:
            self.state.toggle_all_panels()
            return True

        # E: Save
        if key in (ord('e'), ord('E')) and self.on_quick_save:
            self.on_quick_save()
            return True

        # Report
        if key == self.REPORT_KEY and self.on_report_requested:
            self.state.paused = True
            self.on_report_requested()
            return True

        # Movement (ZQSD + arrows)
        self._handle_movement(key)
        return True

    def _handle_movement(self, key: int) -> None:
        """
        @brief Handle camera movement keys.
        @param key The key pressed
        """
        movements = {
            (ord('z'), ord('Z'), curses.KEY_UP): (0, -1),
            (ord('s'), ord('S'), curses.KEY_DOWN): (0, 1),
            (ord('q'), ord('Q'), curses.KEY_LEFT): (-1, 0),
            (ord('d'), ord('D'), curses.KEY_RIGHT): (1, 0),
        }

        for keys, (dx, dy) in movements.items():
            if key in keys:
                fast = key in (ord('Z'), ord('S'), ord('Q'), ord('D'))
                self.camera.move(dx, dy, fast)
                self.state.auto_follow = False
                break

    def _clamp_camera(self) -> None:
        """
        @brief Clamp camera after zoom change.
        """
        max_y, max_x = self.stdscr.getmaxyx()
        ui_h = 5 if self.state.show_ui else 0
        self.camera.clamp(self.board_width, self.board_height, max_x, max_y, ui_h)
