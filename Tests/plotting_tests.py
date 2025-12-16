# -*- coding: utf-8 -*-
"""
@file plotting_tests.py
@brief Plotting Module Tests - Unit tests for Plotting components

@details
Tests for:
- Data structures (PlotData, BattleResult, etc.)
- Scenario-specific plotters
- Data collector
- Plotter registry

"""
import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock


class TestPlotData(unittest.TestCase):
    """Test PlotData dataclass."""

    def test_plot_data_creation(self):
        """Test PlotData can be created with default values."""
        from Plotting.data import PlotData
        
        data = PlotData(unit_type="Knight")
        self.assertEqual(data.unit_type, "Knight")
        self.assertEqual(data.n_values, [])
        self.assertEqual(data.avg_team_a_casualties, [])
        self.assertEqual(data.avg_team_b_casualties, [])

    def test_plot_data_add_point(self):
        """Test adding data points to PlotData."""
        from Plotting.data import PlotData, AggregatedResults
        
        data = PlotData(unit_type="Knight")
        
        # Create mock aggregated results
        agg = AggregatedResults(
            scenario_name="Lanchester",
            scenario_params={"n": 10},
            num_runs=5
        )
        
        data.add_data_point(10, agg)
        self.assertEqual(data.n_values, [10])


class TestBattleResult(unittest.TestCase):
    """Test BattleResult dataclass."""

    def test_battle_result_creation(self):
        """Test BattleResult can be created."""
        from Plotting.data import BattleResult, TeamStats
        
        result = BattleResult(
            ticks=100,
            winner='A',
            team_a=TeamStats(initial_units=10, casualties=2),
            team_b=TeamStats(initial_units=10, casualties=8)
        )
        
        self.assertEqual(result.ticks, 100)
        self.assertEqual(result.winner, 'A')
        self.assertEqual(result.team_a.casualties, 2)
        self.assertEqual(result.team_b.casualties, 8)

    def test_team_stats_casualty_rate(self):
        """Test TeamStats casualty rate calculation."""
        from Plotting.data import TeamStats
        
        stats = TeamStats(initial_units=10, casualties=3)
        self.assertAlmostEqual(stats.casualty_rate, 0.3)


class TestScenarioPlotters(unittest.TestCase):
    """Test scenario-specific plotters."""

    def setUp(self):
        """Create temporary output directory."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_plotter_registry_contains_all_scenarios(self):
        """Test that all scenario plotters are registered."""
        from Plotting.scenario_plotters import SCENARIO_PLOTTERS
        
        expected_scenarios = [
            'Lanchester', 'lanchester',
            'ClassicMedieval', 'classic_medieval_battle',
            'CavalryCharge', 'cavalry_charge',
            'DefensiveSiege', 'defensive_siege',
            'CannaeEnvelopment', 'cannae_envelopment',
            'RomanLegion', 'roman_legion',
            'BritishSquare', 'british_square',
        ]
        
        for scenario in expected_scenarios:
            self.assertIn(scenario, SCENARIO_PLOTTERS, 
                         f"Missing plotter for scenario: {scenario}")

    def test_get_scenario_plotter(self):
        """Test get_scenario_plotter factory function."""
        from Plotting.scenario_plotters import get_scenario_plotter, PlotLanchester
        
        plotter = get_scenario_plotter('Lanchester', self.temp_dir)
        self.assertIsInstance(plotter, PlotLanchester)

    def test_get_scenario_plotter_unknown(self):
        """Test get_scenario_plotter raises error for unknown scenario."""
        from Plotting.scenario_plotters import get_scenario_plotter
        
        with self.assertRaises(ValueError):
            get_scenario_plotter('UnknownScenario', self.temp_dir)

    def test_plotter_generates_file(self):
        """Test that plotter generates a PNG file."""
        from Plotting.scenario_plotters import PlotLanchester
        from Plotting.data import PlotData
        
        plotter = PlotLanchester(self.temp_dir)
        
        # Create mock data
        data = {
            "Knight": PlotData(unit_type="Knight"),
        }
        data["Knight"].n_values = [5, 10, 15]
        data["Knight"].avg_winner_casualties = [0.5, 1.0, 1.5]
        data["Knight"].team_b_win_rates = [1.0, 1.0, 1.0]
        data["Knight"].avg_ticks = [50, 60, 70]
        data["Knight"].avg_team_a_casualties = [5, 10, 15]
        data["Knight"].avg_team_b_casualties = [0.5, 1.0, 1.5]
        
        filepath = plotter.plot(data)
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.png'))


class TestPlotterRegistry(unittest.TestCase):
    """Test the global PLOTTERS registry."""

    def test_plotters_registry_not_empty(self):
        """Test that PLOTTERS registry is populated."""
        from Plotting import PLOTTERS
        
        self.assertGreater(len(PLOTTERS), 0)

    def test_get_plotter_function(self):
        """Test get_plotter factory function."""
        from Plotting import get_plotter, BasePlotter
        
        plotter = get_plotter('PlotCasualties')
        self.assertIsInstance(plotter, BasePlotter)

    def test_get_plotter_unknown(self):
        """Test get_plotter raises error for unknown plotter."""
        from Plotting import get_plotter
        
        with self.assertRaises(ValueError):
            get_plotter('UnknownPlotter')


class TestParseHelpers(unittest.TestCase):
    """Test parse_types_arg and parse_range_arg helpers."""

    def test_parse_types_arg_brackets(self):
        """Test parsing types with brackets."""
        from Plotting.collector import parse_types_arg
        
        result = parse_types_arg('[Knight,Crossbow]')
        self.assertEqual(result, ['Knight', 'Crossbowman'])

    def test_parse_types_arg_no_brackets(self):
        """Test parsing types without brackets."""
        from Plotting.collector import parse_types_arg
        
        result = parse_types_arg('Knight,Pikeman')
        self.assertEqual(result, ['Knight', 'Pikeman'])

    def test_parse_types_arg_single(self):
        """Test parsing single type."""
        from Plotting.collector import parse_types_arg
        
        result = parse_types_arg('[Knight]')
        self.assertEqual(result, ['Knight'])

    def test_parse_range_arg_standard(self):
        """Test parsing standard range."""
        from Plotting.collector import parse_range_arg
        
        result = parse_range_arg('range(1,10)')
        self.assertEqual(list(result), list(range(1, 10)))

    def test_parse_range_arg_with_step(self):
        """Test parsing range with step."""
        from Plotting.collector import parse_range_arg
        
        result = parse_range_arg('range(5,50,5)')
        self.assertEqual(list(result), list(range(5, 50, 5)))

    def test_parse_range_arg_dash_format(self):
        """Test parsing dash format range."""
        from Plotting.collector import parse_range_arg
        
        result = parse_range_arg('1-10')
        self.assertEqual(list(result), list(range(1, 11)))


class TestLanchesterScenario(unittest.TestCase):
    """Test Lanchester scenario generation."""

    def test_lanchester_creates_asymmetric_battle(self):
        """Test Lanchester creates N vs 2N scenario."""
        from Plotting.lanchester import LanchesterScenario
        
        scenario = LanchesterScenario.create('Knight', 10)
        
        self.assertEqual(len(scenario.units_a), 10)
        self.assertEqual(len(scenario.units_b), 20)

    def test_lanchester_unknown_unit_type(self):
        """Test Lanchester raises error for unknown unit type."""
        from Plotting.lanchester import LanchesterScenario
        
        with self.assertRaises(ValueError):
            LanchesterScenario.create('UnknownUnit', 10)

    def test_lanchester_supported_types(self):
        """Test Lanchester supports all expected unit types."""
        from Plotting.lanchester import LanchesterScenario
        
        for unit_type in ['Knight', 'Crossbowman', 'Pikeman']:
            scenario = LanchesterScenario.create(unit_type, 5)
            self.assertEqual(len(scenario.units_a), 5)
            self.assertEqual(len(scenario.units_b), 10)


if __name__ == '__main__':
    unittest.main()
