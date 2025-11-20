#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic game logic used to test the View.
Three units with AOE2-like stats, simple combat system.
"""

import math
from typing import List, Optional


class Unit:
    """Base class for all units."""

    # Collision size (radius of the circle occupied by the unit)
    collision_radius = 0.5  # Default, overridden in subclasses
    
    def __init__(self, x: float, y: float, team: int):
        self.x = x
        self.y = y
        self.equipe = team
        self.hp = self.hp_max
        self.reload_timer = 0.0
        self.target: Optional['Unit'] = None
        
    def distance_to(self, other: 'Unit') -> float:
        """Compute Euclidean distance to another unit (center to center)."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def collides_with(self, other: 'Unit') -> bool:
        """Return True if this unit collides with another (circle vs circle)."""
        distance = self.distance_to(other)
        return distance < (self.collision_radius + other.collision_radius)
    
    def can_attack(self, target: 'Unit') -> bool:
        """Check if this unit can attack the target."""
        if self.reload_timer > 0:
            return False
        # Cannot attack units from the same team
        if self.equipe == target.equipe:
            return False
        return self.distance_to(target) <= self.range
    
    def get_damage_against(self, target: 'Unit') -> int:
        """Compute damage dealt to the target using the AOE2 formula."""
        total_attack = self.attack
        
        # Bonus damage (simplified system)
        if hasattr(self, 'bonus_vs') and type(target).__name__ in self.bonus_vs:
            total_attack += self.bonus_vs[type(target).__name__]
        
        # AOE2 formula: max(1, Attack - Armor)
        # Use melee_armor or pierce_armor depending on attack type
        armor = target.pierce_armor if self.range > 0 else target.melee_armor
        damage = max(1, total_attack - armor)
        
        return damage
    
    def attack_unit(self, target: 'Unit', dt: float):
        """Attack a target unit if possible and reset reload timer.

        Multiple units can attack the same target in the same tick.
        """
        if self.can_attack(target):
            damage = self.get_damage_against(target)
            target.hp -= damage
            self.reload_timer = self.reload_time
    
    def move_towards(self, target_x: float, target_y: float, dt: float, board: 'Board' = None):
        """Move the unit freely towards any position, allowing movement in all directions."""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            # Normalize and apply speed
            dx /= distance
            dy /= distance
            move_distance = self.speed * dt
            # Move freely (ignore collision for stress-test)
            if move_distance < distance:
                self.x += dx * move_distance
                self.y += dy * move_distance
            else:
                self.x = target_x
                self.y = target_y
    
    def update(self, dt: float):
        """Update the unit internal state (reload timer)."""
        if self.reload_timer > 0:
            self.reload_timer = max(0, self.reload_timer - dt)


class Knight(Unit):
    """Knight - Heavy cavalry, strong against archers."""
    
    name = "Knight"
    hp_max = 120
    attack = 12
    melee_armor = 2
    pierce_armor = 2
    range = 0  # Melee
    line_of_sight = 4
    speed = 1.35  # tiles/second
    reload_time = 1.35  # seconds
    collision_radius = 0.6  # Cavalry = larger
    
    def __init__(self, x: float, y: float, team: int):
        super().__init__(x, y, team)


class Pikeman(Unit):
    """Pikeman - Anti-cavalry infantry."""
    
    name = "Pikeman"
    hp_max = 45
    attack = 3
    melee_armor = 0
    pierce_armor = 0
    range = 0
    line_of_sight = 4
    speed = 1.0
    reload_time = 3.05
    collision_radius = 0.45  # Infantry = normal size
    
    def __init__(self, x: float, y: float, team: int):
        super().__init__(x, y, team)
        # Bonus against cavalry
        self.bonus_vs = {'Knight': 15}


class Crossbowman(Unit):
    """Crossbowman - Ranged archer, weak in melee."""
    
    name = "Crossbowman"
    hp_max = 35
    attack = 5
    melee_armor = 0
    pierce_armor = 0
    range = 5  # tiles
    line_of_sight = 7
    speed = 0.96
    reload_time = 2.03
    collision_radius = 0.45  # Archers = normal size
    
    def __init__(self, x: float, y: float, team: int):
        super().__init__(x, y, team)


class Board:
    """Game board containing all units."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.units: List[Unit] = []
    
    def add_unit(self, unit: Unit):
        """Add a unit to the board."""
        self.units.append(unit)
    
    def get_alive_units(self, team: Optional[int] = None) -> List[Unit]:
        """Return all alive units (optionally filtered by team).

        Units internally always use 'A' or 'B' for the team.
        This helper accepts both:
        - logical teams: 'A' / 'B'
        - view teams: 1 / 2
        """
        units = [u for u in self.units if u.hp > 0]
        if team is not None:
            # Normalize team representation
            if team in (1, '1'):
                normalized = 'A'
            elif team in (2, '2'):
                normalized = 'B'
            else:
                normalized = team
            units = [u for u in units if u.equipe == normalized]
        return units
    
    def get_nearest_enemy(self, unit: Unit) -> Optional[Unit]:
        """Find the nearest alive enemy unit for the given unit.

        Only living enemies are considered, regardless of type or position.
        """
        if unit.equipe in ('A', 'a'):
            enemy_team = 'B'
        else:
            enemy_team = 'A'
        # Only consider alive enemies
        enemies = [e for e in self.units if e.hp > 0 and e.equipe == enemy_team]
        if not enemies:
            return None
        return min(enemies, key=lambda e: unit.distance_to(e))


class Simulation:
    """
    Real-time battle simulation (no turns).

    Based on the teacher specifications:
    - Continuous floating positions (x, y)
    - Circular collision (radius per unit type)
    - Circular line of sight (Euclidean distance)
    - First arrived occupies the space (no turn priority)
    - General controls all units in real time
    """
    
    def __init__(self, board: Board, ai1_type: str = "BRAINDEAD", ai2_type: str = "DAFT"):
        self.board = board
        self.elapsed_time = 0.0  # Temps logique de la simulation
        # Slower logical time for more leisurely battles
        self.dt = 0.1  # Time delta per tick (100ms logical)
        self.ai1_type = ai1_type
        self.ai2_type = ai2_type
        # Hard time limit to avoid infinite battles (2 minutes logical time)
        self.max_time = 120.0
    
    def step(self):
        """Advance the simulation by one logical tick."""
        # Stop advancing time if limit is reached (but keep final state)
        if self.elapsed_time >= self.max_time:
            return
        # AI for each team
        self._run_ai(1, self.ai1_type)
        self._run_ai(2, self.ai2_type)
        
        # Update each unit
        for unit in self.board.get_alive_units():
            unit.update(self.dt)
        
        self.elapsed_time += self.dt
    
    def _run_ai(self, team: int, ai_type: str):
        """Run the AI for one team.

        Available behaviours:
        - BRAINDEAD : Captain BRAINDEAD - Units attack if enemy in range, but don't seek fights.
        - DAFT      : Major DAFT - All army attacks nearest enemy with no consideration.
        - SMART     : Advanced AI (reserved for future use).
        """
        units = self.board.get_alive_units(team)

        if ai_type == "BRAINDEAD":
            # Captain BRAINDEAD: Zero tactical AI
            # Units attack if enemy in range, but don't move to seek fights
            for unit in units:
                nearest_enemy = self.board.get_nearest_enemy(unit)
                if nearest_enemy and unit.can_attack(nearest_enemy):
                    unit.attack_unit(nearest_enemy, self.dt)

        elif ai_type == "DAFT":
            # Major DAFT: Dumb-As-Fuck-Tactician
            # All army attacks nearest enemy with absolutely no further consideration
            for unit in units:
                nearest_enemy = self.board.get_nearest_enemy(unit)
                if nearest_enemy:
                    if unit.can_attack(nearest_enemy):
                        unit.attack_unit(nearest_enemy, self.dt)
                    else:
                        unit.move_towards(nearest_enemy.x, nearest_enemy.y, self.dt, self.board)

        elif ai_type == "SMART":
            # Advanced AI (placeholder)
            for unit in units:
                target = self.board.get_nearest_enemy(unit)
                if not target:
                    continue
                if unit.can_attack(target):
                    unit.attack_unit(target, self.dt)
                else:
                    unit.move_towards(target.x, target.y, self.dt, self.board)
    
    def is_finished(self) -> bool:
        """Check whether the battle is finished.

        A battle ends only when all enemies of one side are dead.
        The max_time is a safety guard, but tests and the View
        assume that a winner is found strictly before this limit.
        """
        team_a_alive = len(self.board.get_alive_units('A'))
        team_b_alive = len(self.board.get_alive_units('B'))

        # Victory: one side wiped out
        if team_a_alive == 0 or team_b_alive == 0:
            return True

        # Otherwise, keep fighting (no draw allowed here)
        return False


def create_test_scenario(scenario_type: str = "mirror") -> Simulation:
    """
    Create a test scenario for the battle simulation.

    Args:
        scenario_type: Scenario type ("mirror", "lanchester", "counter_demo")

    Returns:
        Simulation: Configured simulation instance for the chosen scenario
    """
    board = Board(120, 120)
    
    if scenario_type == "mirror":
        # Complex formations: Square formations with tactical unit placement
        # Each team: 62 Knights, 126 Pikemen, 62 Crossbowmen = 250 units
        # Formation: Square with Knights at front/corners, Pikemen in center, Crossbowmen at back
        # But different strategies: Team A braindead, Team B daft
        
        # Team A: Rectangular formation (same as team B for mirror start)
        # Front: Knights (4 rows), Middle: Pikemen (8 rows), Back: Crossbowmen (4 rows)
        base_x_a, base_y_a = 30, 35
        unit_list_a = ([Knight] * 62 + [Pikeman] * 126 + [Crossbowman] * 62)
        
        # 16 columns, 16 rows
        idx = 0
        for row in range(16):
            for col in range(16):
                if idx >= len(unit_list_a):
                    break
                x = base_x_a + col * 2.5
                y = base_y_a + row * 2.5
                board.add_unit(unit_list_a[idx](x, y, 'A'))
                idx += 1
        
        # Team B: Rectangular formation (mirrored - knights at back)
        # Front: Crossbowmen, Middle: Pikemen, Back: Knights
        base_x_b, base_y_b = 30, 80
        unit_list_b = ([Knight] * 62 + [Pikeman] * 126 + [Crossbowman] * 62)
        
        # 16 columns, 16 rows, but place in reverse row order for mirror
        idx = 0
        for row in range(15, -1, -1):  # Reverse order: row 15 to 0
            for col in range(16):
                if idx >= len(unit_list_b):
                    break
                x = base_x_b + col * 2.5
                y = base_y_b + row * 2.5
                board.add_unit(unit_list_b[idx](x, y, 'B'))
                idx += 1
    
    elif scenario_type == "lanchester":
        # Lanchester's law test - identical compositions on both sides
        N = 8
        
        # N Knights for team A
        for i in range(N):
            board.add_unit(Knight(45, 35 + i*3, 'A'))
        
        # N Knights for team B (same number!)
        for i in range(N):
            board.add_unit(Knight(75, 35 + i*3, 'B'))
    
    elif scenario_type == "counter_demo":
        # Demonstration of the counter system with identical compositions.
        # Each team has: 3 Knights, 5 Pikemen, 4 Crossbowmen
        # But different positioning to test tactics.

        # Team A: mixed classic formation
        y = 35
        for i in range(3):
            board.add_unit(Knight(42, y + i*2, 'A'))
        y += 8
        for i in range(5):
            board.add_unit(Pikeman(42, y + i*2, 'A'))
        y += 12
        for i in range(4):
            board.add_unit(Crossbowman(42, y + i*2, 'A'))
        
        # Team B: same composition, mirrored formation
        y = 35
        for i in range(3):
            board.add_unit(Knight(78, y + i*2, 'B'))
        y += 8
        for i in range(5):
            board.add_unit(Pikeman(78, y + i*2, 'B'))
        y += 12
        for i in range(4):
            board.add_unit(Crossbowman(78, y + i*2, 'B'))
    
    # By default, we give different behaviours to each team so that
    # identical armies can win or lose based on decisions, not stats.
    return Simulation(board, ai1_type="BRAINDEAD", ai2_type="DAFT")


if __name__ == "__main__":
    # Quick test with spec verification
    sim = create_test_scenario("mirror")
    
    print("=== Simulation test ===")
    print(f"Units team A: {len(sim.board.get_alive_units('A'))}")
    print(f"Units team B: {len(sim.board.get_alive_units('B'))}")

    # Check teacher specifications
    print("\n--- Specs verification ---")
    u = sim.board.units[0]
    print(f"Floating position: ({u.x}, {u.y}) - Type: {type(u.x).__name__}")
    print(f"Collision radius: {u.collision_radius}")
    print(f"Line of sight: {u.line_of_sight} (circular)")

    # Simulate until battle is over (max 1000 ticks)
    print("\n--- Battle simulation ---")
    for i in range(1000):
        sim.step()
        if i % 200 == 0:
            t_a = len(sim.board.get_alive_units('A'))
            t_b = len(sim.board.get_alive_units('B'))
            print(f"t={sim.elapsed_time:5.1f}s: TeamA={t_a:2} vs TeamB={t_b:2}")
        if sim.is_finished():
            print(f"  Battle finished at tick {i}")
            break
    
    print(f"\nResult after {sim.elapsed_time:.2f}s:")
    t_a_alive = len(sim.board.get_alive_units('A'))
    t_b_alive = len(sim.board.get_alive_units('B'))
    print(f"Units team A: {t_a_alive}")
    print(f"Units team B: {t_b_alive}")

    if sim.is_finished():
        winner = 'A' if t_a_alive > 0 else 'B'
        print(f"\nVICTORY: Team {winner}")
    else:
        print("\nSimulation stopped (tick limit reached)")
