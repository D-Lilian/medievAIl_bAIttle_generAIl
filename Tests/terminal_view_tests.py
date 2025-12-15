# -*- coding: utf-8 -*-
"""
@file terminal_view_tests.py
@brief Terminal View Tests - Unit tests for the view

@details
Tests the TerminalView components, including UnitRepr, Camera,
ViewState, Stats, and rendering logic (mocked).

Refactored to match SOLID/KISS terminal_view.py implementation.
"""
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from View.terminal_view import (
    UnitRepr, UnitStatus, Team, Camera, ViewState, Stats,
    TerminalView, resolve_letter, resolve_team,
    InputHandler, MapRenderer, UnitCacheManager
)


class TestUnitRepr(unittest.TestCase):
    """
    @brief Tests for UnitRepr dataclass.
    """

    def test_alive_property(self):
        """
        @brief Test alive property returns correct status.
        """
        u = UnitRepr(
            type="Knight", team=Team.A, uid=1, letter="K",
            x=10, y=10, hp=100, hp_max=100, status=UnitStatus.ALIVE
        )
        self.assertTrue(u.alive)
        u.status = UnitStatus.DEAD
        self.assertFalse(u.alive)

    def test_hp_percent(self):
        """
        @brief Test hp_percent calculation.
        """
        u = UnitRepr(
            type="Knight", team=Team.A, uid=1, letter="K",
            x=10, y=10, hp=50, hp_max=100, status=UnitStatus.ALIVE
        )
        self.assertEqual(u.hp_percent, 50.0)
        u.hp = 0
        self.assertEqual(u.hp_percent, 0.0)
        u.hp_max = 0
        self.assertEqual(u.hp_percent, 0.0)

    def test_optional_fields(self):
        """
        @brief Test optional fields default to None.
        """
        u = UnitRepr(
            type="Knight", team=Team.A, uid=1, letter="K",
            x=10, y=10, hp=100, hp_max=100, status=UnitStatus.ALIVE
        )
        self.assertIsNone(u.armor)
        self.assertIsNone(u.attack)
        self.assertIsNone(u.target_name)


class TestCamera(unittest.TestCase):
    """
    @brief Tests for Camera dataclass.
    """

    def setUp(self):
        self.camera = Camera(x=0, y=0, zoom_level=1)

    def test_move_normal(self):
        """
        @brief Test normal speed movement.
        """
        initial_x = self.camera.x
        initial_y = self.camera.y
        self.camera.move(1, 0, fast=False)
        self.assertEqual(self.camera.x, initial_x + self.camera.scroll_speed_normal)
        self.assertEqual(self.camera.y, initial_y)

        self.camera.move(0, 1, fast=False)
        self.assertEqual(self.camera.y, initial_y + self.camera.scroll_speed_normal)

    def test_move_fast(self):
        """
        @brief Test fast speed movement.
        """
        initial_x = self.camera.x
        self.camera.move(1, 0, fast=True)
        self.assertEqual(self.camera.x, initial_x + self.camera.scroll_speed_fast)

    def test_toggle_zoom(self):
        """
        @brief Test zoom level cycling 1->2->3->1.
        """
        self.assertEqual(self.camera.zoom_level, 1)
        self.camera.toggle_zoom()
        self.assertEqual(self.camera.zoom_level, 2)
        self.camera.toggle_zoom()
        self.assertEqual(self.camera.zoom_level, 3)
        self.camera.toggle_zoom()
        self.assertEqual(self.camera.zoom_level, 1)

    def test_clamp(self):
        """
        @brief Test camera clamping to board bounds.
        """
        self.camera.x = 150
        self.camera.y = 150
        self.camera.clamp(100, 100, 20, 20, 0)
        self.assertEqual(self.camera.x, 80)
        self.assertEqual(self.camera.y, 80)

        self.camera.x = -50
        self.camera.y = -50
        self.camera.clamp(100, 100, 20, 20, 0)
        self.assertEqual(self.camera.x, 0)
        self.assertEqual(self.camera.y, 0)


class TestViewState(unittest.TestCase):
    """
    @brief Tests for ViewState dataclass.
    """

    def test_default_values(self):
        """
        @brief Test default state values.
        """
        state = ViewState()
        self.assertFalse(state.paused)
        self.assertTrue(state.show_ui)
        self.assertFalse(state.show_debug)
        self.assertTrue(state.show_unit_counts)
        self.assertTrue(state.show_unit_types)
        self.assertTrue(state.show_sim_info)

    def test_toggle_all_panels(self):
        """
        @brief Test F4 toggle all panels.
        """
        state = ViewState()
        # All on initially
        state.toggle_all_panels()
        self.assertFalse(state.show_unit_counts)
        self.assertFalse(state.show_unit_types)
        self.assertFalse(state.show_sim_info)
        self.assertFalse(state.show_ui)

        # Toggle back on
        state.toggle_all_panels()
        self.assertTrue(state.show_unit_counts)
        self.assertTrue(state.show_unit_types)
        self.assertTrue(state.show_sim_info)
        self.assertTrue(state.show_ui)


class TestStats(unittest.TestCase):
    """
    @brief Tests for Stats dataclass.
    """

    def test_reset(self):
        """
        @brief Test stats reset.
        """
        stats = Stats()
        stats.team1_alive = 10
        stats.team2_dead = 5
        stats.type_counts_team1['Knight'] = 3
        stats.reset()
        self.assertEqual(stats.team1_alive, 0)
        self.assertEqual(stats.team2_dead, 0)
        self.assertEqual(len(stats.type_counts_team1), 0)

    def test_add_unit(self):
        """
        @brief Test adding units to stats.
        """
        stats = Stats()

        # Add alive Team A unit
        u1 = UnitRepr(
            type="Knight", team=Team.A, uid=1, letter="K",
            x=0, y=0, hp=100, hp_max=100, status=UnitStatus.ALIVE
        )
        stats.add_unit(u1)
        self.assertEqual(stats.team1_alive, 1)
        self.assertEqual(stats.type_counts_team1.get('Knight', 0), 1)

        # Add dead Team B unit
        u2 = UnitRepr(
            type="Pikeman", team=Team.B, uid=2, letter="P",
            x=0, y=0, hp=0, hp_max=100, status=UnitStatus.DEAD
        )
        stats.add_unit(u2)
        self.assertEqual(stats.team2_dead, 1)
        self.assertEqual(stats.type_counts_team2.get('Pikeman', 0), 0)  # Dead units not counted


class TestResolveFunctions(unittest.TestCase):
    """
    @brief Tests for resolve_letter and resolve_team functions.
    """

    def test_resolve_letter_known(self):
        """
        @brief Test known unit types.
        """
        self.assertEqual(resolve_letter('Knight'), 'K')
        self.assertEqual(resolve_letter('Pikeman'), 'P')
        self.assertEqual(resolve_letter('Crossbowman'), 'C')

    def test_resolve_letter_unknown(self):
        """
        @brief Test unknown unit type defaults to first letter.
        """
        self.assertEqual(resolve_letter('Unknown'), 'U')
        self.assertEqual(resolve_letter(''), '?')

    def test_resolve_team_enum(self):
        """
        @brief Test Team enum passthrough.
        """
        self.assertEqual(resolve_team(Team.A), Team.A)
        self.assertEqual(resolve_team(Team.B), Team.B)

    def test_resolve_team_int(self):
        """
        @brief Test integer team conversion.
        """
        self.assertEqual(resolve_team(1), Team.A)
        self.assertEqual(resolve_team(2), Team.B)
        # Unknown values fall back to Team.A
        self.assertEqual(resolve_team(0), Team.A)

    def test_resolve_team_string(self):
        """
        @brief Test string team conversion.
        """
        self.assertEqual(resolve_team('A'), Team.A)
        self.assertEqual(resolve_team('a'), Team.A)
        self.assertEqual(resolve_team('B'), Team.B)


class TestUnitCacheManager(unittest.TestCase):
    """
    @brief Tests for UnitCacheManager class.
    """

    def setUp(self):
        self.cache = UnitCacheManager()

    def test_update_from_simulation(self):
        """
        @brief Test updating cache from simulation.
        """
        class MockUnit:
            def __init__(self, team):
                self.name = "Knight"
                self.team = team
                self.hp = 100
                self.hp_max = 100
                self.x = 10
                self.y = 10

        class MockScenario:
            def __init__(self):
                self.units = [MockUnit(1), MockUnit(2)]

        class MockSimulation:
            def __init__(self):
                self.scenario = MockScenario()
                self.elapsed_time = 1.5
                self.paused = False

        sim = MockSimulation()
        stats = Stats()
        
        # Mock time.perf_counter to control wall-clock time
        with patch('time.perf_counter') as mock_time:
            # First update: initialize start time
            mock_time.return_value = 100.0
            self.cache.update(sim, stats)
            self.assertEqual(stats.simulation_time, 0.0)
            
            # Second update: 1.5 seconds later
            mock_time.return_value = 101.5
            self.cache.update(sim, stats)
            self.assertEqual(stats.simulation_time, 1.5)

        self.assertEqual(len(self.cache.units), 2)
        self.assertEqual(stats.team1_alive, 1)
        self.assertEqual(stats.team2_alive, 1)


class TestTerminalView(unittest.TestCase):
    """
    @brief Tests for TerminalView class.
    """

    def setUp(self):
        self.view = TerminalView(100, 100)

    def test_init(self):
        """
        @brief Test view initialization.
        """
        self.assertEqual(self.view.board_width, 100)
        self.assertEqual(self.view.board_height, 100)
        self.assertIsNotNone(self.view.state)
        self.assertIsNotNone(self.view.stats)
        self.assertIsNotNone(self.view.camera)
        self.assertIsNotNone(self.view.unit_cache)

    def test_paused_property(self):
        """
        @brief Test paused property getter/setter.
        """
        self.view.paused = True
        self.assertTrue(self.view.state.paused)
        self.assertTrue(self.view.paused)

    def test_tick_speed_property(self):
        """
        @brief Test tick_speed property getter/setter.
        """
        self.view.tick_speed = 60
        self.assertEqual(self.view.state.tick_speed, 60)
        self.assertEqual(self.view.tick_speed, 60)

    def test_debug_snapshot(self):
        """
        @brief Test debug_snapshot method.
        """
        snapshot = self.view.debug_snapshot()
        self.assertIn('time', snapshot)
        self.assertIn('team1_alive', snapshot)
        self.assertIn('team2_alive', snapshot)
        self.assertIn('total_units_cached', snapshot)


class TestTerminalViewCurses(unittest.TestCase):
    """
    @brief Tests for TerminalView curses integration.
    """

    @patch('View.terminal_view.curses')
    def test_init_curses(self, mock_curses):
        """
        @brief Test curses initialization.
        """
        view = TerminalView(100, 100)
        mock_stdscr = MagicMock()
        mock_curses.initscr.return_value = mock_stdscr

        view.init_curses()

        mock_curses.initscr.assert_called_once()
        mock_curses.start_color.assert_called_once()
        mock_curses.noecho.assert_called_once()
        mock_curses.cbreak.assert_called_once()
        mock_stdscr.keypad.assert_called_with(True)
        mock_stdscr.nodelay.assert_called_with(True)

        # Check components are initialized
        self.assertIsNotNone(view.map_renderer)
        self.assertIsNotNone(view.ui_renderer)
        self.assertIsNotNone(view.debug_renderer)
        self.assertIsNotNone(view.input_handler)

    @patch('View.terminal_view.curses')
    def test_cleanup(self, mock_curses):
        """
        @brief Test curses cleanup.
        """
        view = TerminalView(100, 100)
        view.stdscr = MagicMock()

        view.cleanup()

        view.stdscr.keypad.assert_called_with(False)
        mock_curses.nocbreak.assert_called_once()
        mock_curses.echo.assert_called_once()
        mock_curses.endwin.assert_called_once()


class TestInputHandler(unittest.TestCase):
    """
    @brief Tests for InputHandler class.
    """

    def setUp(self):
        self.stdscr = MagicMock()
        self.state = ViewState()
        self.camera = Camera()
        self.handler = InputHandler(
            self.stdscr, self.state, self.camera,
            board_width=100, board_height=100
        )

    def test_quit_key(self):
        """
        @brief Test ESC key returns False.
        """
        self.stdscr.getch.return_value = 27  # ESC
        result = self.handler.process()
        self.assertFalse(result)

    def test_pause_key(self):
        """
        @brief Test P key toggles pause.
        """
        self.stdscr.getch.return_value = ord('p')
        self.assertFalse(self.state.paused)
        self.handler.process()
        self.assertTrue(self.state.paused)

    def test_movement_z(self):
        """
        @brief Test Z key moves camera up.
        """
        self.camera.x = 50
        self.camera.y = 50
        self.stdscr.getch.return_value = ord('z')
        self.handler.process()
        self.assertEqual(self.camera.y, 50 - self.camera.scroll_speed_normal)

    def test_no_key(self):
        """
        @brief Test no key pressed returns True.
        """
        self.stdscr.getch.return_value = -1
        result = self.handler.process()
        self.assertTrue(result)


class TestMapRenderer(unittest.TestCase):
    """
    @brief Tests for MapRenderer class.
    """

    def test_safe_addstr(self):
        """
        @brief Test safe_addstr handles curses errors.
        """
        import curses
        stdscr = MagicMock()
        stdscr.addstr.side_effect = curses.error("test")

        renderer = MapRenderer(stdscr)
        # Should not raise
        renderer.safe_addstr(0, 0, "test")


# =============================================================================
# INTEGRATION TESTS - Verify components work together correctly
# =============================================================================

class TestTickSpeedConsistency(unittest.TestCase):
    """
    @brief Tests for tick_speed consistency across components.
    """

    def test_viewstate_default_matches_constant(self):
        """
        @brief ViewState default tick_speed matches DEFAULT_NUMBER_OF_TICKS_PER_SECOND.
        """
        from Model.simulation import DEFAULT_NUMBER_OF_TICKS_PER_SECOND
        state = ViewState()
        self.assertEqual(state.tick_speed, DEFAULT_NUMBER_OF_TICKS_PER_SECOND)

    def test_terminalview_default_tick_speed(self):
        """
        @brief TerminalView default tick_speed matches DEFAULT_NUMBER_OF_TICKS_PER_SECOND.
        """
        from Model.simulation import DEFAULT_NUMBER_OF_TICKS_PER_SECOND
        view = TerminalView(100, 100)
        self.assertEqual(view.tick_speed, DEFAULT_NUMBER_OF_TICKS_PER_SECOND)

    def test_simulation_controller_has_set_tick_speed(self):
        """
        @brief SimulationController has set_tick_speed method for efficient sync.
        """
        from Controller.simulation_controller import SimulationController
        controller = SimulationController()
        self.assertTrue(hasattr(controller, 'set_tick_speed'))

    def test_simulation_controller_uses_snake_case(self):
        """
        @brief SimulationController.initialize_simulation uses snake_case naming.
        """
        from Controller.simulation_controller import SimulationController
        import inspect
        sig = inspect.signature(SimulationController.initialize_simulation)
        param_names = list(sig.parameters.keys())
        self.assertIn('tick_speed', param_names)


class TestQuitKeys(unittest.TestCase):
    """
    @brief Tests for quit key functionality.
    """

    def test_quit_keys_include_esc(self):
        """
        @brief QUIT_KEYS includes ESC as documented.
        """
        self.assertIn(27, InputHandler.QUIT_KEYS)

    def test_esc_quits(self):
        """
        @brief ESC key returns False to quit.
        """
        stdscr = MagicMock()
        handler = InputHandler(stdscr, ViewState(), Camera(), 100, 100)
        stdscr.getch.return_value = 27
        self.assertFalse(handler.process())


class TestAutoFollow(unittest.TestCase):
    """
    @brief Tests for auto-follow feature.
    """

    def test_auto_follow_disables_on_manual_movement(self):
        """
        @brief Manual camera movement disables auto-follow.
        """
        stdscr = MagicMock()
        state = ViewState()
        state.auto_follow = True
        handler = InputHandler(stdscr, state, Camera(), 100, 100)
        
        stdscr.getch.return_value = ord('z')
        handler.process()
        
        self.assertFalse(state.auto_follow)

    def test_auto_follow_toggle_with_a_key(self):
        """
        @brief A key toggles auto-follow.
        """
        stdscr = MagicMock()
        state = ViewState()
        handler = InputHandler(stdscr, state, Camera(), 100, 100)
        
        stdscr.getch.return_value = ord('a')
        handler.process()
        self.assertTrue(state.auto_follow)
        
        handler.process()
        self.assertFalse(state.auto_follow)


if __name__ == '__main__':
    unittest.main()
