# -*- coding: utf-8 -*-
"""
@file       plotting_tests.py
@brief      Plotting Module Tests - Unit tests for Plotting components.
@author     MedievAIl Team
@version    2.0

@details    Tests for:
            - Data structures (PlotData, BattleResult, LanchesterData, etc.)
            - Scenario-specific plotters
            - Data collector
            - Plotter registry
            - CLI argument parsing
"""
import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

import pandas as pd
import numpy as np


class TestPlotData(unittest.TestCase):
    """Test PlotData dataclass (legacy support)."""

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


class TestLanchesterData(unittest.TestCase):
    """Test LanchesterData pandas DataFrame container."""

    def test_lanchester_data_creation(self):
        """Test LanchesterData can be created with required parameters."""
        from Plotting.data import LanchesterData
        
        data = LanchesterData(
            ai_name="DAFT",
            scenario_name="Lanchester",
            unit_types=["Knight"],
            n_range=range(5, 15, 5),
            num_repetitions=2
        )
        
        self.assertEqual(data.ai_name, "DAFT")
        self.assertEqual(data.scenario_name, "Lanchester")
        self.assertEqual(data.unit_types, ["Knight"])
        self.assertTrue(data.df.empty)

    def test_lanchester_data_add_result(self):
        """Test adding results to LanchesterData."""
        from Plotting.data import LanchesterData
        
        data = LanchesterData(
            ai_name="DAFT",
            scenario_name="Lanchester",
            unit_types=["Knight"],
            n_range=range(5, 15, 5),
            num_repetitions=2
        )
        
        data.add_result({
            'run_id': 1,
            'unit_type': "Knight",
            'n_value': 10,
            'team_a_casualties': 5,
            'team_b_casualties': 10,
            'winner': "B",
            'winner_casualties': 10,
            'duration_ticks': 100
        })
        
        self.assertEqual(len(data.df), 1)
        self.assertEqual(data.df.iloc[0]['unit_type'], "Knight")
        self.assertEqual(data.df.iloc[0]['n_value'], 10)

    def test_lanchester_data_essential_columns(self):
        """Test that LanchesterData uses essential columns."""
        from Plotting.data import LanchesterData
        
        data = LanchesterData(
            ai_name="DAFT",
            scenario_name="Lanchester",
            unit_types=["Knight"],
            n_range=range(5, 10),
            num_repetitions=1
        )
        
        data.add_result({
            'run_id': 1,
            'unit_type': "Knight",
            'n_value': 5,
            'team_a_casualties': 3,
            'team_b_casualties': 5,
            'winner': "B",
            'winner_casualties': 5,
            'duration_ticks': 50
        })
        
        # Check that DataFrame has the essential columns
        expected_cols = {'run_id', 'unit_type', 'n_value', 'team_a_casualties', 
                         'team_b_casualties', 'winner', 'winner_casualties', 'duration_ticks'}
        self.assertTrue(expected_cols.issubset(set(data.df.columns)))

    def test_lanchester_data_summary(self):
        """Test get_summary_by_type_and_n aggregation."""
        from Plotting.data import LanchesterData
        
        data = LanchesterData(
            ai_name="DAFT",
            scenario_name="Lanchester",
            unit_types=["Knight"],
            n_range=range(5, 10),
            num_repetitions=2
        )
        
        # Add multiple runs for same n value
        data.add_result({'run_id': 1, 'unit_type': "Knight", 'n_value': 5, 
                         'team_a_casualties': 3, 'team_b_casualties': 5, 
                         'winner': "B", 'winner_casualties': 5, 'duration_ticks': 50})
        data.add_result({'run_id': 2, 'unit_type': "Knight", 'n_value': 5, 
                         'team_a_casualties': 4, 'team_b_casualties': 6, 
                         'winner': "B", 'winner_casualties': 6, 'duration_ticks': 60})
        
        summary = data.get_summary_by_type_and_n()
        
        self.assertEqual(len(summary), 1)  # One row per n_value/unit_type combo
        self.assertAlmostEqual(summary.iloc[0]['mean_team_a_casualties'], 3.5)
        self.assertAlmostEqual(summary.iloc[0]['mean_team_b_casualties'], 5.5)


class TestScenarioPlotters(unittest.TestCase):
    """Test scenario-specific plotters."""

    def setUp(self):
        """Create temporary output directory."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_plotter_registry_contains_main_plotters(self):
        """Test that main plot types are registered."""
        from Plotting.base import PLOTTERS
        
        # Updated list - removed PlotSurvivors/survivors which don't exist
        expected_plotters = [
            # Lanchester (special case)
            'PlotLanchester', 'lanchester',
            # Generic plot types
            'PlotWinRate', 'winrate',
            'PlotCasualties', 'casualties',
            'PlotDuration', 'duration',
            'PlotComparison', 'comparison',
            'PlotHeatmap', 'heatmap',
            'PlotRawData', 'raw',
        ]
        
        for plotter_name in expected_plotters:
            self.assertIn(plotter_name, PLOTTERS, 
                         f"Missing plotter: {plotter_name}")

    def test_get_plotter_factory(self):
        """Test get_plotter factory function."""
        from Plotting.base import get_plotter, PlotLanchester
        
        plotter = get_plotter('PlotLanchester', self.temp_dir)
        self.assertIsInstance(plotter, PlotLanchester)

    def test_get_plotter_unknown(self):
        """Test get_plotter raises error for unknown plotter."""
        from Plotting.base import get_plotter
        
        with self.assertRaises(ValueError):
            get_plotter('UnknownPlotter', self.temp_dir)

    def test_plotter_with_lanchester_data(self):
        """Test that plotter works with LanchesterData."""
        from Plotting.base import PlotLanchester
        from Plotting.data import LanchesterData
        
        plotter = PlotLanchester(self.temp_dir)
        
        # Create LanchesterData with test data
        data = LanchesterData(
            ai_name="DAFT",
            scenario_name="Lanchester",
            unit_types=["Knight"],
            n_range=range(5, 20, 5),
            num_repetitions=2
        )
        
        # Add test results using proper dict format
        for i, n in enumerate([5, 10, 15]):
            data.add_result({'run_id': i*2, 'unit_type': "Knight", 'n_value': n, 
                             'team_a_casualties': n-1, 'team_b_casualties': n*2-3, 
                             'winner': "B", 'winner_casualties': n*2-3, 'duration_ticks': 50+i*10})
            data.add_result({'run_id': i*2+1, 'unit_type': "Knight", 'n_value': n, 
                             'team_a_casualties': n-2, 'team_b_casualties': n*2-2, 
                             'winner': "B", 'winner_casualties': n*2-2, 'duration_ticks': 55+i*10})
        
        filepath = plotter.plot(data, ai_name="DAFT")
        
        filepath_str = str(filepath)
        self.assertTrue(os.path.exists(filepath_str))
        self.assertTrue(filepath_str.endswith('.png'))


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

    def test_lanchester_constants_defined(self):
        """Test Lanchester module has named constants."""
        from Plotting import lanchester
        
        # Check constants are defined
        self.assertTrue(hasattr(lanchester, 'MAP_SIZE_MIN'))
        self.assertTrue(hasattr(lanchester, 'MAP_SIZE_MAX'))
        self.assertTrue(hasattr(lanchester, 'ENGAGEMENT_GAP'))
        self.assertTrue(hasattr(lanchester, 'MARGIN'))
        self.assertTrue(hasattr(lanchester, 'MAX_UNITS_PER_TEAM'))
        
        # Check reasonable values
        self.assertGreater(lanchester.MAP_SIZE_MAX, lanchester.MAP_SIZE_MIN)
        self.assertGreater(lanchester.MAX_UNITS_PER_TEAM, 0)

    def test_lanchester_max_units_validation(self):
        """Test Lanchester validates max units."""
        from Plotting.lanchester import LanchesterScenario, MAX_UNITS_PER_TEAM
        
        with self.assertRaises(ValueError) as context:
            LanchesterScenario.create('Knight', MAX_UNITS_PER_TEAM + 1)
        
        self.assertIn('exceeds max', str(context.exception))

    def test_lanchester_negative_units_validation(self):
        """Test Lanchester validates positive unit count."""
        from Plotting.lanchester import LanchesterScenario
        
        with self.assertRaises(ValueError):
            LanchesterScenario.create('Knight', 0)
        
        with self.assertRaises(ValueError):
            LanchesterScenario.create('Knight', -5)


if __name__ == '__main__':
    unittest.main()
