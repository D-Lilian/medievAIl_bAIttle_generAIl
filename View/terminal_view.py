# -*- coding: utf-8 -*-
"""
@file terminal_view.py
@brief Terminal View - curses-based medieval battle viewer

@details
MVC implementation: displays the Model state without modifying it.
This is the main facade that coordinates all view components.

@controls
P(pause) M(zoom) A(auto-cam) ZQSD(scroll +Maj=fast) F1-F4(panels) TAB(report) ESC(quit)

@architecture
This module has been refactored following SOLID principles:
- data_types.py: Enums and data classes (Team, UnitRepr, etc.)
- state.py: Camera and ViewState classes
- stats.py: Statistics tracking
- input_handler.py: Keyboard input handling
- renderers/: Renderer classes (Map, UI, Debug)
- unit_cache.py: Unit data caching
- report_generator.py: HTML report generation
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable
import curses
import time

# Import from refactored modules
from View.data_types import Team, UnitStatus, ColorPair, UnitRepr, UNIT_LETTERS, resolve_letter, resolve_team
from View.state import Camera, ViewState
from View.stats import Stats
from View.input_handler import InputHandler
from View.renderers import MapRenderer, UIRenderer, DebugRenderer
from View.unit_cache import UnitCacheManager
from View.report_generator import ReportGenerator


# =============================================================================
# VIEW INTERFACE
# =============================================================================

class ViewInterface(ABC):
    """
    @brief Abstract interface for views (Dependency Inversion).
    """

    @abstractmethod
    def update(self, simulation) -> bool:
        """
        @brief Update display.
        @param simulation Simulation object
        @return False to quit, True to continue
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        @brief Clean up resources.
        """
        pass


# =============================================================================
# MAIN TERMINAL VIEW
# =============================================================================

class TerminalView(ViewInterface):
    """
    @brief Main terminal view using curses.

    Follows SOLID:
    - Single Responsibility: Coordinates components, doesn't do everything itself
    - Open/Closed: Renderers can be extended without modifying this class
    - Dependency Inversion: Uses abstract interfaces where possible
    """

    def __init__(self, board_width: int, board_height: int, tick_speed: int = 5):
        """
        @brief Initialize terminal view.
        @param board_width Board width
        @param board_height Board height
        @param tick_speed Initial tick speed (defaults to DEFAULT_NUMBER_OF_TICKS_PER_SECOND)
        """
        self.board_width = board_width
        self.board_height = board_height

        # State
        self.state = ViewState(tick_speed=tick_speed)
        self.stats = Stats()
        self.camera = Camera(
            x=max(0, board_width // 2 - 40),
            y=max(0, board_height // 2 - 20)
        )

        # Components (will be initialized in init_curses)
        self.stdscr = None
        self.input_handler: Optional[InputHandler] = None
        self.map_renderer: Optional[MapRenderer] = None
        self.ui_renderer: Optional[UIRenderer] = None
        self.debug_renderer: Optional[DebugRenderer] = None
        self.unit_cache = UnitCacheManager()
        self.report_generator = ReportGenerator(board_width, board_height)

        # Callbacks
        self.on_quick_save: Optional[Callable] = None
        self.on_report_requested: Optional[Callable] = None

        # FPS tracking
        self._last_frame = time.perf_counter()

    # Properties for backward compatibility
    @property
    def paused(self) -> bool:
        """
        @brief Get paused state.
        @return True if paused
        """
        return self.state.paused

    @paused.setter
    def paused(self, value: bool):
        """
        @brief Set paused state.
        @param value New paused state
        """
        self.state.paused = value

    @property
    def tick_speed(self) -> int:
        """
        @brief Get tick speed.
        @return Current tick speed
        """
        return self.state.tick_speed

    @tick_speed.setter
    def tick_speed(self, value: int):
        """
        @brief Set tick speed.
        @param value New tick speed
        """
        self.state.tick_speed = value

    @property
    def show_ui(self) -> bool:
        """
        @brief Get UI visibility.
        @return True if UI is shown
        """
        return self.state.show_ui

    def init_curses(self) -> None:
        """
        @brief Initialize curses environment.
        """
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)

        # Color pairs
        curses.init_pair(ColorPair.TEAM_A.value, curses.COLOR_CYAN, -1)
        curses.init_pair(ColorPair.TEAM_B.value, curses.COLOR_RED, -1)
        curses.init_pair(ColorPair.UI.value, curses.COLOR_YELLOW, -1)
        curses.init_pair(ColorPair.DEAD.value, curses.COLOR_BLACK, -1)

        # Initialize components
        self.map_renderer = MapRenderer(self.stdscr)
        self.ui_renderer = UIRenderer(self.stdscr)
        self.debug_renderer = DebugRenderer(self.stdscr)
        self.input_handler = InputHandler(
            self.stdscr, self.state, self.camera,
            self.board_width, self.board_height
        )
        self.input_handler.on_report_requested = self.generate_html_report

    def cleanup(self) -> None:
        """
        @brief Restore terminal.
        """
        if self.stdscr:
            self.stdscr.keypad(False)
            curses.nocbreak()
            curses.echo()
            curses.endwin()

    def update(self, simulation) -> bool:
        """
        @brief Main update loop.
        @param simulation Simulation object
        @return False to quit, True to continue
        """
        # Handle input
        if not self.input_handler.process():
            return False

        # Update data if not paused
        if not self.state.paused:
            self.unit_cache.update(simulation, self.stats)
            self._update_camera()

        # Render
        self._render()

        # FPS control
        self._control_framerate()
        return True

    def _update_camera(self) -> None:
        """
        @brief Update camera position.
        @details If auto_follow is enabled, centers camera on units barycenter.
        """
        max_y, max_x = self.stdscr.getmaxyx()
        ui_h = 5 if self.state.show_ui else 0
        
        # Auto-follow: center camera on units barycenter
        if self.state.auto_follow and self.unit_cache.units:
            alive_units = [u for u in self.unit_cache.units if u.alive]
            if alive_units:
                center_x = sum(u.x for u in alive_units) / len(alive_units)
                center_y = sum(u.y for u in alive_units) / len(alive_units)
                
                # Calculate visible area
                visible_w = (max_x - 2) * self.camera.zoom_level
                visible_h = (max_y - ui_h - 2) * self.camera.zoom_level
                
                # Center camera on barycenter
                self.camera.x = int(center_x - visible_w / 2)
                self.camera.y = int(center_y - visible_h / 2)
        
        self.camera.clamp(self.board_width, self.board_height, max_x, max_y, ui_h)

    def _render(self) -> None:
        """
        @brief Render all components.
        """
        self.map_renderer.draw(
            self.unit_cache.units, self.camera,
            self.board_width, self.board_height, self.state.show_ui
        )
        self.ui_renderer.draw(
            self.state, self.stats, self.camera,
            len(self.unit_cache.units)
        )
        self.debug_renderer.draw(self.unit_cache.units, self.state.show_debug)

        if self.state.paused:
            self.ui_renderer.draw_pause_overlay()

        # Use noutrefresh + doupdate for double buffering (prevents flickering)
        self.stdscr.noutrefresh()
        curses.doupdate()

    def _control_framerate(self) -> None:
        """
        @brief Control framerate and compute FPS.
        """
        target_frame = 1.0 / max(1, self.state.tick_speed)
        start = self._last_frame
        now = time.perf_counter()
        work_time = now - start

        # Sleep the remaining budget to keep a steady frame time
        sleep_time = max(0.0, target_frame - work_time)
        if sleep_time > 0:
            time.sleep(sleep_time)

        end = time.perf_counter()
        frame_time = end - start
        if frame_time > 0:
            self.stats.fps = 1.0 / frame_time
        self._last_frame = end

    def generate_html_report(self) -> None:
        """
        @brief Generate HTML battle report.
        @details Delegates to ReportGenerator.
        """
        self.report_generator.generate(self.unit_cache.units, self.stats)

    def debug_snapshot(self) -> dict:
        """
        @brief Return stats snapshot for tests.
        @return Dictionary with debug stats
        """
        return {
            "time": self.stats.simulation_time,
            "team1_alive": self.stats.team1_alive,
            "team2_alive": self.stats.team2_alive,
            "team1_dead": self.stats.team1_dead,
            "team2_dead": self.stats.team2_dead,
            "types_team1": dict(self.stats.type_counts_team1),
            "types_team2": dict(self.stats.type_counts_team2),
            "total_units_cached": len(self.unit_cache.units)
        }
