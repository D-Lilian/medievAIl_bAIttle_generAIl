# -*- coding: utf-8 -*-
"""
@file terminal_view.py
@brief Terminal View - curses-based medieval battle viewer

@details
MVC implementation: displays the Model state without modifying it
- Interactive mode (curses)
- Headless mode (tests)

@author Marie
@date 2025

@usage
python terminal_view.py [--test]

@controls
P(pause) M(zoom) ZQSD(scroll) ESC(quit)
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum, auto
import curses
from typing import List
import time
import sys
import random
import os

# Add parent directory to path for Model imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Model modules
from Model.simulation import Simulation
from Model.units import Knight, Pikeman, Crossbowman, UnitType

# Monkey-patch Simulation to add a step method if it doesn't exist
if not hasattr(Simulation, 'step'):
    def simulation_step(self):
        """Execute one simulation step (tick)."""
        random.shuffle(self.units)

        for unit in self.units:
            if unit.hp <= 0:
                continue
            enemy = self.get_nearest_enemy_unit(unit)
            if enemy is None:
                unit.target = None
                continue
            unit.target = enemy
            if self.is_in_reach(unit, enemy) and unit.reload <= 0:
                self.attack_unit(unit, enemy)
                unit.reload = unit.reload_time
            else:
                self.move_unit_towards_coordinates(unit, enemy.x, enemy.y)
        
        self.tick += 1

        if self.tick % 5 == 0:
            for unit in self.units:
                self.reload_unit(unit)
                    
    Simulation.step = simulation_step


class Team(Enum):
    """
    @brief Enumeration of possible teams

    @details Defines team identifiers for the game.
    Compatible with the A/B naming convention used by the team.
    """
    A = 1  ##< Team A (cyan)
    B = 2  ##< Team B (red)


class UnitStatus(Enum):
    """
    @brief Status of a unit in the game

    @details Indicates whether a unit is alive or dead,
    used for rendering and basic game logic.
    """
    ALIVE = auto()  ##< Alive unit
    DEAD = auto()   ##< Dead unit


@dataclass
class UniteRepr:
    """
    @brief Representation of a unit for rendering

    @details Data structure containing all information needed
    to render a unit in the terminal view.
    Clearly separates Model data from View data.

    @param type Unit type name (Knight, Pikeman, etc.)
    @param team Unit team (Team.A or Team.B)
    @param letter Character used to render the unit
    @param x X position (float coordinate)
    @param y Y position (float coordinate)
    @param hp Current hit points
    @param hp_max Maximum hit points
    @param status Unit status (ALIVE/DEAD)
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
    target_id: int = None  # ID of the target unit
    
    @property
    def alive(self) -> bool:
        """
        @brief Check whether the unit is alive
        @return True if the unit is alive, False otherwise
        """
        return self.status == UnitStatus.ALIVE
    
    @property
    def hp_percent(self) -> float:
        """
        @brief Compute remaining HP percentage
        @return HP percentage (0-100)
        """
        return (self.hp / self.hp_max * 100) if self.hp_max > 0 else 0.0


class ViewInterface(ABC):
    """
    @brief Abstract interface for all views

    @details Defines the contract that all views must respect
    in the MVC architecture. Guarantees separation between View and Model.
    """
    
    @abstractmethod
    def update(self, simulation):
        """
        @brief Update display with the current simulation state
        @param simulation Simulation instance containing the game state
        @return bool True to continue, False to quit
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """
        @brief Clean up view resources
        @details Releases resources (curses, files, etc.)
        """
        pass


class ColorPair(Enum):
    """
    @brief Color pairs for curses rendering

    @details Defines colors used to distinguish
    teams and UI elements.
    """
    TEAM_A = 1   ##< Cyan for team A
    TEAM_B = 2   ##< Red for team B
    UI = 3       ##< Yellow for the UI
    DEAD = 4     ##< Dark/grey for dead units


@dataclass
class Camera:
    """
    @brief Manage camera position and zoom

    @details Encapsulates all camera movement and zoom logic.
    Applies the Single Responsibility Principle (SOLID).

    @param x Camera X position
    @param y Camera Y position
    @param zoom_level Zoom level (1=normal, 2=zoomed out, 3=very zoomed out)
    @param scroll_speed_normal Normal scroll speed
    @param scroll_speed_fast Fast scroll speed (with Shift)
    """
    x: int = 0
    y: int = 0
    zoom_level: int = 1
    scroll_speed_normal: int = 5
    scroll_speed_fast: int = 15
    # Smooth following
    target_x: float = 0.0
    target_y: float = 0.0
    follow_smoothing: float = 0.1  # How fast to follow (0.1 = smooth, 1.0 = instant)
    
    def move(self, dx: int, dy: int, fast: bool = False):
        """
        @brief Move the camera
        @param dx Movement on X axis (-1, 0, 1)
        @param dy Movement on Y axis (-1, 0, 1)
        @param fast True for faster movement (when Shift is pressed)
        """
        speed = self.scroll_speed_fast if fast else self.scroll_speed_normal
        # In rotated view, dx controls y (horizontal on screen is vertical on board)
        # and dy controls x (vertical on screen is horizontal on board)
        self.y += dx * speed * self.zoom_level
        self.x += dy * speed * self.zoom_level
    
    def toggle_zoom(self):
        """
        @brief Toggle between zoom levels
        @details Cycles through zoom_level 1 (normal), 2 (zoomed out), 3 (very zoomed out)
        """
        self.zoom_level = (self.zoom_level % 3) + 1
    
    def center_on_battle(self, simulation, term_w: int, term_h: int, ui_height: int = 0):
        """
        @brief Set target for smooth camera following of the battle area
        @param simulation Simulation instance
        @param term_w Terminal width
        @param term_h Terminal height
        @param ui_height UI height
        """
        units = simulation.board.units if hasattr(simulation, 'board') else simulation.scenario.units
        if not units:
            return
        
        # Focus on units that are fighting (have a target or are moving)
        # Use getattr for safety in case Model attributes change
        fighting_units = [
            u for u in units 
            if getattr(u, 'target', None) is not None or u.hp < getattr(u, 'hp_max', u.hp)
        ]
        if not fighting_units:
            # If no fighting units, use all units
            fighting_units = units
        
        # Calculate center of mass of fighting units
        avg_x = sum(u.x for u in fighting_units) / len(fighting_units)
        avg_y = sum(u.y for u in fighting_units) / len(fighting_units)
        # Set target position
        # In rotated view: screen_x = (unit.y - camera.y) / zoom, screen_y = (unit.x - camera.x) / zoom
        # To center avg_y on screen_x (term_w), camera.y = avg_y - (term_w / 2) * zoom
        # To center avg_x on screen_y (term_h), camera.x = avg_x - ((term_h - ui_height) / 2) * zoom
        self.target_x = avg_x - ((term_h - ui_height) / 2) * self.zoom_level
        self.target_y = avg_y - (term_w / 2) * self.zoom_level
    
    def update_smooth_follow(self):
        """
        @brief Update camera position with smooth interpolation towards target
        """
        # Interpolate towards target
        self.x = int(self.x + (self.target_x - self.x) * self.follow_smoothing)
        self.y = int(self.y + (self.target_y - self.y) * self.follow_smoothing)
    
    def clamp(self, board_width: int, board_height: int, term_w: int, term_h: int, ui_height: int = 0):
        """
        @brief Clamp the camera inside the board limits
        @param board_width Game board width
        @param board_height Game board height
        @param term_w Terminal width
        @param term_h Terminal height
        @param ui_height UI height
        """
        visible_w = int(term_h * self.zoom_level)  # term_h becomes width in rotated view
        visible_h = int((term_w - ui_height) * self.zoom_level)  # term_w becomes height
        max_x = max(0, board_height - visible_w)  # board_height for x (since x controls y)
        max_y = max(0, board_width - visible_h)  # board_width for y
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))


class TerminalView(ViewInterface):
    """
    @brief Terminal View using curses to display the battle

    @details Main view implementation in the MVC architecture.
    Provides a curses-based terminal display to visualize battles
    in real time. Supports both interactive and headless modes.

    @features
    - Colored rendering of units by team
    - Keyboard controls (pause, zoom, scroll)
    - Headless mode for automated tests
    - HTML report generation
    - Compatible with A/B teams

    @controls
    - P: Pause/Resume
    - M: Toggle zoom
    - ZQSD/Arrows: Move camera
    - +/-: Adjust tick speed
    - TAB: Generate HTML report
    - ESC: Quit
    """
    
    ##< @brief Mapping from unit types to display letters
    UNIT_LETTERS = {
        'Knight': 'K',           ##< Knight
        'Pikeman': 'P',          ##< Pikeman
        'Crossbowman': 'C',      ##< Crossbowman
        'Long Swordsman': 'L',   ##< Long Swordsman
        'Elite Skirmisher': 'S', ##< Elite Skirmisher
        'Cavalry Archer': 'A',   ##< Cavalry Archer
        'Onager': 'O',           ##< Onager
        'Light Cavalry': 'V',    ##< Light Cavalry
        'Scorpion': 'R',         ##< Scorpion
        'Capped Ram': 'M',       ##< Capped Ram
        'Trebuchet': 'T',        ##< Trebuchet
        'Elite War Elephant': 'E', ##< Elite War Elephant
        'Monk': 'N',             ##< Monk
        'Castle': '#',           ##< Castle
        'Wonder': 'W'            ##< Wonder
    }
    
    def __init__(self, board_width: int, board_height: int, tick_speed: int = 40):
        """
        @brief Initialize the terminal view

        @param board_width Game board width
        @param board_height Game board height
        @param tick_speed Number of ticks per second (framerate)

        @details Configures all parameters required for rendering:
        camera, view state, unit cache, and statistics.
        """
        self.board_width = board_width
        self.board_height = board_height
        self.tick_speed = tick_speed
        
        # Camera (initially centered on the board)
        self.camera = Camera(
            x=max(0, board_width // 2 - 40),
            y=max(0, board_height // 2 - 20),
        )
        
        # View state
        self.paused = False
        self.show_debug = False
        self.show_ui = True
        self.auto_follow = False  # Auto-follow camera on battle (disabled)
        
        # Curses window
        self.stdscr = None
        self.windows = {}
        
        # Unit cache
        self.units_cache: List[UniteRepr] = []
        self.all_units_dict = {}  # Persistent storage for all units (alive and dead)
        
        # Stats
        self.team1_units = 0
        self.team2_units = 0
        self.simulation_time = 0.0
        self.dead_team1 = 0
        self.dead_team2 = 0
        self.type_counts_team1 = {}
        self.type_counts_team2 = {}
        self.unit_hp_memory = {}  # id(unit) -> hp_max estimé
        
        # FPS
        self.fps = 0.0
        self._last_frame_time = time.perf_counter()
        # Suivi des unités récemment mortes pour les faire clignoter
        self._death_times = {}  # id(unit_repr) -> time_of_death
        
    def init_curses(self):
        """
        @brief Initialize the curses environment

        @details Configure curses for terminal rendering:
        - Initialize the screen and colors
        - Configure non-blocking keyboard input
        - Define color pairs for teams and UI

        @note Must be called before any curses-based rendering
        """
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)  # Hide cursor
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)  # Non-blocking input
        
        # Initialisation des paires de couleurs
        curses.init_pair(ColorPair.TEAM_A.value, curses.COLOR_CYAN, -1)
        curses.init_pair(ColorPair.TEAM_B.value, curses.COLOR_RED, -1)
        curses.init_pair(ColorPair.UI.value, curses.COLOR_YELLOW, -1)
        curses.init_pair(ColorPair.DEAD.value, curses.COLOR_BLACK, -1)
        
    def cleanup(self):
        """
        @brief Clean up and restore the terminal environment

        @details Restores the terminal to its normal state:
        - Disable keypad mode
        - Restore canonical mode and echo
        - Release the curses screen

        @note Must always be called at the end of the program
        """
        if self.stdscr:
            self.stdscr.keypad(False)
            curses.nocbreak()
            curses.echo()
            curses.endwin()
    
    def handle_input(self) -> bool:
        """
        @brief Handle user keyboard input

        @details Processes all keyboard interactions:
        - Navigation: ZQSD, arrow keys (with Shift for faster move)
        - Zoom: M (cycle between zoom levels)
        - Auto-follow: A (toggle auto-follow camera on battle)
        - Controls: P(pause), +/-(tick speed), TAB(report), F(UI), Ctrl+D(debug)
        - Exit: Escape

        @return bool False to quit the application, True to continue
        @note Uses non-blocking getch() to avoid freezes
        """
        try:
            key = self.stdscr.getch()
        except (KeyboardInterrupt, curses.error):
            return True
        
        if key == -1:  # No input
            return True
        
        # Tick speed adjustment
        if key in (ord('+'), ord('=')):
            self.tick_speed = min(240, self.tick_speed + 5)
            return True
        if key in (ord('-'), ord('_')):
            self.tick_speed = max(1, self.tick_speed - 5)
            return True
        
        # Pause/Resume
        if key in (ord('p'), ord('P')):
            self.paused = not self.paused
            return True
        
        # Zoom
        if key in (ord('m'), ord('M')):
            self.camera.toggle_zoom()
            # Re-clamp camera after zoom change
            max_y, max_x = self.stdscr.getmaxyx()
            ui_height = 5 if self.show_ui else 0
            self.camera.clamp(self.board_width, self.board_height, max_x, max_y, ui_height)
            return True
        
        # Toggle auto-follow
        if key in (ord('a'), ord('A')):
            self.auto_follow = not self.auto_follow
            return True
        
        # Debug view
        if key == 4:  # Ctrl+D
            self.show_debug = not self.show_debug
            return True
        
        # Toggle UI
        if key in (ord('f'), ord('F')):
            self.show_ui = not self.show_ui
            return True
        
        # HTML report generation
        if key == ord('\t'):  # TAB
            self.paused = True  # Pause the game
            self.generate_html_report()
            return True
        
        # Quit
        if key == 27:  # ESC only
            return False
        
        # Scroll with ZQSD
        if key in (ord('z'), ord('Z'), curses.KEY_UP):
            fast = key == ord('Z')
            self.camera.move(0, -1, fast)
            self.auto_follow = False  # Disable auto-follow on manual movement
        elif key in (ord('s'), ord('S'), curses.KEY_DOWN):
            fast = key == ord('S')
            self.camera.move(0, 1, fast)
            self.auto_follow = False
        elif key in (ord('q'), ord('Q'), curses.KEY_LEFT):
            fast = key == ord('Q')
            self.camera.move(-1, 0, fast)
            self.auto_follow = False
        elif key in (ord('d'), ord('D'), curses.KEY_RIGHT):
            fast = key == ord('D')
            self.camera.move(1, 0, fast)
            self.auto_follow = False
        
        return True
    
    def _resolve_letter(self, unit_type: str) -> str:
        """Return the display letter for a type or '?' by default."""
        return self.UNIT_LETTERS.get(unit_type, unit_type[:1].upper() if unit_type else '?')
    
    def _get_unit_display_attributes(self, unit: UniteRepr) -> tuple[str, ColorPair, int]:
        """
        @brief Determine the visual display attributes of a unit

        @param unit Unit to display
        @return tuple Triplet (character, color_enum, curses_attributes)

        @details Rendering logic:
        - Alive units: type letter + team color + bold
        - Dead units: 'x' in grey with blink
        """
        if unit.alive:
            color = ColorPair.TEAM_A if unit.team == Team.A else ColorPair.TEAM_B
            char = unit.letter
            attr = curses.color_pair(color.value) | curses.A_BOLD
            return char, color, attr
        
        # Dead units are not rendered on the map
        return ' ', ColorPair.DEAD, curses.A_NORMAL

    def _draw_border(self, width: int, height: int):
        """
        @brief Draw a decorative border around the game board

        @param width Border width in characters
        @param height Border height in characters

        @details Uses Unicode characters for a nicer look:
        - Corners: ┌ ┐└ ┘
        - Borders: ─ │
        - Uses the UI color pair
        """
        ui_color = curses.color_pair(ColorPair.UI.value)
        try:
            # Corners
            self.stdscr.addch(0, 0, '┌', ui_color)
            self.stdscr.addch(0, width - 1, '┐', ui_color)
            self.stdscr.addch(height - 1, 0, '└', ui_color)
            self.stdscr.addch(height - 1, width - 1, '┘', ui_color)
            
            # Horizontal lines
            for x in range(1, width - 1):
                self.stdscr.addch(0, x, '─', ui_color)
                self.stdscr.addch(height - 1, x, '─', ui_color)
            
            # Vertical lines
            for y in range(1, height - 1):
                self.stdscr.addch(y, 0, '│', ui_color)
                self.stdscr.addch(y, width - 1, '│', ui_color)
        except curses.error:
            pass  # Ignore errors if terminal is too small

    def _extract_unit_fields(self, unit):
        """Adapt to model attribute naming differences."""
        # team/equipe
        team = getattr(unit, 'equipe', getattr(unit, 'team', 1))
        # hp / hp_max
        hp = getattr(unit, 'hp', 0)
        # hp_max: if missing, remember the first non-zero value
        if hasattr(unit, 'hp_max'):
            hp_max = getattr(unit, 'hp_max')
        else:
            uid = id(unit)
            if uid not in self.unit_hp_memory and hp > 0:
                self.unit_hp_memory[uid] = hp
            hp_max = self.unit_hp_memory.get(uid, hp)
        # type/name
        unit_type = getattr(unit, 'name', type(unit).__name__)
        # position
        x = getattr(unit, 'x', 0.0)
        y = getattr(unit, 'y', 0.0)
        # alive()
        alive = hp > 0
        # optional stats
        armor = getattr(unit, 'armor', None)
        attack = getattr(unit, 'attack', None)
        rng = getattr(unit, 'range', None)
        reload_time = getattr(unit, 'reload_time', None)
        reload_val = getattr(unit, 'reload', None)
        damage_dealt = getattr(unit, 'damage_dealt', 0)
        target = getattr(unit, 'target', None)
        target_id = id(target) if target else None
        
        return {
            'team': team, 'hp': hp, 'hp_max': hp_max, 'type': unit_type,
            'x': x, 'y': y, 'alive': alive,
            'armor': armor, 'attack': attack, 'range': rng,
            'reload_time': reload_time, 'reload_val': reload_val,
            'damage_dealt': damage_dealt,
            'target_id': target_id
        }

    def _resolve_team(self, team_val) -> Team:
        """Resolve team value to Team enum."""
        if isinstance(team_val, Team):
            return team_val
        if team_val in (1, 'A', 'a'):
            return Team.A
        return Team.B

    def _get_units_from_simulation(self, simulation) -> list:
        """Retrieve units list from simulation."""
        if hasattr(simulation, 'units'):
            return simulation.units
        if hasattr(simulation, 'board') and hasattr(simulation.board, 'units'):
            return simulation.board.units
        return []

    def update_units_cache(self, simulation):
        """
        Update the unit cache from the simulation.

        Args:
            simulation: Simulation instance containing the units
        """
        # Reset stats
        self.team1_units = 0
        self.team2_units = 0
        self.dead_team1 = 0
        self.dead_team2 = 0
        self.type_counts_team1 = {}
        self.type_counts_team2 = {}
        
        # Get current living units from simulation
        current_units = self._get_units_from_simulation(simulation)
        current_unit_ids = set()
        
        # Update living units
        for unit in current_units:
            if not hasattr(unit, 'hp'):
                continue
                
            fields = self._extract_unit_fields(unit)
            team = self._resolve_team(fields['team'])
            uid = id(unit)
            current_unit_ids.add(uid)
            
            repr_obj = UniteRepr(
                type=fields['type'],
                team=team,
                letter=self._resolve_letter(fields['type']),
                x=fields['x'],
                y=fields['y'],
                hp=max(0, fields['hp']),
                hp_max=fields['hp_max'],
                status=UnitStatus.ALIVE if fields['alive'] else UnitStatus.DEAD,
                damage_dealt=fields['damage_dealt'],
                target_id=fields['target_id']
            )
            self.all_units_dict[uid] = repr_obj

        # Mark missing units as dead
        for uid, repr_obj in self.all_units_dict.items():
            if uid not in current_unit_ids:
                repr_obj.status = UnitStatus.DEAD
                repr_obj.hp = 0
                # Keep last known position
        
        # Rebuild cache from all units
        self.units_cache = list(self.all_units_dict.values())
        
        # Recalculate stats
        for unit in self.units_cache:
            is_team_a = (unit.team == Team.A)
            target_counts = self.type_counts_team1 if is_team_a else self.type_counts_team2
            
            if unit.alive:
                target_counts[unit.type] = target_counts.get(unit.type, 0) + 1
                if is_team_a:
                    self.team1_units += 1
                else:
                    self.team2_units += 1
            else:
                if is_team_a:
                    self.dead_team1 += 1
                else:
                    self.dead_team2 += 1
        
        # Update simulation time
        if hasattr(simulation, 'elapsed_time'):
            self.simulation_time = simulation.elapsed_time
        elif hasattr(simulation, 'tick') and hasattr(simulation, 'tickSpeed'):
             self.simulation_time = simulation.tick / simulation.tickSpeed
    
    def draw_map(self):
        """
        @brief Draw the map and units on screen

        @details Main rendering function that:
        - Clears the previous frame
        - Computes the available display area
        - Applies camera constraints
        - Draws the border, units and visual elements

        @note Called every frame to refresh the display
        """
        max_y, max_x = self.stdscr.getmaxyx()
        
        # Clear screen
        self.stdscr.clear()
        
        # Game area (keeps some space at the bottom for the UI)
        game_height = max_y - (5 if self.show_ui else 0)
        
        # Camera constraints
        ui_height = 5 if self.show_ui else 0
        self.camera.clamp(self.board_width, self.board_height, max_x, max_y, ui_height)
        
        # Draw a border around the game area
        self._draw_border(max_x, game_height)
        
        # Direct drawing (no intermediate grid)
        # Keep 1 row/column margin for the border
        for unit in self.units_cache:
            # Screen position with zoom and camera, rotated 90 degrees
            # Swap x and y for rotation
            screen_x = int((unit.y - self.camera.y) / self.camera.zoom_level) + 1  # y becomes x
            screen_y = int((unit.x - self.camera.x) / self.camera.zoom_level) + 1  # x becomes y
            
            # Bounds check (taking the border into account)
            if 1 <= screen_x < max_x - 1 and 1 <= screen_y < game_height - 1:
                # Utilise la même logique que _get_unit_display_attributes
                char, _color_enum, attr = self._get_unit_display_attributes(unit)
                try:
                    self.stdscr.addstr(screen_y, screen_x, char, attr)
                except curses.error:
                    pass  # Ignore les erreurs en bordure d'écran
    
    def draw_ui(self):
        """
        @brief Draw the user interface

        @details Displays at the bottom of the screen:
        - Separator line between game area and UI
        - Team statistics (units, deaths)
        - Available control shortcuts
        - Camera and zoom information

        @note Only if self.show_ui is True
        """
        if not self.show_ui:
            return
        
        max_y, max_x = self.stdscr.getmaxyx()
        ui_start_y = max_y - 5
        
        # Separator line
        try:
            self.stdscr.addstr(ui_start_y, 0, "─" * max_x, curses.color_pair(ColorPair.UI.value))
        except curses.error:
            pass
        
        stats_line = (
            f"Time:{self.simulation_time:.1f}s | T1 A:{self.team1_units} D:{self.dead_team1} | "
            f"T2 A:{self.team2_units} D:{self.dead_team2} | Total:{len(self.units_cache)} | FPS:{self.fps:.0f}"
        )
        try:
            self.stdscr.addstr(ui_start_y + 1, 2, stats_line, curses.color_pair(ColorPair.UI.value) | curses.A_BOLD)
        except curses.error:
            pass
        
        state_line = (
            f"{'PAUSE' if self.paused else 'PLAY'} | Zoom:x{self.camera.zoom_level} "
            f"| Cam:({self.camera.x},{self.camera.y}) | {'AUTO' if self.auto_follow else 'MANUAL'} | Tick:{self.tick_speed}"
        )
        try:
            self.stdscr.addstr(ui_start_y + 2, 2, state_line)
        except curses.error:
            pass
        
        # Summary line for main types (Archer/Knight/Pikeman if present)
        summary = []
        for label in ['Archer', 'Knight', 'Pikeman']:
            c1 = self.type_counts_team1.get(label, 0)
            c2 = self.type_counts_team2.get(label, 0)
            if c1 or c2:
                summary.append(f"{label}:{c1}/{c2}")
        types_line = " | ".join(summary)
        if types_line:
            try:
                self.stdscr.addstr(ui_start_y + 3, 2, types_line, curses.color_pair(ColorPair.UI.value))
            except curses.error:
                pass
        
        # Commands (shifted depending on whether types_line exists)
        commands_y = ui_start_y + (4 if types_line else 3)
        commands_line = "P:Pause M:Zoom +/-:Tick ZQSD/Flèches:Scroll TAB:Rapport F:UI D:Debug ESC:Quitter"
        try:
            self.stdscr.addstr(commands_y, 2, commands_line, curses.color_pair(ColorPair.UI.value))
        except curses.error:
            pass
    
    def draw_debug_info(self):
        """
        @brief Display debug information as an overlay

        @details Developer-oriented mode that shows:
        - Details of the first units (position, health, team)
        - Internal state for diagnostics

        @note Only if self.show_debug is True (D key)
        """
        if not self.show_debug:
            return
        
        max_y, max_x = self.stdscr.getmaxyx()
        
        # Show first units with detailed information
        debug_y = 1
        try:
            self.stdscr.addstr(debug_y, max_x - 48, "═══ DEBUG ═══", curses.color_pair(ColorPair.UI.value) | curses.A_BOLD)
            debug_y += 1
            
            for i, unit in enumerate(self.units_cache[:6]):
                status = "ALV" if unit.alive else "DED"
                debug_text = f"{status} {unit.type[:10]:10} ({unit.letter}) HP:{unit.hp:3}/{unit.hp_max:3} DMG:{unit.damage_dealt:3}"
                color = ColorPair.TEAM_A if unit.team == Team.A else ColorPair.TEAM_B
                if not unit.alive:
                    color = ColorPair.DEAD
                self.stdscr.addstr(debug_y + i, max_x - 48, debug_text[:48], curses.color_pair(color.value))
        except curses.error:
            pass
    
    def draw_pause_overlay(self, max_x: int, max_y: int):
        """
        @brief Draw pause overlay when game is paused
        @param max_x Terminal width
        @param max_y Terminal height
        """
        try:
            # Draw semi-transparent pause message in center
            pause_msg = "PAUSED - Press P to resume"
            msg_len = len(pause_msg)
            center_x = max_x // 2 - msg_len // 2
            center_y = max_y // 2
            
            # Draw background box
            box_width = msg_len + 4
            box_height = 3
            box_x = center_x - 2
            box_y = center_y - 1
            
            for y in range(box_y, box_y + box_height):
                for x in range(box_x, box_x + box_width):
                    if 0 <= x < max_x and 0 <= y < max_y:
                        self.stdscr.addstr(y, x, ' ', curses.color_pair(ColorPair.UI.value) | curses.A_REVERSE)
            
            # Draw message
            self.stdscr.addstr(center_y, center_x, pause_msg, curses.color_pair(ColorPair.UI.value) | curses.A_BOLD | curses.A_REVERSE)
        except curses.error:
            pass
    
    def update(self, simulation):
        """
        Update the display with the current simulation state.

        Args:
            simulation: Simulation instance from the Model
        """
        # Handle user input
        if not self.handle_input():
            return False  
        
        # Get terminal dimensions
        max_y, max_x = self.stdscr.getmaxyx()
        
        # If paused, do not update the cache but still redraw
        if not self.paused:
            self.update_units_cache(simulation)
            # Auto-follow camera on battle if enabled
            if self.auto_follow:
                self.camera.center_on_battle(simulation, max_x, max_y, 5 if self.show_ui else 0)
                # Update smooth camera following
                self.camera.update_smooth_follow()
            # Clamp camera after movement
            self.camera.clamp(self.board_width, self.board_height, max_x, max_y, 5 if self.show_ui else 0)
            
            self.draw_map()
            self.draw_ui()
            self.draw_debug_info()
        else:
            # When paused, still draw the UI to show pause status
            self.draw_ui()
            self.draw_debug_info()
            # Draw pause overlay
            self.draw_pause_overlay(max_x, max_y)
        
        # Refresh the screen
        self.stdscr.refresh()
        
        # Compute FPS before sleeping
        now = time.perf_counter()
        dt = now - self._last_frame_time
        if dt > 0:
            self.fps = 1.0 / dt
        self._last_frame_time = now
        
        # Framerate control
        time.sleep(max(0.0, 1.0 / self.tick_speed))
        
        return True
    
    def _generate_unit_html(self, i: int, unit: UniteRepr, team_num: int) -> str:
        """Generate HTML for a single unit."""
        hp_percent = (unit.hp / unit.hp_max) * 100 if unit.hp_max > 0 else 0
        hp_class = "hp-critical" if hp_percent < 25 else "hp-low" if hp_percent < 50 else ""
        status_label = "Alive" if unit.alive else "Dead"
        target_info = f"Targeting: #{unit.target_id}" if unit.target_id else "Idle"
        
        # Generate unique ID for the unit
        unit_id = f"unit-{team_num}-{i}"
        
        return f"""
                <div class="unit team{team_num}" id="{unit_id}" data-unit-id="{unit_id}">
                    <div class="unit-header">
                        <span>#{i} {unit.type} ({unit.letter})</span>
                        <span>{status_label}</span>
                    </div>
                    <div class="unit-details">
                        <div>Pos: ({unit.x:.1f}, {unit.y:.1f})</div>
                        <div>HP: {unit.hp}/{unit.hp_max} ({hp_percent:.0f}%) | DMG: {unit.damage_dealt}</div>
                        <div>{target_info}</div>
                    </div>
                    <div class="hp-bar">
                        <div class="hp-fill {hp_class}" style="width: {hp_percent}%"></div>
                    </div>
                </div>
"""

    def _generate_team_section(self, team_num: int, units: List[UniteRepr]) -> str:
        """Generate HTML section for a team."""
        units_html = "".join(self._generate_unit_html(i, u, team_num) for i, u in enumerate(units, 1))
        return f"""
    <div class="team-section">
        <details open>
            <summary>Team {team_num} - {len(units)} units</summary>
            <div class="unit-list">
{units_html}
            </div>
        </details>
    </div>
"""

    def _generate_battle_map(self) -> str:
        """Generate HTML for the battle map visualization."""
        dots_html = ""
        
        # Split units by team to match ID generation in team sections
        team1_units = [u for u in self.units_cache if u.team == Team.A]
        team2_units = [u for u in self.units_cache if u.team == Team.B]
        
        def process_unit(i, unit, team_num):
            if not unit.alive:
                return ""
                
            # Calculate grid position (1-based)
            col = int(unit.x) + 1
            row = int(unit.y) + 1
            
            # Clamp to board limits
            col = max(1, min(self.board_width, col))
            row = max(1, min(self.board_height, row))
            
            team_class = "team1" if team_num == 1 else "team2"
            unit_id = f"unit-{team_num}-{i}"
            
            return f'<div class="unit-cell {team_class}" style="grid-column: {col}; grid-row: {row};" data-unit-id="{unit_id}" onclick="selectUnit(\'{unit_id}\')" title="{unit.type} #{i} ({unit.x:.1f}, {unit.y:.1f})">{unit.letter}</div>'

        # Process Team 1
        for i, unit in enumerate(team1_units, 1):
            dots_html += process_unit(i, unit, 1)
            
        # Process Team 2
        for i, unit in enumerate(team2_units, 1):
            dots_html += process_unit(i, unit, 2)
            
        return f"""
        <div class="battle-map-container">
            <details open>
                <summary>Battlefield Map ({self.board_width}x{self.board_height})</summary>
                <div class="map-header">
                    <div class="map-controls">
                        <button onclick="zoomMap(0.5)" title="Zoom In">+</button>
                        <button onclick="zoomMap(-0.5)" title="Zoom Out">-</button>
                        <button onclick="resetZoom()" title="Reset Zoom">Reset</button>
                    </div>
                </div>
                <div class="battle-map-viewport">
                    <div id="battleMap" class="battle-map" style="--cols: {self.board_width}; --rows: {self.board_height};">
                        {dots_html}
                    </div>
                </div>
                <p class="help-text">Click units to view details • Use controls to zoom</p>
            </details>
        </div>
        """

    def generate_html_report(self):
        """
        Generate an HTML report with the current state of all units.
        Called when the TAB key is pressed.
        """
        import datetime
        import os
        import webbrowser
        
        # Prepare data
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"battle_report_{timestamp}.html"
        
        # Generate sections
        team1_units = [u for u in self.units_cache if u.team == Team.A]
        team2_units = [u for u in self.units_cache if u.team == Team.B]
        
        team_sections = self._generate_team_section(1, team1_units) + \
                        self._generate_team_section(2, team2_units)
        
        battle_map = self._generate_battle_map()
        
        legend_items = "\n".join(
            f"            <li><strong>{letter}</strong>: {unit_type}</li>" 
            for unit_type, letter in sorted(self.UNIT_LETTERS.items())
        )
        
        # Load resources
        base_dir = os.path.dirname(__file__)
        with open(os.path.join(base_dir, 'battle_report_template.html'), 'r', encoding='utf-8') as f:
            template = f.read()
        with open(os.path.join(base_dir, 'battle_report.css'), 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        # Fill template
        replacements = {
            '{timestamp}': timestamp,
            '{simulation_time}': f"{self.simulation_time:.2f}",
            '{team1_units}': str(self.team1_units),
            '{team2_units}': str(self.team2_units),
            '{total_units}': str(len(self.units_cache)),
            '{team_sections}': team_sections,
            '{battle_map}': battle_map,
            '{legend_items}': legend_items,
            '{generation_datetime}': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        html_content = template
        for key, value in replacements.items():
            html_content = html_content.replace(key, value)
            
        # Write files
        with open("battle_report.css", 'w', encoding='utf-8') as f:
            f.write(css_content)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        webbrowser.open('file://' + os.path.abspath(filename))

    def debug_snapshot(self) -> dict:
        """Return a snapshot of current stats (for tests)."""
        return {
            "time": self.simulation_time,
            "team1_alive": self.team1_units,
            "team2_alive": self.team2_units,
            "team1_dead": self.dead_team1,
            "team2_dead": self.dead_team2,
            "types_team1": dict(self.type_counts_team1),
            "types_team2": dict(self.type_counts_team2),
            "total_units_cached": len(self.units_cache)
        }

    def run_headless(self, simulation, ticks: int = 10):
        """Run a few ticks without curses for automated tests."""
        for _ in range(ticks):
            if not self.paused:
                simulation.step() if hasattr(simulation, "step") else None
                self.update_units_cache(simulation)
        return self.debug_snapshot()


def main_test():
    """Headless test mode: python terminal_view.py --test"""
    print("=== Headless Test Mode ===")
    
    # Create real simulation
    units = []
    units_a = []
    units_b = []
    
    # Small scenario for testing
    u1 = Knight(1, 20, 20)
    u2 = Pikeman(2, 30, 30)
    units = [u1, u2]
    units_a = [u1]
    units_b = [u2]
    
    simulation = Simulation(units, units_a, None, units_b, None, tickSpeed=20, size_x=120, size_y=120)
    
    view = TerminalView(120, 120)
    
    print("Simulation: 50 ticks")
    snapshot = view.run_headless(simulation, ticks=50)
    
    print("\nResults:")
    print(f"  Simulated time: {snapshot['time']:.2f}s")
    print(f"  Team 1: {snapshot['team1_alive']} alive, {snapshot['team1_dead']} dead")
    print(f"  Team 2: {snapshot['team2_alive']} alive, {snapshot['team2_dead']} dead")
    print(f"  Total units: {snapshot['total_units_cached']}")
    print("\nHeadless test: OK")


def main_demo():
    """Demo function for the terminal view."""
    
    units = []
    units_a = []
    units_b = []
    
    # Team A (Cyan) - Left side
    for i in range(5):
        u = Knight(1, 20, 20 + i*5)
        units.append(u)
        units_a.append(u)
    
    for i in range(5):
        u = Pikeman(1, 25, 20 + i*5)
        units.append(u)
        units_a.append(u)
        
    # Team B (Red) - Right side
    for i in range(5):
        u = Knight(2, 100, 20 + i*5)
        units.append(u)
        units_b.append(u)
        
    for i in range(5):
        u = Pikeman(2, 95, 20 + i*5)
        units.append(u)
        units_b.append(u)
        
    simulation = Simulation(units, units_a, None, units_b, None, tickSpeed=20, size_x=120, size_y=120)
    
    # Create the view
    view = TerminalView(120, 120, tick_speed=20)
    
    try:
        view.init_curses()
        
        # Main loop
        running = True
        while running:
            if not view.paused:
                simulation.step()
            
            running = view.update(simulation)
            
    finally:
        view.cleanup()


if __name__ == "__main__":
    if "--test" in sys.argv:
        main_test()
    else:
        main_demo()