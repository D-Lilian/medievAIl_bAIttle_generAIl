import time
import random
import math

from Model.Units  import Knight

class Simulation:

    def __init__(self, units, unitsA, generalA, unitsB, generalB, tickSpeed = 5,size_x = 200, size_y = 200, paused = False, unlocked = False):
        self.size_x = size_x
        self.size_y = size_y

        self.units = units

        self.unitsA = unitsA
        self.generalA = generalA

        self.unitsB = unitsB
        self.generalB = generalB

        self.tickSpeed = tickSpeed
        self.tick = 0
        self.paused = paused
        self.unlocked = unlocked

        self.asUnitMoved = False
        self.asUnitAttacked = False


    ## ----------- Simulation functions -------------

    def simulate(self):
        while not self.finished():
            random.shuffle(self.units)

            for unit in self.units:
                enemy = self.get_nearest_enemy_unit(unit)
                if enemy is None:
                    continue
                if self.is_in_reach(unit, enemy) and unit.reload <= 0:
                    self.attack_unit(unit, enemy)
                    unit.reload = unit.reload_time
                else:
                    self.move_unit_towards_coordinates(unit, enemy.x, enemy.y)
            self.tick += 1
            print(self.tick)

            if self.tick % 5 == 0:
                for unit in self.units:
                    self.reload_unit(unit)

            if self.paused:
                while self.paused:
                    time.sleep(0.1)
            elif not self.unlocked:
                time.sleep(1/self.tickSpeed)

    def finished(self):
        """Check if the simulation has finished."""
        if not self.unitsA or not self.unitsB:
            print("Ticks : ", self.tick, "Team A units left:", len(self.unitsA), "  | Team B units left:", len(self.unitsB))
            return True
        return self.tick >= self.tickSpeed * 240

    def toggle_pause(self):
        self.paused = not self.paused

    def increase_tick(self):
        self.tickSpeed += 1

    def decrease_tick(self):
        if self.tickSpeed > 1:
            self.tickSpeed -= 1

    ## ----------- Movement functions -------------

    def move_unit_towards_unit(self, unit, target):
        """Move a unit towards target unit, up to its max distance."""
        return self.move_unit_towards_coordinates(unit, target.x, target.y)


    def move_one_step_from_target_in_direction(self, unit, target, direction):
        """Move a unit one step in the given direction angle (0-360) relative to the unit in facing the target."""
        if unit in self.units and target in self.units:
            angle_to_target = math.atan2(target.y - unit.y, target.x - unit.x)
            move_angle = angle_to_target + math.radians(direction)

            move_x = math.cos(move_angle) * unit.speed
            move_y = math.sin(move_angle) * unit.speed

            return self.move_unit_towards_coordinates(unit, unit.x + move_x, unit.y + move_y)
        return None


    def move_unit_towards_coordinates(self, unit, target_x, target_y):
        """Move a unit towards target coordinates, up to its max distance."""
        if unit in self.units:
            distance_to_target = self.distance_between_coordinates(target_x, target_y, unit.x, unit.y)
            dx = target_x - unit.x
            dy = target_y - unit.y

            if distance_to_target > 0:
                move_distance = min(unit.speed, distance_to_target)

                move_x = (dx / distance_to_target) * move_distance
                move_y = (dy / distance_to_target) * move_distance

                new_x = unit.x + move_x
                new_y = unit.y + move_y

                collision_occurred = False
                for other in self.units:
                    if other is not unit:

                        dist = self.distance_between_coordinates(new_x, new_y, other.x, other.y)
                        min_distance = unit.size + other.size

                        if dist < min_distance:
                            collision_occurred = True

                            if dist > 0:
                                ux = (new_x - other.x) / dist
                                uy = (new_y - other.y) / dist
                                final_x = other.x + ux * min_distance
                                final_y = other.y + uy * min_distance
                            else:
                                angle = random.random() * 2 * math.pi
                                final_x = other.x + math.cos(angle) * min_distance
                                final_y = other.y + math.sin(angle) * min_distance
                            break

                if not collision_occurred:
                    final_x = new_x
                    final_y = new_y

                final_x = max(0, min(final_x, self.size_x))
                final_y = max(0, min(final_y, self.size_y))

                unit.x = final_x
                unit.y = final_y

                self.asUnitMoved = True
        return False

    ## ----------- Combat functions -------------

    def is_in_sight(self, attacker, target):
        """Check if target is within sight of the attacker."""
        if attacker in self.units and target in self.units:
            center_distance = self.distance_between_coordinates(attacker.x, attacker.y, target.x, target.y)
            surface_distance = center_distance - (attacker.size + target.size)

            return surface_distance <= attacker.sight
        return False

    def is_in_reach(self, attacker, target):
        """Check if target is within range of the attacker."""
        if attacker in self.units and target in self.units:
            center_distance = self.distance_between_coordinates(attacker.x, attacker.y, target.x, target.y)
            surface_distance = center_distance - (attacker.size + target.size)

            return surface_distance <= attacker.range
        return False

    def get_nearest_enemy_unit(self, unit):
        """Return the nearest enemy unit of the given unit."""
        enemy_units = self.unitsB if unit.team == "A" else self.unitsA
        nearest_unit = None
        nearest_distance = float('inf')
        for enemy in enemy_units:
            distance = self.distance_between_coordinates(unit.x, unit.y, enemy.x, enemy.y)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_unit = enemy
        return nearest_unit

    def get_nearest_troops_in_sight(self, unit):
        """Return the nearest enemies units in sight of the given unit."""
        ennemies_units = self.unitsB if unit.team == "A" else self.unitsA
        nearest_unit = []
        for ennemy in ennemies_units:
            if self.is_in_sight(unit, ennemy):
                nearest_unit.append(ennemy)
        return nearest_unit

    def attack_unit(self, attacker, target):
        """Attack a target point if within range. Returns True if attack succeeded."""
        if self.is_in_reach(attacker, target):
            target.hp -= attacker.attack
            self.asUnitAttacked = True
            if target.hp <= 0:
                self.units.remove(target)
                if target.team == "A":
                    self.unitsA.remove(target)
                else:
                    self.unitsB.remove(target)
            return True
        return False

    def reload_unit(self, unit):
        """Reload the unit's weapon."""
        if unit.reload <= 1:
            unit.reload = 0
        else:
            unit.reload -= 1

    ## ----------- Distance functions -------------

    def distance_between_coordinates(self, unit_x, unit_y, other_unit_x, other_unit_y):
        return ((unit_x - other_unit_x) ** 2 + (unit_y - other_unit_y) ** 2) ** 0.5

    def compare_position(self, unit, x, y):
        return math.isclose(unit.x, x, abs_tol=unit.speed) and math.isclose(unit.y, y, abs_tol=unit.speed)


# Example usage
if __name__ == "__main__":

    unitsA = []
    unitsB = []
    units = []
    for i in range (0, 100):
        temp = Knight("A", 20 + i % 20, 10 + i % 5)
        unitsA.append(temp)
        units.append(temp)

        temp = Knight("B", 20 + i % 20, 50 + i % 5)
        unitsB.append(temp)
        units.append(temp)


    start_time = time.perf_counter()

    sim = Simulation(
        units,
        unitsA,
        None,
        unitsB,
        None,
        tickSpeed = 5,
        unlocked = True
    )

    sim.simulate()
    end_time = time.perf_counter()
    print(f"\nMain execution time: {end_time - start_time:.6f} seconds")