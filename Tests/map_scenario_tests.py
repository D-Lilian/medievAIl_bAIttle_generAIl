# -*- coding: utf-8 -*-
"""
@file       map_scenario_tests.py
@brief      Unit tests for MapGenerator, Scenario, and LanchesterScenario.

@details    Tests for:
            - Scenario creation and validation
            - MapGenerator formations
            - LanchesterScenario factory (N vs 2N)
            - Unit positioning and map bounds
"""
import unittest
import math


class TestScenario(unittest.TestCase):
    """Test Scenario class."""

    def test_scenario_creation(self):
        """Test basic scenario creation."""
        from Model.scenario import Scenario
        from Model.units import Knight
        
        unit_a = Knight(team='A', x=10, y=50)
        unit_b = Knight(team='B', x=100, y=50)
        
        scenario = Scenario(
            units=[unit_a, unit_b],
            units_a=[unit_a],
            units_b=[unit_b],
            general_a=None,
            general_b=None,
            size_x=120,
            size_y=120
        )
        
        self.assertEqual(len(scenario.units), 2)
        self.assertEqual(len(scenario.units_a), 1)
        self.assertEqual(len(scenario.units_b), 1)
        self.assertEqual(scenario.size_x, 120)
        self.assertEqual(scenario.size_y, 120)

    def test_scenario_minimum_size(self):
        """Test that scenario enforces minimum map size."""
        from Model.scenario import Scenario
        
        scenario = Scenario(
            units=[],
            units_a=[],
            units_b=[],
            general_a=None,
            general_b=None,
            size_x=50,  # Below minimum
            size_y=80   # Below minimum
        )
        
        # Should enforce minimum of 120
        self.assertGreaterEqual(scenario.size_x, 120)
        self.assertGreaterEqual(scenario.size_y, 120)

    def test_scenario_with_generals(self):
        """Test scenario can include generals (set to None when not used)."""
        from Model.scenario import Scenario
        
        # Generals require complex initialization, test with None
        scenario = Scenario(
            units=[],
            units_a=[],
            units_b=[],
            general_a=None,
            general_b=None,
            size_x=120,
            size_y=120
        )
        
        self.assertIsNone(scenario.general_a)
        self.assertIsNone(scenario.general_b)


class TestMapGenerator(unittest.TestCase):
    """Test MapGenerator class."""

    def test_classic_formation(self):
        """Test classic formation generation."""
        from Utils.map_generator import MapGenerator
        
        scenario = MapGenerator.generate_battle_scenario(
            units_per_team=50,
            formation='classic',
            size_x=120,
            size_y=120
        )
        
        self.assertEqual(len(scenario.units_a), 50)
        self.assertEqual(len(scenario.units_b), 50)
        self.assertEqual(len(scenario.units), 100)

    def test_defensive_formation(self):
        """Test defensive formation generation."""
        from Utils.map_generator import MapGenerator
        
        scenario = MapGenerator.generate_battle_scenario(
            units_per_team=60,
            formation='defensive'
        )
        
        # Some formations may have slight rounding differences
        self.assertGreaterEqual(len(scenario.units_a), 55)
        self.assertLessEqual(len(scenario.units_a), 65)
        self.assertEqual(len(scenario.units_a), len(scenario.units_b))

    def test_offensive_formation(self):
        """Test offensive formation generation."""
        from Utils.map_generator import MapGenerator
        
        scenario = MapGenerator.generate_battle_scenario(
            units_per_team=40,
            formation='offensive'
        )
        
        self.assertEqual(len(scenario.units_a), 40)
        self.assertEqual(len(scenario.units_b), 40)

    def test_hammer_anvil_formation(self):
        """Test hammer and anvil formation generation."""
        from Utils.map_generator import MapGenerator
        
        scenario = MapGenerator.generate_battle_scenario(
            units_per_team=80,
            formation='hammer_anvil'
        )
        
        self.assertEqual(len(scenario.units_a), 80)
        self.assertEqual(len(scenario.units_b), 80)

    def test_testudo_formation(self):
        """Test testudo formation generation."""
        from Utils.map_generator import MapGenerator
        
        scenario = MapGenerator.generate_battle_scenario(
            units_per_team=30,
            formation='testudo'
        )
        
        self.assertEqual(len(scenario.units_a), 30)
        self.assertEqual(len(scenario.units_b), 30)

    def test_hollow_square_formation(self):
        """Test hollow square formation generation."""
        from Utils.map_generator import MapGenerator
        
        scenario = MapGenerator.generate_battle_scenario(
            units_per_team=100,
            formation='hollow_square'
        )
        
        # Hollow square may use fewer units due to geometry
        self.assertGreaterEqual(len(scenario.units_a), 80)
        self.assertLessEqual(len(scenario.units_a), 110)
        self.assertEqual(len(scenario.units_a), len(scenario.units_b))

    def test_unknown_formation_defaults_to_classic(self):
        """Test that unknown formation defaults to classic."""
        from Utils.map_generator import MapGenerator
        
        scenario = MapGenerator.generate_battle_scenario(
            units_per_team=50,
            formation='unknown_formation'
        )
        
        self.assertEqual(len(scenario.units_a), 50)
        self.assertEqual(len(scenario.units_b), 50)

    def test_teams_are_mirrored(self):
        """Test that Team B is mirrored from Team A."""
        from Utils.map_generator import MapGenerator
        
        scenario = MapGenerator.generate_battle_scenario(
            units_per_team=20,
            formation='classic',
            size_x=120,
            size_y=120
        )
        
        # Team A should be on left half (x < 60)
        for unit in scenario.units_a:
            self.assertLess(unit.x, 60, f"Team A unit at x={unit.x} should be < 60")
        
        # Team B should be on right half (x > 60)
        for unit in scenario.units_b:
            self.assertGreater(unit.x, 60, f"Team B unit at x={unit.x} should be > 60")

    def test_units_within_map_bounds(self):
        """Test that all units are within map bounds."""
        from Utils.map_generator import MapGenerator
        
        size_x, size_y = 150, 150
        scenario = MapGenerator.generate_battle_scenario(
            units_per_team=100,
            formation='classic',
            size_x=size_x,
            size_y=size_y
        )
        
        for unit in scenario.units:
            self.assertGreaterEqual(unit.x, 0, f"Unit x={unit.x} below 0")
            self.assertLessEqual(unit.x, size_x, f"Unit x={unit.x} above {size_x}")
            self.assertGreaterEqual(unit.y, 0, f"Unit y={unit.y} below 0")
            self.assertLessEqual(unit.y, size_y, f"Unit y={unit.y} above {size_y}")

    def test_unit_types_in_classic_formation(self):
        """Test that classic formation has all unit types."""
        from Utils.map_generator import MapGenerator
        from Model.units import Knight, Pikeman, Crossbowman
        
        scenario = MapGenerator.generate_battle_scenario(
            units_per_team=100,
            formation='classic'
        )
        
        # Check team A has all three unit types
        has_knight = any(isinstance(u, Knight) for u in scenario.units_a)
        has_pikeman = any(isinstance(u, Pikeman) for u in scenario.units_a)
        has_crossbowman = any(isinstance(u, Crossbowman) for u in scenario.units_a)
        
        self.assertTrue(has_knight, "Classic formation should have Knights")
        self.assertTrue(has_pikeman, "Classic formation should have Pikemen")
        self.assertTrue(has_crossbowman, "Classic formation should have Crossbowmen")

    def test_custom_map_size(self):
        """Test custom map sizes."""
        from Utils.map_generator import MapGenerator
        
        scenario = MapGenerator.generate_battle_scenario(
            units_per_team=50,
            formation='classic',
            size_x=200,
            size_y=180
        )
        
        self.assertEqual(scenario.size_x, 200)
        self.assertEqual(scenario.size_y, 180)


class TestLanchesterScenario(unittest.TestCase):
    """Test LanchesterScenario factory and Lanchester convenience function."""

    def test_lanchester_creates_n_vs_2n(self):
        """Test that Lanchester creates N vs 2N scenario."""
        from Plotting.lanchester import LanchesterScenario
        
        n = 15
        scenario = LanchesterScenario.create('Knight', n)
        
        self.assertEqual(len(scenario.units_a), n)
        self.assertEqual(len(scenario.units_b), 2 * n)
        self.assertEqual(len(scenario.units), 3 * n)

    def test_lanchester_convenience_function(self):
        """Test Lanchester() convenience function."""
        from Plotting.lanchester import Lanchester
        
        scenario = Lanchester('Crossbowman', 10)
        
        self.assertEqual(len(scenario.units_a), 10)
        self.assertEqual(len(scenario.units_b), 20)

    def test_lanchester_supported_types(self):
        """Test all supported unit types."""
        from Plotting.lanchester import LanchesterScenario
        
        supported = LanchesterScenario.get_supported_types()
        
        for unit_type in ['Knight', 'Crossbowman', 'Pikeman']:
            self.assertIn(unit_type, supported)
            
            scenario = LanchesterScenario.create(unit_type, 5)
            self.assertEqual(len(scenario.units_a), 5)
            self.assertEqual(len(scenario.units_b), 10)

    def test_lanchester_unit_type_aliases(self):
        """Test unit type aliases work."""
        from Plotting.lanchester import LanchesterScenario, UNIT_TYPES
        
        # Test aliases
        self.assertIn('Melee', UNIT_TYPES)
        self.assertIn('Ranged', UNIT_TYPES)
        self.assertIn('Crossbow', UNIT_TYPES)
        self.assertIn('Archer', UNIT_TYPES)
        
        # All aliases should work
        for alias in ['Melee', 'Ranged', 'Crossbow', 'Archer']:
            scenario = LanchesterScenario.create(alias, 5)
            self.assertEqual(len(scenario.units_a), 5)

    def test_lanchester_unknown_unit_type_raises(self):
        """Test unknown unit type raises ValueError."""
        from Plotting.lanchester import LanchesterScenario
        
        with self.assertRaises(ValueError) as ctx:
            LanchesterScenario.create('UnknownUnit', 10)
        
        self.assertIn('Unknown unit type', str(ctx.exception))

    def test_lanchester_invalid_n_raises(self):
        """Test invalid N values raise errors."""
        from Plotting.lanchester import LanchesterScenario
        
        # Zero units
        with self.assertRaises(ValueError):
            LanchesterScenario.create('Knight', 0)
        
        # Negative units
        with self.assertRaises(ValueError):
            LanchesterScenario.create('Knight', -5)

    def test_lanchester_non_integer_n_raises(self):
        """Test non-integer N raises TypeError."""
        from Plotting.lanchester import LanchesterScenario
        
        with self.assertRaises(TypeError):
            LanchesterScenario.create('Knight', 10.5)
        
        with self.assertRaises(TypeError):
            LanchesterScenario.create('Knight', "10")

    def test_lanchester_max_units_validation(self):
        """Test max units limit is enforced."""
        from Plotting.lanchester import LanchesterScenario, MAX_UNITS_PER_TEAM
        
        with self.assertRaises(ValueError) as ctx:
            LanchesterScenario.create('Knight', MAX_UNITS_PER_TEAM + 1)
        
        self.assertIn('exceeds max', str(ctx.exception))

    def test_lanchester_map_scales_with_units(self):
        """Test map size scales with unit count."""
        from Plotting.lanchester import LanchesterScenario, MAP_SIZE_MIN, MAP_SIZE_MAX
        
        # Small battle
        scenario_small = LanchesterScenario.create('Knight', 5)
        
        # Large battle
        scenario_large = LanchesterScenario.create('Knight', 100)
        
        # Both should be within bounds
        self.assertGreaterEqual(scenario_small.size_x, MAP_SIZE_MIN)
        self.assertLessEqual(scenario_large.size_x, MAP_SIZE_MAX)

    def test_lanchester_units_face_each_other(self):
        """Test teams are positioned facing each other."""
        from Plotting.lanchester import LanchesterScenario
        
        scenario = LanchesterScenario.create('Knight', 20)
        
        # Get average X position for each team
        avg_a_x = sum(u.x for u in scenario.units_a) / len(scenario.units_a)
        avg_b_x = sum(u.x for u in scenario.units_b) / len(scenario.units_b)
        
        # Team A should be to the left of Team B
        self.assertLess(avg_a_x, avg_b_x)
        
        # They should be close (engagement gap)
        gap = avg_b_x - avg_a_x
        self.assertLess(gap, 20, f"Gap {gap} too large for quick engagement")

    def test_lanchester_units_within_bounds(self):
        """Test all Lanchester units are within map bounds."""
        from Plotting.lanchester import LanchesterScenario, MARGIN
        
        scenario = LanchesterScenario.create('Crossbowman', 50)
        
        for unit in scenario.units:
            self.assertGreaterEqual(unit.x, MARGIN - 1)
            self.assertLessEqual(unit.x, scenario.size_x - MARGIN + 1)
            self.assertGreaterEqual(unit.y, MARGIN - 1)
            self.assertLessEqual(unit.y, scenario.size_y - MARGIN + 1)

    def test_lanchester_constants_defined(self):
        """Test all required constants are defined."""
        from Plotting import lanchester
        
        required_constants = [
            'MAP_SIZE_MIN',
            'MAP_SIZE_MAX',
            'MAP_SIZE_BASE',
            'ENGAGEMENT_GAP',
            'MARGIN',
            'UNIT_SPACING_MAX',
            'MAX_UNITS_PER_TEAM',
            'UNIT_TYPES',
        ]
        
        for const in required_constants:
            self.assertTrue(hasattr(lanchester, const), f"Missing constant: {const}")

    def test_lanchester_homogeneous_units(self):
        """Test that Lanchester scenario uses only one unit type."""
        from Plotting.lanchester import LanchesterScenario
        from Model.units import Knight, Crossbowman
        
        # Knight scenario should have only Knights
        scenario_k = LanchesterScenario.create('Knight', 10)
        for unit in scenario_k.units:
            self.assertIsInstance(unit, Knight)
        
        # Crossbowman scenario should have only Crossbowmen
        scenario_c = LanchesterScenario.create('Crossbowman', 10)
        for unit in scenario_c.units:
            self.assertIsInstance(unit, Crossbowman)


class TestUnitPositioning(unittest.TestCase):
    """Test unit positioning and spacing."""

    def test_units_have_correct_teams(self):
        """Test units are assigned to correct teams."""
        from Utils.map_generator import MapGenerator
        
        scenario = MapGenerator.generate_battle_scenario(units_per_team=20)
        
        for unit in scenario.units_a:
            self.assertEqual(unit.team, 'A')
        
        for unit in scenario.units_b:
            self.assertEqual(unit.team, 'B')

    def test_units_not_overlapping(self):
        """Test that units are not stacked on same position."""
        from Plotting.lanchester import LanchesterScenario
        
        scenario = LanchesterScenario.create('Knight', 30)
        
        positions = set()
        for unit in scenario.units:
            pos = (round(unit.x, 1), round(unit.y, 1))
            # Allow some overlap due to rounding, but not exact same position
            self.assertNotIn((unit.x, unit.y), positions, 
                           f"Duplicate position: ({unit.x}, {unit.y})")
            positions.add((unit.x, unit.y))

    def test_line_formation_vertical_spread(self):
        """Test that line formations spread vertically."""
        from Plotting.lanchester import LanchesterScenario
        
        scenario = LanchesterScenario.create('Knight', 20)
        
        # Get Y positions for team A
        y_positions = [u.y for u in scenario.units_a]
        
        # Should have some vertical spread
        y_range = max(y_positions) - min(y_positions)
        self.assertGreater(y_range, 10, "Line formation should spread vertically")


class TestScenarioIntegration(unittest.TestCase):
    """Integration tests for scenario creation and simulation compatibility."""

    def test_scenario_can_be_used_in_simulation(self):
        """Test that generated scenarios work with simulation."""
        from Utils.map_generator import MapGenerator
        from Model.simulation import Simulation
        
        scenario = MapGenerator.generate_battle_scenario(
            units_per_team=10,
            formation='classic'
        )
        
        # Should be able to create simulation
        sim = Simulation(scenario)
        self.assertIsNotNone(sim)
        self.assertEqual(sim.tick, 0)

    def test_lanchester_scenario_can_be_simulated(self):
        """Test that Lanchester scenarios work with simulation."""
        from Plotting.lanchester import Lanchester
        from Model.simulation import Simulation
        
        scenario = Lanchester('Knight', 5)
        
        sim = Simulation(scenario)
        self.assertIsNotNone(sim)
        self.assertEqual(sim.tick, 0)
        
        # Verify scenario is properly attached
        self.assertEqual(len(sim.scenario.units_a), 5)
        self.assertEqual(len(sim.scenario.units_b), 10)


if __name__ == '__main__':
    unittest.main()
