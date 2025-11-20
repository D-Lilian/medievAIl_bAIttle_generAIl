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
        """Attack a target unit if possible and reset reload timer."""
        if self.can_attack(target):
            damage = self.get_damage_against(target)
            target.hp -= damage
            self.reload_timer = self.reload_time
    
    def move_towards(self, target_x: float, target_y: float, dt: float, board: 'Board' = None):
        """Move the unit towards a position while avoiding collisions."""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize and apply speed
            dx /= distance
            dy /= distance
            move_distance = self.speed * dt
            
            if move_distance < distance:
                new_x = self.x + dx * move_distance
                new_y = self.y + dy * move_distance
                
                # Check collisions with other units (first arrived keeps the space)
                collision = False
                if board:
                    for other in board.units:
                        if other is not self and other.hp > 0:
                            # Distance between new position and the other unit
                            dist_to_other = math.sqrt((new_x - other.x)**2 + (new_y - other.y)**2)
                            if dist_to_other < (self.collision_radius + other.collision_radius):
                                collision = True
                                break
                
                # If no collision, apply movement
                if not collision:
                    self.x = new_x
                    self.y = new_y
                # Otherwise stay in place (other unit already occupies space)
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
    hp_max = 100
    attack = 10
    melee_armor = 2
    pierce_armor = 2
    range = 0  # Melee
    line_of_sight = 4
    speed = 1.35  # tiles/second
    reload_time = 1.8  # seconds
    collision_radius = 0.6  # Cavalry = larger
    
    def __init__(self, x: float, y: float, team: int):
        super().__init__(x, y, team)


class Pikeman(Unit):
    """Pikeman - Anti-cavalry infantry."""
    
    name = "Pikeman"
    hp_max = 55
    attack = 4
    melee_armor = 0
    pierce_armor = 0
    range = 0
    line_of_sight = 4
    speed = 1.0
    reload_time = 3.0
    collision_radius = 0.45  # Infantry = normal size
    
    def __init__(self, x: float, y: float, team: int):
        super().__init__(x, y, team)
        # Huge bonus against cavalry
        self.bonus_vs = {'Knight': 22, 'Cavalry Archer': 22}


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
    reload_time = 2.0
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
        """Return all alive units (optionally filtered by team)."""
        units = [u for u in self.units if u.hp > 0]
        if team is not None:
            units = [u for u in units if u.equipe == team]
        return units
    
    def get_nearest_enemy(self, unit: Unit) -> Optional[Unit]:
        """Find the nearest enemy unit for the given unit."""
        # Convert 'A'/'B' or 1/2 to the opposite team
        if unit.equipe in ('A', 'a', 1):
            enemy_team = 'B'
        else:
            enemy_team = 'A'
        enemies = self.get_alive_units(team=enemy_team)
        if not enemies:
            return None
        
        nearest = min(enemies, key=lambda e: unit.distance_to(e))
        return nearest


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
    
    def __init__(self, board: Board, ai1_type: str = "DAFT", ai2_type: str = "DAFT"):
        self.board = board
        self.elapsed_time = 0.0  # Temps logique de la simulation
        self.dt = 0.05  # Time delta per tick (50ms), independent from framerate
        self.ai1_type = ai1_type
        self.ai2_type = ai2_type
    
    def step(self):
        """Advance the simulation by one logical tick."""
        # AI for each team
        self._run_ai(1, self.ai1_type)
        self._run_ai(2, self.ai2_type)
        
        # Update each unit
        for unit in self.board.get_alive_units():
            unit.update(self.dt)
        
        self.elapsed_time += self.dt
    
    def _run_ai(self, team: int, ai_type: str):
        """Run the AI for one team."""
        units = self.board.get_alive_units(team)
        
        if ai_type == "BRAINDEAD":
            # Does nothing - units only attack when in range
            pass
        
        elif ai_type == "DAFT":
            # Attack the nearest enemy without any strategy
            for unit in units:
                nearest_enemy = self.board.get_nearest_enemy(unit)
                if nearest_enemy:
                    # If in range, attack
                    if unit.can_attack(nearest_enemy):
                        unit.attack_unit(nearest_enemy, self.dt)
                    else:
                        # Otherwise, move closer
                        # For archers, get to optimal range
                        distance = unit.distance_to(nearest_enemy)
                        if distance > unit.range:
                            unit.move_towards(nearest_enemy.x, nearest_enemy.y, self.dt, self.board)
                        elif distance < unit.range * 0.8:  # Too close for an archer
                            # Step back a little
                            dx = unit.x - nearest_enemy.x
                            dy = unit.y - nearest_enemy.y
                            dist = math.sqrt(dx**2 + dy**2)
                            if dist > 0:
                                unit.move_towards(
                                    unit.x + (dx/dist) * 2,
                                    unit.y + (dy/dist) * 2,
                                    self.dt,
                                    self.board
                                )
    
    def is_finished(self) -> bool:
        """Check whether the battle is finished."""
        team_a_alive = len(self.board.get_alive_units('A'))
        team_b_alive = len(self.board.get_alive_units('B'))
        return team_a_alive == 0 or team_b_alive == 0


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
        # Face-to-face mirror formations - very close for immediate combat
        formations = [
            (Knight, 3),
            (Pikeman, 5),
            (Crossbowman, 4),
        ]
        
        y_pos = 40
        for unit_class, count in formations:
            # Team A (left) - position x = 50
            for i in range(count):
                board.add_unit(unit_class(50, y_pos + i*2, 'A'))
            
            # Team B (right) - position x = 70 (distance = 20 tiles)
            for i in range(count):
                board.add_unit(unit_class(70, y_pos + i*2, 'B'))
            
            y_pos += count * 2 + 3
    
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
    
    return Simulation(board, ai1_type="DAFT", ai2_type="DAFT")


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
