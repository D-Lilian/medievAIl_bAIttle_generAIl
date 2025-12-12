# -*- coding: utf-8 -*-
"""
@file terminal_view.py
@brief Terminal View - curses-based medieval battle viewer

@details
MVC implementation: displays the Model state without modifying it.
Refactored following SOLID and KISS principles.

@controls
P(pause) M(zoom) A(auto-cam) ZQSD(scroll +Maj=fast) F1-F4(panels) TAB(report) ESC/Q(quit)
"""

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Dict, Optional, Callable
import curses
import time

from Model.simulation import DEFAULT_NUMBER_OF_TICKS_PER_SECOND


# =============================================================================
# ENUMS & DATA CLASSES
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


@dataclass
class UnitRepr:
    """
    @brief View representation of a unit (separates Model from View).

    Only contains data needed for rendering.
    """
    type: str
    team: Team
    letter: str
    x: float
    y: float
    hp: int
    hp_max: int
    status: UnitStatus
    damage_dealt: int = 0
    target_name: Optional[str] = None
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
    tick_speed: int = DEFAULT_NUMBER_OF_TICKS_PER_SECOND  ##< Simulation tick speed

    def toggle_all_panels(self) -> None:
        """
        @brief F4: Toggle all UI panels at once.
        """
        all_on = self.show_unit_counts and self.show_unit_types and self.show_sim_info
        self.show_unit_counts = not all_on
        self.show_unit_types = not all_on
        self.show_sim_info = not all_on
        self.show_ui = not all_on


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


# =============================================================================
# INPUT HANDLER (Single Responsibility)
# =============================================================================

class InputHandler:
    """
    @brief Handles all keyboard input.
    @details Single Responsibility: only processes input, returns actions.
    """

    # Key mappings for cleaner code
    QUIT_KEYS = {27, ord('q'), ord('Q')}  # ESC or Q
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
        self.on_quick_load: Optional[Callable] = None

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

        # F11/F12: Save/Load (placeholders)
        if key == curses.KEY_F11 and self.on_quick_save:
            self.on_quick_save()
            return True
        if key == curses.KEY_F12 and self.on_quick_load:
            self.on_quick_load()
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


# =============================================================================
# RENDERERS (Single Responsibility + Open/Closed)
# =============================================================================

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
                    f"{follow_str} | Tick:{state.tick_speed} | FPS:{stats.fps:.0f}")
            self.safe_addstr(line, 2, text)
            line += 1

        # F2: Unit types
        if state.show_unit_types:
            summary = self._build_type_summary(stats)
            if summary:
                self.safe_addstr(line, 2, summary, ui_attr)
                line += 1

        # Help line
        help_text = "P:Pause M:Zoom +/-:Tick ZQSD:Scroll(+Maj) F1-F4:Panels TAB:Report ESC:Quit"
        self.safe_addstr(line, 2, help_text, ui_attr)

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


# =============================================================================
# UNIT CACHE MANAGER (Single Responsibility)
# =============================================================================

class UnitCacheManager:
    """
    @brief Manages unit data extraction and caching.
    """

    def __init__(self):
        """
        @brief Initialize cache manager.
        """
        self.units: List[UnitRepr] = []
        self._all_units: Dict[int, UnitRepr] = {}
        self._hp_memory: Dict[int, int] = {}

    def update(self, simulation, stats: Stats) -> None:
        """
        @brief Update cache from simulation.
        @param simulation Simulation object
        @param stats Statistics to update
        """
        stats.reset()

        raw_units = self._get_units(simulation)
        current_ids = set()

        for unit in raw_units:
            if not hasattr(unit, 'hp'):
                continue

            uid = id(unit)
            current_ids.add(uid)
            repr_unit = self._create_repr(unit, uid)
            self._all_units[uid] = repr_unit

        # Mark missing as dead
        for uid, repr_unit in self._all_units.items():
            if uid not in current_ids:
                repr_unit.status = UnitStatus.DEAD
                repr_unit.hp = 0

        # Rebuild cache and stats
        self.units = list(self._all_units.values())
        for unit in self.units:
            stats.add_unit(unit)

        # Update time
        stats.simulation_time = self._get_time(simulation)

    def _get_units(self, simulation) -> list:
        """
        @brief Extract units from simulation.
        @param simulation Simulation object
        @return List of units
        """
        if hasattr(simulation, 'scenario') and hasattr(simulation.scenario, 'units'):
            return simulation.scenario.units
        if hasattr(simulation, 'units'):
            return simulation.units
        return []

    def _get_time(self, simulation) -> float:
        """
        @brief Get simulation time.
        @param simulation Simulation object
        @return Time in seconds
        """
        if hasattr(simulation, 'elapsed_time'):
            return simulation.elapsed_time
        if hasattr(simulation, 'tick'):
            tick_speed = getattr(simulation, 'tick_speed', DEFAULT_NUMBER_OF_TICKS_PER_SECOND)
            return simulation.tick / tick_speed
        return 0.0

    def _create_repr(self, unit, uid: int) -> UnitRepr:
        """
        @brief Create UnitRepr from model unit.
        @param unit Model unit object
        @param uid Unit ID
        @return Unit representation
        """
        hp = getattr(unit, 'hp', 0)
        hp_max = self._get_hp_max(unit, uid, hp)
        team = resolve_team(getattr(unit, 'team', getattr(unit, 'equipe', 1)))
        unit_type = getattr(unit, 'name', type(unit).__name__)

        target = getattr(unit, 'target', None)
        target_name = None
        if target:
            t_name = getattr(target, 'name', type(target).__name__)
            t_team = resolve_team(getattr(target, 'team', getattr(target, 'equipe', None)))
            target_name = f"{t_name} (Team {'A' if t_team == Team.A else 'B'})"

        return UnitRepr(
            type=unit_type,
            team=team,
            letter=resolve_letter(unit_type),
            x=getattr(unit, 'x', 0.0),
            y=getattr(unit, 'y', 0.0),
            hp=max(0, hp),
            hp_max=hp_max,
            status=UnitStatus.ALIVE if hp > 0 else UnitStatus.DEAD,
            damage_dealt=getattr(unit, 'damage_dealt', 0),
            target_name=target_name,
            armor=getattr(unit, 'armor', None),
            attack=getattr(unit, 'attack', None),
            range=getattr(unit, 'range', None),
            reload_time=getattr(unit, 'reload_time', None),
            reload_val=getattr(unit, 'reload', None),
            speed=getattr(unit, 'speed', None),
            accuracy=getattr(unit, 'accuracy', None)
        )

    def _get_hp_max(self, unit, uid: int, current_hp: int) -> int:
        """
        @brief Get or estimate hp_max.
        @param unit Unit object
        @param uid Unit ID
        @param current_hp Current HP value
        @return Maximum HP value
        """
        if hasattr(unit, 'hp_max'):
            return getattr(unit, 'hp_max')
        if uid not in self._hp_memory and current_hp > 0:
            self._hp_memory[uid] = current_hp
        return self._hp_memory.get(uid, current_hp)


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

    def __init__(self, board_width: int, board_height: int, tick_speed: int = DEFAULT_NUMBER_OF_TICKS_PER_SECOND):
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
        now = time.perf_counter()
        dt = now - self._last_frame
        if dt > 0:
            self.stats.fps = 1.0 / dt
        self._last_frame = now
        time.sleep(max(0.0, 1.0 / self.state.tick_speed))

    # =========================================================================
    # HTML REPORT GENERATION
    # =========================================================================

    def generate_html_report(self) -> None:
        """
        @brief Generate HTML battle report.
        """
        import datetime
        import os
        import webbrowser

        reports_dir = os.path.join(os.getcwd(), "Reports")
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(reports_dir, f"battle_report_{timestamp}.html")

        # Generate content
        team1 = [u for u in self.unit_cache.units if u.team == Team.A]
        team2 = [u for u in self.unit_cache.units if u.team == Team.B]

        team_sections = self._gen_team_section(1, team1) + self._gen_team_section(2, team2)
        battle_map = self._gen_battle_map(team1, team2)
        breakdown = self._gen_breakdown()
        legend = self._gen_legend()

        # Load template (CSS is referenced via relative path in template)
        base_dir = os.path.join(os.path.dirname(__file__), '..', 'Utils')
        with open(os.path.join(base_dir, 'battle_report_template.html'), 'r', encoding='utf-8') as f:
            template = f.read()

        # Fill template
        html = template.replace('{timestamp}', timestamp)
        html = html.replace('{simulation_time}', f"{self.stats.simulation_time:.2f}")
        html = html.replace('{team1_units}', str(self.stats.team1_alive))
        html = html.replace('{team2_units}', str(self.stats.team2_alive))
        html = html.replace('{total_units}', str(len(self.unit_cache.units)))
        html = html.replace('{team_sections}', team_sections)
        html = html.replace('{battle_map}', battle_map)
        html = html.replace('{breakdown_section}', breakdown)
        html = html.replace('{legend_items}', legend)
        html = html.replace('{generation_datetime}',
                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Write HTML file only (CSS is in Utils/)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)

        webbrowser.open('file://' + os.path.abspath(filename))

    def _gen_unit_html(self, i: int, unit: UnitRepr, team: int) -> str:
        """
        @brief Generate HTML for single unit.
        @param i Unit index
        @param unit Unit representation
        @param team Team number
        @return HTML string
        """
        hp_pct = unit.hp_percent
        hp_class = "hp-critical" if hp_pct < 25 else "hp-low" if hp_pct < 50 else ""
        status = "Alive" if unit.alive else "Dead"
        uid = f"unit-{team}-{i}"

        return f'''
        <div class="unit team{team}" id="{uid}">
            <div class="unit-header">
                <span class="unit-id">#{i}</span>
                <span class="unit-type">{unit.type} ({unit.letter})</span>
                <span class="unit-status {status.lower()}">{status}</span>
            </div>
            <div class="hp-bar-container">
                <div class="hp-bar">
                    <div class="hp-fill {hp_class}" style="width: {hp_pct}%"></div>
                </div>
                <span class="hp-text">{unit.hp}/{unit.hp_max} HP</span>
            </div>
            <div class="unit-stats-grid">
                <div class="stat-item"><span class="stat-label">Pos:</span>({unit.x:.1f}, {unit.y:.1f})</div>
                <div class="stat-item"><span class="stat-label">Dmg:</span>{unit.damage_dealt}</div>
                <div class="stat-item"><span class="stat-label">Tgt:</span>{unit.target_name or 'None'}</div>
            </div>
        </div>'''

    def _gen_team_section(self, team: int, units: List[UnitRepr]) -> str:
        """
        @brief Generate HTML for team section.
        @param team Team number
        @param units List of units
        @return HTML string
        """
        units_html = "".join(self._gen_unit_html(i, u, team) for i, u in enumerate(units, 1))
        return f'''
        <div class="team-section">
            <details open>
                <summary>Team {team} - {len(units)} units</summary>
                <div class="unit-list">{units_html}</div>
            </details>
        </div>'''

    def _gen_battle_map(self, team1: List[UnitRepr], team2: List[UnitRepr]) -> str:
        """
        @brief Generate battle map HTML.
        @param team1 Team 1 units
        @param team2 Team 2 units
        @return HTML string
        """
        dots = ""
        for i, u in enumerate(team1, 1):
            if u.alive:
                dots += f'<div class="unit-cell team1" style="grid-column:{int(u.x)+1};grid-row:{int(u.y)+1}">{u.letter}</div>'
        for i, u in enumerate(team2, 1):
            if u.alive:
                dots += f'<div class="unit-cell team2" style="grid-column:{int(u.x)+1};grid-row:{int(u.y)+1}">{u.letter}</div>'

        return f'''
        <div class="battle-map-container">
            <details open>
                <summary>Battlefield ({self.board_width}x{self.board_height})</summary>
                <div class="battle-map" style="--cols:{self.board_width};--rows:{self.board_height}">{dots}</div>
            </details>
        </div>'''

    def _gen_breakdown(self) -> str:
        """
        @brief Generate breakdown section HTML.
        @return HTML string
        """
        def table(counts: Dict[str, int], title: str, color: str) -> str:
            total = sum(counts.values())
            if total == 0:
                return f'''
                <div class="breakdown-card">
                    <h4 style="color:var({color})">{title}</h4>
                    <div class="no-units-message">No units</div>
                </div>'''
            rows = "".join(
                f'<tr><td>{t}</td><td>{c}</td><td><div class="progress-bar">'
                f'<div class="progress-fill" style="width:{c/total*100}%;background:var({color})"></div>'
                f'</div></td></tr>'
                for t, c in sorted(counts.items())
            )
            return f'''
            <div class="breakdown-card">
                <h4 style="color:var({color})">{title}</h4>
                <table class="breakdown-table">
                    <thead><tr><th>Type</th><th>Count</th><th>%</th></tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>'''

        return f'''
        <div class="breakdown-container">
            <h3>Unit Breakdown</h3>
            <div class="breakdown-grid">
                {table(self.stats.type_counts_team1, "Team 1", "--team1-color")}
                {table(self.stats.type_counts_team2, "Team 2", "--team2-color")}
            </div>
        </div>'''

    def _gen_legend(self) -> str:
        """
        @brief Generate legend HTML.
        @return HTML string
        """
        return "\n".join(
            f"<li><strong>{letter}</strong>: {unit_type}</li>"
            for unit_type, letter in sorted(UNIT_LETTERS.items())
        )

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


