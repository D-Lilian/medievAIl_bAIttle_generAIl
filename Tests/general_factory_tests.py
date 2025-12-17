# -*- coding: utf-8 -*-
"""
@file general_factory_tests.py
@brief General Factory Tests - Unit tests for the AI General Factory

@details
Tests for:
- create_general function
- get_available_ais function
- All AI strategies (BRAINDEAD, DAFT, SOMEIQ, RPC)
- Error handling for unknown AIs
"""
import unittest
from unittest.mock import Mock


class TestGeneralFactory(unittest.TestCase):
    """Test general_factory module functions."""

    def test_get_available_ais(self):
        """Test get_available_ais returns expected list."""
        from Model.general_factory import get_available_ais, AVAILABLE_AIS
        
        ais = get_available_ais()
        
        self.assertIsInstance(ais, list)
        self.assertIn('BRAINDEAD', ais)
        self.assertIn('DAFT', ais)
        self.assertIn('SOMEIQ', ais)
        self.assertIn('RPC', ais)
        self.assertEqual(len(ais), 4)
        
        # Should return a copy, not the original
        ais.append('TEST')
        self.assertNotIn('TEST', AVAILABLE_AIS)

    def test_create_general_braindead(self):
        """Test creating a BRAINDEAD general."""
        from Model.general_factory import create_general
        from Model.generals import General
        
        # Create mock units
        units_a = [Mock()]
        units_b = [Mock()]
        
        general = create_general('BRAINDEAD', units_a, units_b)
        
        self.assertIsInstance(general, General)

    def test_create_general_daft(self):
        """Test creating a DAFT general."""
        from Model.general_factory import create_general
        from Model.generals import General
        
        units_a = [Mock()]
        units_b = [Mock()]
        
        general = create_general('DAFT', units_a, units_b)
        
        self.assertIsInstance(general, General)

    def test_create_general_someiq(self):
        """Test creating a SOMEIQ general."""
        from Model.general_factory import create_general
        from Model.generals import General
        
        units_a = [Mock()]
        units_b = [Mock()]
        
        general = create_general('SOMEIQ', units_a, units_b)
        
        self.assertIsInstance(general, General)

    def test_create_general_rpc(self):
        """Test creating a RPC general."""
        from Model.general_factory import create_general
        from Model.generals import General
        
        units_a = [Mock()]
        units_b = [Mock()]
        
        general = create_general('RPC', units_a, units_b)
        
        self.assertIsInstance(general, General)

    def test_create_general_case_insensitive(self):
        """Test that AI names are case insensitive."""
        from Model.general_factory import create_general
        from Model.generals import General
        
        units_a = [Mock()]
        units_b = [Mock()]
        
        # Test various cases
        for name in ['braindead', 'BrainDead', 'BRAINDEAD', 'Braindead']:
            general = create_general(name, units_a, units_b)
            self.assertIsInstance(general, General)

    def test_create_general_unknown_raises_error(self):
        """Test that unknown AI name raises ValueError."""
        from Model.general_factory import create_general
        
        units_a = [Mock()]
        units_b = [Mock()]
        
        with self.assertRaises(ValueError) as context:
            create_general('UNKNOWN_AI', units_a, units_b)
        
        self.assertIn('Unknown AI', str(context.exception))
        self.assertIn('UNKNOWN_AI', str(context.exception))
        # Should list available AIs
        self.assertIn('BRAINDEAD', str(context.exception))

    def test_create_general_with_real_units(self):
        """Test create_general with real unit objects."""
        from Model.general_factory import create_general
        from Model.generals import General
        from Model.units import Knight, Crossbowman, Pikeman
        
        # Create real units
        units_a = [
            Knight(team='A', x=10, y=10),
            Crossbowman(team='A', x=15, y=10),
            Pikeman(team='A', x=20, y=10),
        ]
        units_b = [
            Knight(team='B', x=50, y=10),
            Crossbowman(team='B', x=55, y=10),
        ]
        
        for ai_name in ['BRAINDEAD', 'DAFT', 'SOMEIQ', 'RPC']:
            general = create_general(ai_name, units_a, units_b)
            self.assertIsInstance(general, General)


class TestGeneralFactoryStrategies(unittest.TestCase):
    """Test that created generals have correct strategies."""

    def test_braindead_strategies(self):
        """Test BRAINDEAD general has BrainDead strategies."""
        from Model.general_factory import create_general
        from Model.strategies import StrategieBrainDead
        from Model.units import UnitType
        
        units_a = [Mock()]
        units_b = [Mock()]
        
        general = create_general('BRAINDEAD', units_a, units_b)
        
        # Check strategy types
        for unit_type in [UnitType.KNIGHT, UnitType.CROSSBOWMAN, UnitType.PIKEMAN]:
            self.assertIsInstance(general.sT[unit_type], StrategieBrainDead)

    def test_daft_strategies(self):
        """Test DAFT general has DAFT strategies."""
        from Model.general_factory import create_general
        from Model.strategies import StrategieDAFT
        from Model.units import UnitType
        
        units_a = [Mock()]
        units_b = [Mock()]
        
        general = create_general('DAFT', units_a, units_b)
        
        for unit_type in [UnitType.KNIGHT, UnitType.CROSSBOWMAN, UnitType.PIKEMAN]:
            self.assertIsInstance(general.sT[unit_type], StrategieDAFT)

    def test_someiq_has_start_strategy(self):
        """Test SOMEIQ general has start strategy."""
        from Model.general_factory import create_general
        from Model.strategies import StrategieStartSomeIQ
        
        units_a = [Mock()]
        units_b = [Mock()]
        
        general = create_general('SOMEIQ', units_a, units_b)
        
        # SOMEIQ should have a start strategy
        self.assertIsNotNone(general.sS)
        self.assertIsInstance(general.sS, StrategieStartSomeIQ)

    def test_rpc_counter_strategies(self):
        """Test RPC general has counter strategies."""
        from Model.general_factory import create_general
        from Model.strategies import StrategieSimpleAttackBestAvoidWorst
        from Model.units import UnitType
        
        units_a = [Mock()]
        units_b = [Mock()]
        
        general = create_general('RPC', units_a, units_b)
        
        for unit_type in [UnitType.KNIGHT, UnitType.CROSSBOWMAN, UnitType.PIKEMAN]:
            self.assertIsInstance(general.sT[unit_type], StrategieSimpleAttackBestAvoidWorst)


class TestGeneralFactoryIntegration(unittest.TestCase):
    """Integration tests for general_factory with other modules."""

    def test_used_by_tournament_runner(self):
        """Test that Tournament.runner uses general_factory."""
        from Tournament import runner
        
        # Check that runner imports from general_factory
        self.assertTrue(hasattr(runner, 'create_general'))

    def test_used_by_plotting_collector(self):
        """Test that Plotting.collector uses general_factory."""
        from Plotting import collector
        
        # Check that collector imports from general_factory
        self.assertTrue(hasattr(collector, 'create_general'))


if __name__ == '__main__':
    unittest.main()
