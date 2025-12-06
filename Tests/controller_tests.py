import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Controller.main_controller import create_default_scenario, get_strategy_by_name
from Model.strategies import StrategyStart, StrategieDAFT, StrategieBrainDead, StrategieStartSomeIQ, StrategieSimpleAttackBestAvoidWorst
from Model.Units import Unit

class TestMainController(unittest.TestCase):
    
    def test_create_default_scenario(self):
        """Test that the default scenario creates the correct number of units."""
        units, units_a, units_b = create_default_scenario()
        
        # Check total units (5 Knights + 5 Pikemen per team = 20 total)
        self.assertEqual(len(units), 20)
        self.assertEqual(len(units_a), 10)
        self.assertEqual(len(units_b), 10)
        
        # Check unit types in Team A
        knights_a = [u for u in units_a if u.name == "Knight"]
        pikemen_a = [u for u in units_a if u.name == "Pikeman"]
        self.assertEqual(len(knights_a), 5)
        self.assertEqual(len(pikemen_a), 5)
        
        # Check teams
        for u in units_a:
            self.assertEqual(u.team, 1)
        for u in units_b:
            self.assertEqual(u.team, 2)

    def test_get_strategy_by_name_daft(self):
        """Test retrieving DAFT strategy."""
        sS, sT = get_strategy_by_name("daft")
        self.assertIsInstance(sS, StrategyStart)
        self.assertIsInstance(sT, StrategieDAFT)

    def test_get_strategy_by_name_braindead(self):
        """Test retrieving BrainDead strategy."""
        sS, sT = get_strategy_by_name("braindead")
        self.assertIsInstance(sS, StrategyStart)
        self.assertIsInstance(sT, StrategieBrainDead)

    def test_get_strategy_by_name_someiq(self):
        """Test retrieving SomeIQ strategy."""
        sS, sT = get_strategy_by_name("someiq")
        self.assertIsInstance(sS, StrategieStartSomeIQ)
        self.assertIsInstance(sT, StrategieSimpleAttackBestAvoidWorst)

    def test_get_strategy_by_name_case_insensitive(self):
        """Test that strategy names are case insensitive."""
        sS, sT = get_strategy_by_name("DAFT")
        self.assertIsInstance(sT, StrategieDAFT)
        
        sS, sT = get_strategy_by_name("BrainDead")
        self.assertIsInstance(sT, StrategieBrainDead)

    def test_get_strategy_by_name_default(self):
        """Test that unknown names return the default strategy (DAFT)."""
        sS, sT = get_strategy_by_name("unknown_strategy")
        self.assertIsInstance(sS, StrategyStart)
        self.assertIsInstance(sT, StrategieDAFT)

if __name__ == '__main__':
    unittest.main()
