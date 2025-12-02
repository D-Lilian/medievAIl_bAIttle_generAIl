import unittest
from Model.simulation import Simulation


class MockUnit:
    """Mock unit class for testing."""

    def __init__(self, x, y, team, hp=100, attack=10, speed=5, size=5,
                 sight=50, range_val=10, reload_time=5):
        self.x = x
        self.y = y
        self.team = team
        self.hp = hp
        self.attack = attack
        self.speed = speed
        self.size = size
        self.sight = sight
        self.range = range_val
        self.reload = 0
        self.reload_time = reload_time


class TestSimulationInit(unittest.TestCase):
    """Test Simulation initialization."""

    def setUp(self):
        self.unitA = MockUnit(10, 10, "A")
        self.unitB = MockUnit(50, 50, "B")
        self.units = [self.unitA, self.unitB]
        self.unitsA = [self.unitA]
        self.unitsB = [self.unitB]

    def test_init_default_values(self):
        sim = Simulation(self.units, self.unitsA, None, self.unitsB, None)
        self.assertEqual(sim.tick_speed, 5)
        self.assertEqual(sim.size_x, 200)
        self.assertEqual(sim.size_y, 200)
        self.assertFalse(sim.paused)
        self.assertFalse(sim.unlocked)
        self.assertEqual(sim.tick, 0)

    def test_init_custom_values(self):
        sim = Simulation(self.units, self.unitsA, None, self.unitsB, None,
                         tick_speed=10, size_x=300, size_y=400, paused=True, unlocked=True)
        self.assertEqual(sim.tick_speed, 10)
        self.assertEqual(sim.size_x, 300)
        self.assertEqual(sim.size_y, 400)
        self.assertTrue(sim.paused)
        self.assertTrue(sim.unlocked)


class TestSimulationState(unittest.TestCase):
    """Test simulation state management."""

    def setUp(self):
        self.unitA = MockUnit(10, 10, "A")
        self.unitB = MockUnit(50, 50, "B")
        self.units = [self.unitA, self.unitB]
        self.unitsA = [self.unitA]
        self.unitsB = [self.unitB]
        self.sim = Simulation(self.units, self.unitsA, None, self.unitsB, None)

    def test_finished_no_units_a(self):
        self.sim.units_a = []
        self.assertTrue(self.sim.finished())

    def test_finished_no_units_b(self):
        self.sim.units_b = []
        self.assertTrue(self.sim.finished())

    def test_finished_max_ticks(self):
        self.sim.tick = self.sim.tick_speed * 240
        self.assertTrue(self.sim.finished())

    def test_not_finished(self):
        self.assertFalse(self.sim.finished())

    def test_toggle_pause(self):
        self.assertFalse(self.sim.paused)
        self.sim.toggle_pause()
        self.assertTrue(self.sim.paused)
        self.sim.toggle_pause()
        self.assertFalse(self.sim.paused)

    def test_increase_tick(self):
        initial = self.sim.tick_speed
        self.sim.increase_tick()
        self.assertEqual(self.sim.tick_speed, initial + 1)

    def test_decrease_tick(self):
        self.sim.tick_speed = 5
        self.sim.decrease_tick()
        self.assertEqual(self.sim.tick_speed, 4)

    def test_decrease_tick_minimum(self):
        self.sim.tick_speed = 1
        self.sim.decrease_tick()
        self.assertEqual(self.sim.tick_speed, 1)


class TestMovementFunctions(unittest.TestCase):
    """Test unit movement functions."""

    def setUp(self):
        self.unitA = MockUnit(10, 10, "A", speed=5, size=5)
        self.unitB = MockUnit(50, 50, "B", size=5)
        self.units = [self.unitA, self.unitB]
        self.sim = Simulation(self.units, [self.unitA], None, [self.unitB], None)

    def test_move_unit_towards_coordinates(self):
        self.sim.move_unit_towards_coordinates(self.unitA, 20, 20)
        self.assertGreater(self.unitA.x, 10)
        self.assertGreater(self.unitA.y, 10)
        self.assertTrue(self.sim.as_unit_moved)

    def test_move_unit_towards_unit(self):
        initial_x = self.unitA.x
        initial_y = self.unitA.y
        self.sim.move_unit_towards_unit(self.unitA, self.unitB)
        self.assertGreater(self.unitA.x, initial_x)
        self.assertGreater(self.unitA.y, initial_y)

    def test_move_respects_max_speed(self):
        initial_x = self.unitA.x
        self.unitA.speed = 3
        self.sim.move_unit_towards_coordinates(self.unitA, 100, 10)
        distance_moved = abs(self.unitA.x - initial_x)
        self.assertLessEqual(distance_moved, 3.01)

    def test_move_clamped_to_bounds(self):
        self.sim.move_unit_towards_coordinates(self.unitA, -10, -10)
        self.assertGreaterEqual(self.unitA.x, 0)
        self.assertGreaterEqual(self.unitA.y, 0)

        self.unitA.x = 190
        self.unitA.y = 190
        self.sim.move_unit_towards_coordinates(self.unitA, 300, 300)
        self.assertLessEqual(self.unitA.x, self.sim.size_x)
        self.assertLessEqual(self.unitA.y, self.sim.size_y)

    def test_move_collision_detection(self):
        self.unitA.x = 20
        self.unitA.y = 20
        self.unitB.x = 25
        self.unitB.y = 20
        initial_distance = self.sim.distance_between_coordinates(
            self.unitA.x, self.unitA.y, self.unitB.x, self.unitB.y
        )
        self.sim.move_unit_towards_coordinates(self.unitA, 25, 20)
        final_distance = self.sim.distance_between_coordinates(
            self.unitA.x, self.unitA.y, self.unitB.x, self.unitB.y
        )
        min_distance = self.unitA.size + self.unitB.size
        self.assertGreaterEqual(final_distance, min_distance - 0.01)

    def test_move_one_step_from_target_in_direction(self):
        self.unitA.x = 50
        self.unitA.y = 50
        self.unitB.x = 60
        self.unitB.y = 50
        initial_y = self.unitA.y
        self.sim.move_one_step_from_target_in_direction(self.unitA, self.unitB, 90)
        self.assertGreater(self.unitA.y, initial_y)


class TestCombatFunctions(unittest.TestCase):
    """Test combat-related functions."""

    def setUp(self):
        self.unitA = MockUnit(10, 10, "A", hp=100, attack=20, range_val=15, sight=50, size=5)
        self.unitB = MockUnit(20, 10, "B", hp=100, size=5)
        self.units = [self.unitA, self.unitB]
        self.sim = Simulation(self.units, [self.unitA], None, [self.unitB], None)

    def test_is_in_sight_true(self):
        self.assertTrue(self.sim.is_in_sight(self.unitA, self.unitB))

    def test_is_in_sight_false(self):
        self.unitB.x = 200
        self.unitB.y = 200
        self.assertFalse(self.sim.is_in_sight(self.unitA, self.unitB))

    def test_is_in_reach_true(self):
        self.assertTrue(self.sim.is_in_reach(self.unitA, self.unitB))

    def test_is_in_reach_false(self):
        self.unitB.x = 100
        self.assertFalse(self.sim.is_in_reach(self.unitA, self.unitB))

    def test_get_nearest_enemy_unit(self):
        unitB2 = MockUnit(15, 15, "B")
        self.sim.units.append(unitB2)
        self.sim.units_b.append(unitB2)
        nearest = self.sim.get_nearest_enemy_unit(self.unitA)
        self.assertEqual(nearest, unitB2)

    def test_attack_unit_success(self):
        initial_hp = self.unitB.hp
        result = self.sim.attack_unit(self.unitA, self.unitB)
        self.assertTrue(result)
        self.assertEqual(self.unitB.hp, initial_hp - self.unitA.attack)
        self.assertTrue(self.sim.as_unit_attacked)

    def test_attack_unit_out_of_range(self):
        self.unitB.x = 100
        result = self.sim.attack_unit(self.unitA, self.unitB)
        self.assertFalse(result)

    def test_attack_unit_kills_target(self):
        self.unitB.hp = 10
        self.sim.attack_unit(self.unitA, self.unitB)
        self.assertNotIn(self.unitB, self.sim.units)
        self.assertNotIn(self.unitB, self.sim.units_b)


class TestDistanceFunctions(unittest.TestCase):
    """Test distance calculation functions."""

    def setUp(self):
        self.unitA = MockUnit(0, 0, "A", speed=5)
        self.sim = Simulation([self.unitA], [self.unitA], None, [], None)

    def test_distance_between_coordinates(self):
        distance = self.sim.distance_between_coordinates(0, 0, 3, 4)
        self.assertEqual(distance, 5.0)

    def test_distance_zero(self):
        distance = self.sim.distance_between_coordinates(10, 10, 10, 10)
        self.assertEqual(distance, 0.0)

    def test_compare_position_exact(self):
        self.unitA.x = 10
        self.unitA.y = 20
        self.assertTrue(self.sim.compare_position(self.unitA, 10, 20))

    def test_compare_position_within_tolerance(self):
        self.unitA.x = 10
        self.unitA.y = 20
        self.unitA.speed = 5
        self.assertTrue(self.sim.compare_position(self.unitA, 12, 21))

    def test_compare_position_outside_tolerance(self):
        self.unitA.x = 10
        self.unitA.y = 20
        self.unitA.speed = 1
        self.assertFalse(self.sim.compare_position(self.unitA, 15, 25))


if __name__ == '__main__':
    unittest.main()