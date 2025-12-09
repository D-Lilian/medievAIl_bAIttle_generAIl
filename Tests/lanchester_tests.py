# -*- coding: utf-8 -*-
"""
@file lanchester_tests.py
@brief Tests for Lanchester's Laws scenarios and plotters

@details
Unit tests for:
- LanchesterScenario setup and execution
- BattleResult data structure
- LanchesterPlotter data preparation

"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Model.scenarios.base_scenario import BattleResult, MockGeneral
from Model.scenarios.lanchester_scenario import LanchesterScenario, LanchesterExperiment


class TestBattleResult(unittest.TestCase):
    """Test the BattleResult dataclass"""
    
    def test_casualty_rate(self):
        result = BattleResult(
            scenario_name="Test",
            team_a_initial=10,
            team_a_remaining=3,
            team_a_casualties=7,
            team_b_initial=20,
            team_b_remaining=15,
            team_b_casualties=5
        )
        
        self.assertAlmostEqual(result.team_a_casualty_rate, 0.7)
        self.assertAlmostEqual(result.team_b_casualty_rate, 0.25)
    
    def test_hp_loss_rate(self):
        result = BattleResult(
            scenario_name="Test",
            team_a_total_hp_initial=1000,
            team_a_total_hp_remaining=300,
            team_b_total_hp_initial=2000,
            team_b_total_hp_remaining=1500
        )
        
        self.assertAlmostEqual(result.team_a_hp_loss_rate, 0.7)
        self.assertAlmostEqual(result.team_b_hp_loss_rate, 0.25)
    
    def test_to_dict(self):
        result = BattleResult(
            scenario_name="Test",
            parameters={'n': 10},
            team_a_initial=10,
            team_a_remaining=0,
            team_a_casualties=10,
            team_b_initial=20,
            team_b_remaining=15,
            team_b_casualties=5,
            winner="B"
        )
        
        d = result.to_dict()
        self.assertEqual(d['scenario_name'], "Test")
        self.assertEqual(d['parameters']['n'], 10)
        self.assertEqual(d['team_a']['casualties'], 10)
        self.assertEqual(d['team_b']['remaining'], 15)
        self.assertEqual(d['winner'], "B")


class TestLanchesterScenario(unittest.TestCase):
    """Test LanchesterScenario setup"""
    
    def test_scenario_creation(self):
        scenario = LanchesterScenario()
        scenario.setup(unit_type="Knight", n=5)
        
        # Check unit counts
        self.assertEqual(len(scenario.units_a), 5)
        self.assertEqual(len(scenario.units_b), 10)  # 2*N
        self.assertEqual(len(scenario.units), 15)  # Total
    
    def test_scenario_name(self):
        scenario = LanchesterScenario()
        scenario.setup(unit_type="Crossbowman", n=10)
        
        self.assertEqual(scenario.name, "Lanchester(Crossbowman, 10)")
    
    def test_invalid_unit_type(self):
        scenario = LanchesterScenario()
        
        with self.assertRaises(ValueError):
            scenario.setup(unit_type="InvalidUnit", n=5)
    
    def test_melee_alias(self):
        scenario = LanchesterScenario()
        scenario.setup(unit_type="melee", n=5)
        
        # Should create Knights (melee alias)
        self.assertEqual(scenario.units_a[0].name, "Knight")
    
    def test_ranged_alias(self):
        scenario = LanchesterScenario()
        scenario.setup(unit_type="ranged", n=5)
        
        # Should create Crossbowmen (ranged alias)
        self.assertEqual(scenario.units_a[0].name, "Crossbowman")
    
    def test_reset(self):
        scenario = LanchesterScenario()
        scenario.setup(unit_type="Knight", n=5)
        
        self.assertEqual(len(scenario.units), 15)
        
        scenario.reset()
        
        self.assertEqual(len(scenario.units), 0)
        self.assertEqual(len(scenario.units_a), 0)
        self.assertEqual(len(scenario.units_b), 0)
    
    def test_parameters(self):
        scenario = LanchesterScenario()
        scenario.setup(unit_type="Pikeman", n=7)
        
        params = scenario._get_parameters()
        self.assertEqual(params['unit_type'], "Pikeman")
        self.assertEqual(params['n'], 7)
        self.assertEqual(params['team_a_count'], 7)
        self.assertEqual(params['team_b_count'], 14)


class TestMockGeneral(unittest.TestCase):
    """Test MockGeneral doesn't raise errors"""
    
    def test_mock_general_methods(self):
        general = MockGeneral()
        
        # These should all run without error
        general.BeginStrategy()
        general.CreateOrders()
        general.notify("SomeType")
        general.HandleUnitTypeDepleted("SomeType")


class TestLanchesterScenarioRun(unittest.TestCase):
    """Integration tests for running scenarios (may be slow)"""
    
    def test_quick_battle(self):
        """Run a very quick battle to test the full pipeline"""
        scenario = LanchesterScenario()
        scenario.setup(unit_type="Knight", n=2)  # Small N for speed
        
        result = scenario.run(tick_speed=1000, unlocked=True)
        
        # Basic sanity checks
        self.assertEqual(result.team_a_initial, 2)
        self.assertEqual(result.team_b_initial, 4)
        self.assertIn(result.winner, ['A', 'B', 'draw'])
        self.assertGreater(result.ticks, 0)
    
    def test_result_consistency(self):
        """Check that result values are consistent"""
        scenario = LanchesterScenario()
        scenario.setup(unit_type="Knight", n=3)
        
        result = scenario.run(tick_speed=1000, unlocked=True)
        
        # Casualties should equal initial - remaining
        self.assertEqual(
            result.team_a_casualties,
            result.team_a_initial - result.team_a_remaining
        )
        self.assertEqual(
            result.team_b_casualties,
            result.team_b_initial - result.team_b_remaining
        )


if __name__ == '__main__':
    unittest.main()
