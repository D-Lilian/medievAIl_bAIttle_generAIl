import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from View.terminal_view import UniteRepr, UnitStatus, Team, Camera, TerminalView

class TestUniteRepr(unittest.TestCase):
    def test_alive_property(self):
        u = UniteRepr("Knight", Team.A, "K", 10, 10, 100, 100, UnitStatus.ALIVE)
        self.assertTrue(u.alive)
        u.status = UnitStatus.DEAD
        self.assertFalse(u.alive)

    def test_hp_percent(self):
        u = UniteRepr("Knight", Team.A, "K", 10, 10, 50, 100, UnitStatus.ALIVE)
        self.assertEqual(u.hp_percent, 50.0)
        u.hp = 0
        self.assertEqual(u.hp_percent, 0.0)
        u.hp_max = 0
        self.assertEqual(u.hp_percent, 0.0)

class TestCamera(unittest.TestCase):
    def setUp(self):
        self.camera = Camera(x=0, y=0, zoom_level=1)

    def test_move_normal(self):
        # In rotated view logic:
        # move(dx, dy) -> y += dx * speed, x += dy * speed
        # dx=1 (right key) -> y increases (horizontal on screen is vertical on board)
        # dy=1 (down key) -> x increases (vertical on screen is horizontal on board)
        
        initial_x = self.camera.x
        initial_y = self.camera.y
        self.camera.move(1, 0, fast=False) # Move "Right" on screen -> +y on board
        self.assertEqual(self.camera.y, initial_y + self.camera.scroll_speed_normal)
        self.assertEqual(self.camera.x, initial_x)

        self.camera.move(0, 1, fast=False) # Move "Down" on screen -> +x on board
        self.assertEqual(self.camera.x, initial_x + self.camera.scroll_speed_normal)

    def test_move_fast(self):
        initial_y = self.camera.y
        self.camera.move(1, 0, fast=True)
        self.assertEqual(self.camera.y, initial_y + self.camera.scroll_speed_fast)

    def test_clamp(self):
        # Board 100x100, Terminal 20x20
        # visible_w = term_h * zoom = 20
        # visible_h = term_w * zoom = 20
        # max_x = 100 - 20 = 80
        # max_y = 100 - 20 = 80
        
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

class TestTerminalView(unittest.TestCase):
    def setUp(self):
        self.view = TerminalView(100, 100)

    def test_resolve_letter(self):
        self.assertEqual(self.view._resolve_letter('Knight'), 'K')
        self.assertEqual(self.view._resolve_letter('Unknown'), 'U')
        self.assertEqual(self.view._resolve_letter(''), '?')

    def test_resolve_team(self):
        self.assertEqual(self.view._resolve_team(Team.A), Team.A)
        self.assertEqual(self.view._resolve_team(1), Team.A)
        self.assertEqual(self.view._resolve_team('B'), Team.B)

    def test_extract_unit_fields(self):
        # Mock a unit object
        class MockUnit:
            def __init__(self):
                self.name = "TestUnit"
                self.team = 1
                self.hp = 100
                self.hp_max = 100
                self.x = 10.0
                self.y = 20.0
                self.damage_dealt = 50
                self.target = None
        
        unit = MockUnit()
        fields = self.view._extract_unit_fields(unit)
        
        self.assertEqual(fields['type'], "TestUnit")
        self.assertEqual(fields['team'], 1)
        self.assertEqual(fields['hp'], 100)
        self.assertEqual(fields['damage_dealt'], 50)
        self.assertTrue(fields['alive'])

    def test_update_units_cache(self):
        # Mock simulation and units
        class MockUnit:
            def __init__(self, team):
                self.name = "Knight"
                self.team = team
                self.hp = 100
                self.hp_max = 100
                self.x = 10
                self.y = 10
        
        class MockSimulation:
            def __init__(self):
                self.units = [MockUnit(1), MockUnit(2)]
                self.elapsed_time = 1.5
        
        sim = MockSimulation()
        self.view.update_units_cache(sim)
        
        self.assertEqual(len(self.view.units_cache), 2)
        self.assertEqual(self.view.team1_units, 1)
        self.assertEqual(self.view.team2_units, 1)
        self.assertEqual(self.view.simulation_time, 1.5)

class TestTerminalViewCurses(unittest.TestCase):
    @patch('View.terminal_view.curses')
    def test_init_curses(self, mock_curses):
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

    @patch('View.terminal_view.curses')
    def test_draw_map(self, mock_curses):
        view = TerminalView(100, 100)
        view.stdscr = MagicMock()
        view.stdscr.getmaxyx.return_value = (24, 80) # h, w
        
        # Add a unit to cache
        u = UniteRepr("Knight", Team.A, "K", 10, 10, 100, 100, UnitStatus.ALIVE)
        view.units_cache = [u]
        
        # Set camera to 0,0
        view.camera.x = 0
        view.camera.y = 0
        
        view.draw_map()
        
        view.stdscr.clear.assert_called_once()
        # Check if addstr was called for the unit
        # Unit at 10,10. Rotated view:
        # screen_x = (y - cam_y) + 1 = 10 + 1 = 11
        # screen_y = (x - cam_x) + 1 = 10 + 1 = 11
        # addstr(y, x, str, attr)
        view.stdscr.addstr.assert_any_call(11, 11, 'K', unittest.mock.ANY)

    @patch('View.terminal_view.curses')
    def test_handle_input_quit(self, mock_curses):
        view = TerminalView(100, 100)
        view.stdscr = MagicMock()
        view.stdscr.getch.return_value = 27 # ESC
        
        result = view.handle_input()
        self.assertFalse(result)

    @patch('View.terminal_view.curses')
    def test_handle_input_move(self, mock_curses):
        view = TerminalView(100, 100)
        view.stdscr = MagicMock()
        view.stdscr.getch.return_value = ord('z') # Up (in QWERTY/ZQSD mapping logic)
        
        initial_y = view.camera.y
        view.handle_input()
        
        # 'z' calls move(0, -1) -> y += 0, x += -1 * speed (rotated logic in move)
        # Wait, let's check move logic again:
        # move(dx, dy): y += dx * speed, x += dy * speed
        # 'z' -> move(0, -1) -> dx=0, dy=-1 -> y unchanged, x decreases
        # But wait, 'z' is usually UP.
        # In handle_input:
        # if key == 'z': move(0, -1)
        # In move(dx, dy): self.y += dx..., self.x += dy...
        # So move(0, -1) -> self.x += -1 * speed.
        # x is vertical on board (rows). Decreasing x means moving "Up" on board (lower row index).
        # So 'z' moves Up. Correct.
        
        # Let's verify camera x changed
        # Initial x is set in __init__ to center.
        # Let's force it to something known
        view.camera.x = 50
        view.camera.y = 50
        view.handle_input()
        
        self.assertEqual(view.camera.x, 50 - view.camera.scroll_speed_normal)

if __name__ == '__main__':
    unittest.main()
