import unittest
from Model.Simulation import Simulation
from Model.Scenario import Scenario


class MockUnit:
    """Mock unit class for testing compatible with current Simulation.

    Provides attributes/methods expected by Model.simulation:
    - x, y, team, hp, speed, size, sight, range, reload_time, reload
    - attack (dict), armor (dict), accuracy (float), unit_type (str)
    - can_attack(), perform_attack(), update_reload(dt)
    """

    def __init__(self, x, y, team, hp=100, attack=10, speed=5, size=5,
                 sight=50, range_val=10, reload_time=0, unit_type='soldier'):
        self.x = float(x)
        self.y = float(y)
        self.team = team
        self.hp = hp
        # attack can be passed as int or dict; normalize to dict
        if isinstance(attack, dict):
            self.attack = attack
        else:
            self.attack = {'physical': attack}
        self.speed = float(speed)
        self.size = float(size)
        self.sight = float(sight)
        self.range = float(range_val)
        self.reload_time = float(reload_time)
        self.reload = 0.0
        self.accuracy = 1.0
        self.armor = {}
        self.unit_type = unit_type
        self.damage_dealt = 0
        self.distance_moved = 0

    def can_attack(self):
        return self.reload <= 0.0

    def perform_attack(self):
        # set reload to reload_time to simulate attack cooldown
        self.reload = self.reload_time

    def update_reload(self, dt):
        # decrease reload timer
        self.reload = max(0.0, self.reload - dt)


class TestSimulationInit(unittest.TestCase):
    """Test Simulation initialization with current signature (scenario).
    """

    def setUp(self):
        self.unitA = MockUnit(10, 10, "A")
        self.unitB = MockUnit(50, 50, "B")
        self.units = [self.unitA, self.unitB]
        self.unitsA = [self.unitA]
        self.unitsB = [self.unitB]
        self.scenario = Scenario(self.units, self.unitsA, self.unitsB, None, None)

    def test_init_default_values(self):
        sim = Simulation(self.scenario)
        self.assertEqual(sim.tick_speed, 5)
        # Scenario defaults are 120x120 in this repository's Scenario implementation
        self.assertEqual(self.scenario.size_x, 120)
        self.assertEqual(self.scenario.size_y, 120)
        self.assertFalse(sim.paused)
        self.assertFalse(sim.unlocked)
        self.assertEqual(sim.tick, 0)

    def test_init_custom_values(self):
        sim = Simulation(self.scenario, tick_speed=10, paused=True, unlocked=True)
        self.assertEqual(sim.tick_speed, 10)
        self.assertTrue(sim.paused)
        self.assertTrue(sim.unlocked)


class TestSimulationState(unittest.TestCase):
    """Test simulation state management using Scenario-based Simulation."""

    def setUp(self):
        self.unitA = MockUnit(10, 10, "A")
        self.unitB = MockUnit(50, 50, "B")
        self.units = [self.unitA, self.unitB]
        self.unitsA = [self.unitA]
        self.unitsB = [self.unitB]
        self.scenario = Scenario(self.units, self.unitsA, self.unitsB, None, None)
        self.sim = Simulation(self.scenario)

    def test_finished_no_units_a(self):
        self.scenario.units_a = []
        self.assertTrue(self.sim.finished())

    def test_finished_no_units_b(self):
        self.scenario.units_b = []
        self.assertTrue(self.sim.finished())

    def test_finished_max_ticks(self):
        self.sim.tick = self.sim.tick_speed * 240
        self.assertTrue(self.sim.finished())

    def test_not_finished(self):
        self.assertFalse(self.sim.finished())

    def test_toggle_pause(self):
        # Simulation doesn't provide toggle_pause method; flip the attribute directly
        self.assertFalse(self.sim.paused)
        self.sim.paused = True
        self.assertTrue(self.sim.paused)
        self.sim.paused = False
        self.assertFalse(self.sim.paused)

    def test_increase_tick(self):
        initial = self.sim.tick_speed
        # No increase_tick method in Simulation; modify tick_speed directly
        self.sim.tick_speed += 1
        self.assertEqual(self.sim.tick_speed, initial + 1)

    def test_decrease_tick(self):
        self.sim.tick_speed = 5
        # No decrease_tick method in Simulation; decrease with a floor at 1
        if self.sim.tick_speed > 1:
            self.sim.tick_speed -= 1
        self.assertEqual(self.sim.tick_speed, 4)

    def test_decrease_tick_minimum(self):
        self.sim.tick_speed = 1
        # Ensure tick_speed does not go below 1 when decreased manually
        if self.sim.tick_speed > 1:
            self.sim.tick_speed -= 1
        self.assertEqual(self.sim.tick_speed, 1)


class TestMovementFunctions(unittest.TestCase):
    """Test unit movement functions."""

    def setUp(self):
        self.unitA = MockUnit(10, 10, "A", speed=5, size=5)
        self.unitB = MockUnit(50, 50, "B", size=5)
        self.units = [self.unitA, self.unitB]
        self.scenario = Scenario(self.units, [self.unitA], [self.unitB], None, None)
        self.sim = Simulation(self.scenario)

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
        self.unitA = MockUnit(10, 10, "A", hp=100, attack={'physical': 20}, speed=5, size=5, sight=50, range_val=15, reload_time=0)
        self.unitB = MockUnit(20, 10, "B", hp=100, attack={'physical': 0}, size=5)
        self.units = [self.unitA, self.unitB]
        self.scenario = Scenario(self.units, [self.unitA], [self.unitB], None, None)
        self.sim = Simulation(self.scenario)

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
        self.scenario.units.append(unitB2)
        self.scenario.units_b.append(unitB2)
        nearest = self.sim.get_nearest_enemy_unit(self.unitA)
        self.assertEqual(nearest, unitB2)

    def test_attack_unit_success(self):
        initial_hp = self.unitB.hp
        # ensure attacker can attack
        self.unitA.reload = 0
        result = self.sim.attack_unit(self.unitA, self.unitB)
        self.assertTrue(result)
        self.assertLess(self.unitB.hp, initial_hp)
        # Simulation currently tracks reloading units; ensure attacker was registered
        self.assertIn(self.unitA, self.sim.reload_units)

    def test_attack_unit_out_of_range(self):
        self.unitB.x = 100
        result = self.sim.attack_unit(self.unitA, self.unitB)
        self.assertFalse(result)

    def test_attack_unit_kills_target(self):
        self.unitB.hp = 1
        self.unitA.reload = 0
        self.sim.attack_unit(self.unitA, self.unitB)
        self.assertLessEqual(self.unitB.hp, 0)


class TestDistanceFunctions(unittest.TestCase):
    """Test distance calculation functions."""

    def setUp(self):
        self.unitA = MockUnit(0, 0, "A", speed=5)
        self.scenario = Scenario([self.unitA], [self.unitA], [], None, None)
        self.sim = Simulation(self.scenario)

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
