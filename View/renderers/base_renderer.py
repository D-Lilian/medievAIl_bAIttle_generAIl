# -*- coding: utf-8 -*-
"""
@file renderers/base_renderer.py
@brief Abstract base class for all renderers.

@details
Provides common rendering utilities used by all concrete renderers.
Follows Open/Closed Principle: can be extended without modification.
"""

import curses
from abc import ABC, abstractmethod


class BaseRenderer(ABC):
    """
    @brief Abstract base for all renderers.
    """

    def __init__(self, stdscr):
        """
        @brief Initialize renderer with curses window.
        @param stdscr Curses window
        """
        self.stdscr = stdscr

    def safe_addstr(self, y: int, x: int, text: str, attr: int = 0) -> None:
        """
        @brief Safely add string, ignoring curses errors at screen edges.
        @param y Y coordinate
        @param x X coordinate
        @param text Text to add
        @param attr Curses attributes
        """
        try:
            self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            # Ignore errors when writing at the screen edges (intentional)
            pass

    def safe_addch(self, y: int, x: int, ch: str, attr: int = 0) -> None:
        """
        @brief Safely add character.
        @param y Y coordinate
        @param x X coordinate
        @param ch Character to add
        @param attr Curses attributes
        """
        try:
            self.stdscr.addch(y, x, ch, attr)
        except curses.error:
            pass
