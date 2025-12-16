# -*- coding: utf-8 -*-
"""
@file tournament_tests.py
@brief Tournament Module Tests - Unit tests for Tournament components

@details
Tests for:
- TournamentConfig
- TournamentResults
- MatchResult
- TournamentReportGenerator
- TournamentController

"""
import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock


class TestTournamentConfig(unittest.TestCase):
    """Test TournamentConfig dataclass."""

    def test_config_creation(self):
        """Test TournamentConfig can be created."""
        from Tournament.config import TournamentConfig
        
        config = TournamentConfig(
            generals=['DAFT', 'BRAINDEAD'],
            scenarios=['cavalry_charge'],
            rounds_per_matchup=5
        )
        
        self.assertEqual(config.generals, ['DAFT', 'BRAINDEAD'])
        self.assertEqual(config.scenarios, ['cavalry_charge'])
        self.assertEqual(config.rounds_per_matchup, 5)

    def test_config_defaults(self):
        """Test TournamentConfig default values."""
        from Tournament.config import TournamentConfig
        
        config = TournamentConfig(
            generals=['DAFT'],
            scenarios=['cavalry_charge']
        )
        
        self.assertEqual(config.rounds_per_matchup, 10)
        self.assertTrue(config.alternate_positions)


class TestMatchResult(unittest.TestCase):
    """Test MatchResult dataclass."""

    def test_match_result_creation(self):
        """Test MatchResult can be created."""
        from Tournament.results import MatchResult
        
        result = MatchResult(
            general_a='DAFT',
            general_b='BRAINDEAD',
            scenario_name='cavalry_charge',
            winner='A',
            ticks=100,
            team_a_survivors=80,
            team_b_survivors=0,
            team_a_casualties=20,
            team_b_casualties=100
        )
        
        self.assertEqual(result.general_a, 'DAFT')
        self.assertEqual(result.winner, 'A')

    def test_winner_name_property(self):
        """Test winner_name property."""
        from Tournament.results import MatchResult
        
        result = MatchResult(
            general_a='DAFT',
            general_b='BRAINDEAD',
            scenario_name='cavalry_charge',
            winner='A',
            ticks=100,
            team_a_survivors=80,
            team_b_survivors=0,
            team_a_casualties=20,
            team_b_casualties=100
        )
        
        self.assertEqual(result.winner_name, 'DAFT')


class TestTournamentResults(unittest.TestCase):
    """Test TournamentResults dataclass and methods."""

    def test_results_creation(self):
        """Test TournamentResults can be created."""
        from Tournament.config import TournamentConfig
        from Tournament.results import TournamentResults
        
        config = TournamentConfig(
            generals=['DAFT', 'BRAINDEAD'],
            scenarios=['cavalry_charge']
        )
        results = TournamentResults(config=config)
        
        self.assertEqual(results.config.generals, ['DAFT', 'BRAINDEAD'])
        self.assertEqual(results.matches, [])

    def test_results_add_match(self):
        """Test adding match results."""
        from Tournament.config import TournamentConfig
        from Tournament.results import TournamentResults, MatchResult
        
        config = TournamentConfig(
            generals=['DAFT', 'BRAINDEAD'],
            scenarios=['cavalry_charge']
        )
        results = TournamentResults(config=config)
        
        match = MatchResult(
            general_a='DAFT',
            general_b='BRAINDEAD',
            scenario_name='cavalry_charge',
            winner='A',
            ticks=100,
            team_a_survivors=80,
            team_b_survivors=0,
            team_a_casualties=20,
            team_b_casualties=100
        )
        
        results.add_match(match)
        self.assertEqual(len(results.matches), 1)

    def test_results_get_overall_scores(self):
        """Test overall score calculation."""
        from Tournament.config import TournamentConfig
        from Tournament.results import TournamentResults, MatchResult
        
        config = TournamentConfig(
            generals=['DAFT', 'BRAINDEAD'],
            scenarios=['cavalry_charge']
        )
        results = TournamentResults(config=config)
        
        # Add some matches
        for _ in range(3):
            results.add_match(MatchResult(
                general_a='DAFT', general_b='BRAINDEAD',
                scenario_name='cavalry_charge', winner='A',
                ticks=100, team_a_survivors=80, team_b_survivors=0,
                team_a_casualties=20, team_b_casualties=100
            ))
        
        scores = results.get_overall_scores()
        self.assertEqual(scores['DAFT']['wins'], 3)
        self.assertEqual(scores['BRAINDEAD']['losses'], 3)


class TestTournamentRunner(unittest.TestCase):
    """Test TournamentRunner class."""

    def test_runner_creation(self):
        """Test TournamentRunner can be created."""
        from Tournament.config import TournamentConfig
        from Tournament.runner import TournamentRunner
        
        config = TournamentConfig(
            generals=['DAFT', 'BRAINDEAD'],
            scenarios=['cavalry_charge'],
            rounds_per_matchup=5
        )
        runner = TournamentRunner(config)
        
        self.assertEqual(runner.config.generals, ['DAFT', 'BRAINDEAD'])
        self.assertEqual(runner.config.rounds_per_matchup, 5)

    def test_runner_available_generals(self):
        """Test available generals list."""
        from Tournament.runner import TournamentRunner
        
        self.assertIn('DAFT', TournamentRunner.AVAILABLE_GENERALS)
        self.assertIn('BRAINDEAD', TournamentRunner.AVAILABLE_GENERALS)
        self.assertIn('SOMEIQ', TournamentRunner.AVAILABLE_GENERALS)

    def test_runner_scenario_map(self):
        """Test scenario map is populated."""
        from Tournament.runner import TournamentRunner
        
        self.assertIn('cavalry_charge', TournamentRunner.SCENARIO_MAP)
        self.assertIn('defensive_siege', TournamentRunner.SCENARIO_MAP)


class TestTournamentReport(unittest.TestCase):
    """Test TournamentReportGenerator."""

    def setUp(self):
        """Create temporary directory."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_report_generator_creation(self):
        """Test report generator can be created."""
        from Tournament.report import TournamentReportGenerator
        
        gen = TournamentReportGenerator(self.temp_dir)
        self.assertEqual(gen.output_dir, self.temp_dir)

    def test_report_generates_html(self):
        """Test report generates HTML file."""
        from Tournament.report import TournamentReportGenerator
        from Tournament.config import TournamentConfig
        from Tournament.results import TournamentResults, MatchResult
        
        gen = TournamentReportGenerator(self.temp_dir)
        
        config = TournamentConfig(
            generals=['DAFT', 'BRAINDEAD'],
            scenarios=['cavalry_charge']
        )
        results = TournamentResults(config=config)
        
        # Add some matches
        results.add_match(MatchResult(
            general_a='DAFT', general_b='BRAINDEAD',
            scenario_name='cavalry_charge', winner='A',
            ticks=100, team_a_survivors=80, team_b_survivors=0,
            team_a_casualties=20, team_b_casualties=100
        ))
        
        filepath = gen.generate(results)
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.html'))


class TestTournamentController(unittest.TestCase):
    """Test TournamentController."""

    def test_controller_exists(self):
        """Test TournamentController can be imported."""
        from Controller.tournament_controller import TournamentController
        
        self.assertTrue(hasattr(TournamentController, 'run_tournament'))


if __name__ == '__main__':
    unittest.main()
