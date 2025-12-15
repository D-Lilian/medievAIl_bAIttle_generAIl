# -*- coding: utf-8 -*-
"""
@file simulation.py
@brief Simulation Model - Core logic of the battle simulation

@details
Manages the game loop, unit updates, and interaction between units.
Handles time progression and game state.

"""
import time
import random
import math

from Model.units import *

# Number chosen to make simulation fast but realistic
# So that reload time and tick speed are compatible
DEFAULT_NUMBER_OF_TICKS_PER_SECOND = 5

class Simulation:

    def __init__(self, scenario, tick_speed = 5, paused = False, unlocked = False):
        self.scenario = scenario
        self.reload_units = []

        self.tick_speed = tick_speed
        self.tick = 0
        self.paused = paused
        self.unlocked = unlocked

        self.as_unit_moved = False
        self.as_unit_attacked = False

        self.types_present = self.type_present_in_team()

    ## ----------- Simulation functions -------------

    def simulate(self, on_end=None):
        """Run the simulation until a team wins or time runs out."""
        self.scenario.general_a.BeginStrategy()
        self.scenario.general_b.BeginStrategy()
        self.scenario.general_a.CreateOrders()
        self.scenario.general_b.CreateOrders()

        while not self.finished():
            random.shuffle(self.scenario.units)

            for unit in self.scenario.units:
                if not self.is_unit_still_alive(unit):
                    continue

                for unit_order in unit.order_manager:
                    if unit_order.Try(self):
                        unit_order.Remove(unit_order)
                self.as_unit_attacked = False
                self.as_unit_moved = False
            self.tick += 1

            for unit in list(self.reload_units):
                unit.update_reload(1 / DEFAULT_NUMBER_OF_TICKS_PER_SECOND)
                if unit.can_attack():
                    try:
                        self.reload_units.remove(unit)
                    except ValueError:
                        pass

            if self.tick % DEFAULT_NUMBER_OF_TICKS_PER_SECOND == 0:
                types = self.type_present_in_team()
                for types_present in types.get("A"):
                    if types_present not in self.types_present.get("A"):
                        self.scenario.general_a.notify(types_present)
                for types_present in types.get("B"):
                    if types_present not in self.types_present.get("B"):
                        self.scenario.general_b.HandleUnitTypeDepleted(types_present)
                self.types_present = types

                self.scenario.general_a.CreateOrders()
                self.scenario.general_b.CreateOrders()

            if self.paused:
                while self.paused:
                    time.sleep(0.1)
            elif not self.unlocked:
                time.sleep(1 / self.tick_speed)

        # Simulation ended, return results
        # Can be expanded to return more detailed results in the future
        output = {
            'ticks': self.tick
        }
        if callable(on_end):
            on_end(output)
        return output

    def finished(self):
        """Check if the simulation has finished."""
        count_a = 0
        count_b = 0

        for unit in self.scenario.units_a:
            if self.is_unit_still_alive(unit):
                count_a += 1
        for unit in self.scenario.units_b:
            if self.is_unit_still_alive(unit):
                count_b += 1

        if count_a == 0 or count_b == 0:
            print("Ticks : ", self.tick, "Team A units left:", count_a, "  | Team B units left:", count_b)
            return True

        return self.tick >= self.tick_speed * 120

    ## ----------- Movement functions -------------

    def move_unit_towards_unit(self, attacker_unit, target_unit):
        """Move a unit towards target unit, up to its max distance."""
        return self.move_unit_towards_coordinates(attacker_unit, target_unit.x, target_unit.y)

    def move_one_step_from_target_in_direction(self, attacker_unit, target_unit, direction):
        """Move a unit one step in the given direction angle (0-360) relative to the unit in facing the target."""
        if attacker_unit in self.scenario.units and target_unit in self.scenario.units:
            angle_to_target = math.atan2(target_unit.y - attacker_unit.y, target_unit.x - attacker_unit.x)
            move_angle = angle_to_target + math.radians(direction)

            move_x = math.cos(move_angle) * attacker_unit.speed
            move_y = math.sin(move_angle) * attacker_unit.speed

            return self.move_unit_towards_coordinates(attacker_unit, attacker_unit.x + move_x, attacker_unit.y + move_y)
        return None

    def move_unit_towards_coordinates(self, attacker_unit, target_x, target_y):
        """Move a unit towards target coordinates, up to its max distance."""
        if attacker_unit in self.scenario.units and self.is_unit_still_alive(attacker_unit) and not self.as_unit_moved:

            final_x = attacker_unit.x
            final_y = attacker_unit.y

            distance_to_target = self.distance_between_coordinates(target_x, target_y, attacker_unit.x, attacker_unit.y)
            dx = target_x - attacker_unit.x
            dy = target_y - attacker_unit.y

            if distance_to_target > 0:
                move_distance = min(attacker_unit.speed, distance_to_target)

                move_x = (dx / distance_to_target) * move_distance
                move_y = (dy / distance_to_target) * move_distance

                new_x = attacker_unit.x + move_x
                new_y = attacker_unit.y + move_y

                collision_occurred = False
                for other in self.scenario.units:
                    if other is not attacker_unit and self.is_unit_still_alive(other):

                        dist = self.distance_between_coordinates(new_x, new_y, other.x, other.y)
                        min_distance = attacker_unit.size + other.size

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

                final_x = max(0, min(final_x, self.scenario.size_x))
                final_y = max(0, min(final_y, self.scenario.size_y))

                attacker_unit.x = final_x
                attacker_unit.y = final_y

                self.as_unit_moved = True
                attacker_unit.distance_moved += move_distance
                return True
        return False

    ## ----------- Combat functions -------------

    def is_in_sight(self, attacker_unit, target_unit):
        """Check if target is within sight of the attacker."""
        if attacker_unit in self.scenario.units and target_unit in self.scenario.units and self.is_unit_still_alive(attacker_unit) and self.is_unit_still_alive(target_unit):
            center_distance = self.distance_between_coordinates(attacker_unit.x, attacker_unit.y, target_unit.x, target_unit.y)
            surface_distance = center_distance - (attacker_unit.size + target_unit.size)

            return surface_distance <= attacker_unit.sight
        return False

    def is_in_reach(self, attacker_unit, target_unit):
        """Check if target is within range of the attacker."""
        if attacker_unit in self.scenario.units and target_unit in self.scenario.units and self.is_unit_still_alive(attacker_unit) and self.is_unit_still_alive(target_unit):
            center_distance = self.distance_between_coordinates(attacker_unit.x, attacker_unit.y, target_unit.x, target_unit.y)
            surface_distance = center_distance - (attacker_unit.size + target_unit.size)

            return surface_distance <= attacker_unit.range
        return False

    def get_nearest_enemy_unit(self, unit, type_target=UnitType.ALL):
        """Return the nearest enemy unit of the given unit."""
        if type_target == UnitType.NONE:
            return None

        enemy_units = self.scenario.units_b if unit.team == "A" else self.scenario.units_a
        nearest_unit = None
        nearest_distance = float('inf')
        for enemy in enemy_units:
            if not self.is_unit_still_alive(enemy) or (type_target is not UnitType.ALL and enemy.unit_type != type_target):
                continue
            distance = self.distance_between_coordinates(unit.x, unit.y, enemy.x, enemy.y)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_unit = enemy
        return nearest_unit

    def get_nearest_enemy_in_sight(self, unit, type_target=UnitType.ALL):
        """Return the nearest enemy unit in sight of the given unit."""
        if type_target == UnitType.NONE:
            return None

        enemy_units = self.scenario.units_b if unit.team == "A" else self.scenario.units_a
        nearest_unit = None
        nearest_distance = float('inf')
        for target_unit in enemy_units:
            if (type_target is not UnitType.ALL and target_unit.unit_type != type_target) or not self.is_unit_still_alive(target_unit):
                continue
            if self.is_in_sight(unit, target_unit):
                distance = self.distance_between_coordinates(unit.x, unit.y, target_unit.x, target_unit.y)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_unit = target_unit
        return nearest_unit

    def get_nearest_enemy_in_reach(self, unit, type_target=UnitType.ALL):
        """Return the nearest enemy unit in reach of the given unit."""
        if not self.is_unit_still_alive(unit) or type_target == UnitType.NONE:
            return None
        enemy_units = self.scenario.units_b if unit.team == "A" else self.scenario.units_a
        nearest_unit = None
        nearest_distance = float('inf')
        for target_unit in enemy_units:
            if (type_target is not UnitType.ALL and target_unit.unit_type != type_target) or not self.is_unit_still_alive(target_unit):
                continue
            if self.is_in_reach(unit, target_unit):
                distance = self.distance_between_coordinates(unit.x, unit.y, target_unit.x, target_unit.y)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_unit = target_unit
        return nearest_unit

    def get_nearest_friendly_in_sight(self, unit, type_target=UnitType.ALL):
        """Return the nearest friendly unit in sight of the given unit."""
        if type_target == UnitType.NONE:
            return None

        friendly_units = self.scenario.units_a if unit.team == "A" else self.scenario.units_b
        nearest_unit = None
        nearest_distance = float('inf')
        for target_unit in friendly_units:
            if (type_target is not UnitType.ALL and target_unit.unit_type != type_target) or not self.is_unit_still_alive(target_unit):
                continue
            if self.is_in_sight(unit, target_unit):
                distance = self.distance_between_coordinates(unit.x, unit.y, target_unit.x, target_unit.y)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_unit = target_unit
        return nearest_unit

    def is_unit_still_alive(self, unit):
        """Check if the given unit is still alive."""
        return unit.hp > 0

    def get_nearest_enemy_with_attributes(self, unit, attribute):
        """Return the nearest enemy unit with the lowest value of the given attribute."""
        enemy_units = self.scenario.units_b if unit.team == "A" else self.scenario.units_a
        nearest_unit = None
        best_attribute_value = float('inf')
        for target_unit in enemy_units:
            if not self.is_unit_still_alive(target_unit):
                continue
            attr_value = getattr(target_unit, attribute, None)
            if attr_value is not None and attr_value < best_attribute_value:
                best_attribute_value = attr_value
                nearest_unit = target_unit
        return nearest_unit

    def attack_unit(self, attacker_unit, target_unit):
        """Perform an attack on a target unit if possible."""
        if attacker_unit.can_attack() and self.is_in_reach(attacker_unit, target_unit) and self.is_unit_still_alive(attacker_unit) and self.is_unit_still_alive(target_unit):
            elevation_modifier = 1.0
            accuracy_modifier = attacker_unit.accuracy
            base_damage = 0

            for damage_type, damage_value in attacker_unit.attack.items():
                if damage_type in target_unit.armor:
                    base_damage += max(0, damage_value - target_unit.armor.get(damage_type))

            damage = max(1, base_damage * elevation_modifier * accuracy_modifier)
            target_unit.hp -= damage

            attacker_unit.perform_attack()
            attacker_unit.damage_dealt += damage
            self.reload_units.append(attacker_unit)
            self.as_unit_attacked = True
            return True
        return False

    ## ----------- Strategies functions -------------

    def type_present_in_team(self):
        """Return the set of unit types present in each team."""
        types_a = set()
        types_b = set()
        for unit in self.scenario.units_a:
            types_a.add(unit.unit_type)
        for unit in self.scenario.units_b:
            types_b.add(unit.unit_type)
        return {'A': types_a, 'B': types_b}

    def is_in_formation(self, unit, units, type_formation='ROND'):
        """Check if the unit is in the specified formation with the given units."""
        if type_formation == 'ROND':
            count = 0
            center_x = 0
            center_y = 0
            for u in units:
                if u.hp <= 0:
                    continue
                center_x += u.x
                center_y += u.y
                count += 1

            if count <= 0:
                return False

            center_x /= count
            center_y /= count

            angle = math.atan2(unit.y - center_y, unit.x - center_x)
            desired_distance = 5

            target_x = center_x + math.cos(angle) * desired_distance
            target_y = center_y + math.sin(angle) * desired_distance

            return self.compare_position(unit, target_x, target_y)
        return False

    def do_formation(self, unit, units, type_formation='ROND'):
        """Move the unit into the specified formation with the given units."""
        if type_formation == 'ROND':
            if not self.is_in_formation(unit, units, type_formation):
                target_cords = self.distance_for_unit_in_formation(unit, units)
                
                self.move_unit_towards_coordinates(unit, target_cords[0], target_cords[1])

    ## ----------- Distance functions -------------

    @staticmethod
    def distance_between_coordinates(unit_x, unit_y, other_unit_x, other_unit_y):
        return ((unit_x - other_unit_x) ** 2 + (unit_y - other_unit_y) ** 2) ** 0.5

    @staticmethod
    def compare_position(unit, x, y):
        return math.isclose(unit.x, x, abs_tol=(unit.speed/2)) and math.isclose(unit.y, y, abs_tol=(unit.speed/2))
    
    @staticmethod
    def distance_for_unit_in_formation(unit, units):
        center_x = sum(u.x for u in units) / len(units)
        center_y = sum(u.y for u in units) / len(units)

        angle = math.atan2(unit.y - center_y, unit.x - center_x)
        desired_distance = 5

        target_x = center_x + math.cos(angle) * desired_distance
        target_y = center_y + math.sin(angle) * desired_distance

        return target_x, target_y
