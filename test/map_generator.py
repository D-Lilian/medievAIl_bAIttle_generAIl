# map_generator.py

from scenario import Scenario
from unit import Crossbowman, Knight, Pikeman
import random
import math


class MapGenerator:
    """
    Generate symmetric battle scenarios with historically-inspired tactical formations.

    Design principles:
    - Symmetric battles (mirrored armies)
    - 100-200 units range
    - Fast battles (~2min max)
    """

    @staticmethod
    def generate_battle_scenario(
            units_per_team: int = 100,
            formation: str = 'classic',
            size_x: int = 200,
            size_y: int = 120
    ) -> Scenario:
        """
        Generate a symmetric battle scenario with tactical formations.

        :param units_per_team: Number of units per team (50-200)
        :param formation: Formation type
        :param size_x: Battlefield width
        :param size_y: Battlefield height
        :return: Scenario with tactically positioned armies
        """

        units_a = []
        units_b = []

        # Distance between armies
        engagement_distance = 60
        team_a_x = (size_x - engagement_distance) // 2
        team_b_x = team_a_x + engagement_distance
        center_y = size_y // 2

        print(f"\n{'=' * 70}")
        print(f"  GENERATING TACTICAL BATTLE SCENARIO")
        print(f"{'=' * 70}")
        print(f"Formation: {formation.upper()}")
        print(f"Map size: {size_x}x{size_y}")
        print(f"Units per team: {units_per_team}")
        print(f"{'=' * 70}\n")

        # Generate formations
        if formation == 'classic':
            units_a = MapGenerator._create_classic_formation(
                'A', team_a_x, center_y, size_y, units_per_team
            )
            units_b = MapGenerator._create_classic_formation(
                'B', team_b_x, center_y, size_y, units_per_team
            )

        elif formation == 'defensive':
            units_a = MapGenerator._create_defensive_formation(
                'A', team_a_x, center_y, size_y, units_per_team
            )
            units_b = MapGenerator._create_defensive_formation(
                'B', team_b_x, center_y, size_y, units_per_team
            )

        elif formation == 'offensive':
            units_a = MapGenerator._create_offensive_formation(
                'A', team_a_x, center_y, size_y, units_per_team
            )
            units_b = MapGenerator._create_offensive_formation(
                'B', team_b_x, center_y, size_y, units_per_team, mirror=True
            )

        elif formation == 'hammer_anvil':
            units_a = MapGenerator._create_hammer_anvil_formation(
                'A', team_a_x, center_y, size_y, units_per_team
            )
            units_b = MapGenerator._create_hammer_anvil_formation(
                'B', team_b_x, center_y, size_y, units_per_team, mirror=True
            )

        elif formation == 'testudo':
            units_a = MapGenerator._create_testudo_formation(
                'A', team_a_x, center_y, units_per_team
            )
            units_b = MapGenerator._create_testudo_formation(
                'B', team_b_x, center_y, units_per_team
            )

        elif formation == 'hollow_square':
            units_a = MapGenerator._create_hollow_square_formation(
                'A', team_a_x, center_y, units_per_team
            )
            units_b = MapGenerator._create_hollow_square_formation(
                'B', team_b_x, center_y, units_per_team
            )

        else:
            units_a = MapGenerator._create_classic_formation(
                'A', team_a_x, center_y, size_y, units_per_team
            )
            units_b = MapGenerator._create_classic_formation(
                'B', team_b_x, center_y, size_y, units_per_team
            )

        # Combine all units
        all_units = units_a + units_b

        # Display army composition
        comp_a = MapGenerator._get_composition(units_a)
        comp_b = MapGenerator._get_composition(units_b)

        # Create scenario
        scenario = Scenario(
            units=all_units,
            units_a=units_a,
            units_b=units_b,
            general_a=None,
            general_b=None,
            size_x=size_x,
            size_y=size_y
        )

        return scenario

    # ============ TACTICAL FORMATIONS ============

    @staticmethod
    def _create_classic_formation(team: str, spawn_x: float, center_y: float,
                                  map_height: int, num_units: int) -> list:
        """
        CLASSIC MEDIEVAL FORMATION (Battle of Agincourt style)

        Structure:
        - Front: 40% Pikemen
        - Center: 30% Knights
        - Back: 30% Crossbowmen

        """
        units = []

        # Unit distribution
        num_pikemen = int(num_units * 0.40)
        num_knights = int(num_units * 0.30)
        num_crossbowmen = num_units - num_pikemen - num_knights

        spacing = max(2.5, (map_height - 20) / (num_units + 1))
        start_y = max(10.0, center_y - (num_units * spacing) / 2)

        y_offset = 0

        # FRONT LINE: Pikemen
        for i in range(num_pikemen):
            y = start_y + y_offset
            unit = Pikeman(team=team, x=spawn_x, y=y)
            units.append(unit)
            y_offset += spacing

        # SECOND LINE: Knights
        knight_x = spawn_x + (5 if team == 'A' else -5)
        for i in range(num_knights):
            y = start_y + y_offset
            unit = Knight(team=team, x=knight_x, y=y)
            units.append(unit)
            y_offset += spacing

        # BACK LINE: Crossbowmen
        archer_x = spawn_x + (8 if team == 'A' else -8)
        for i in range(num_crossbowmen):
            y = start_y + y_offset
            unit = Crossbowman(team=team, x=archer_x, y=y)
            units.append(unit)
            y_offset += spacing

        return units

    @staticmethod
    def _create_defensive_formation(team: str, spawn_x: float, center_y: float,
                                    map_height: int, num_units: int) -> list:
        """
        DEFENSIVE FORMATION

        Structure:
        - Front: 50% Pikemen
        - Back: 25% Knights
        - Rear: 25% Crossbowmen

        """
        units = []

        num_pikemen = int(num_units * 0.50)
        num_knights = int(num_units * 0.25)
        num_crossbowmen = num_units - num_pikemen - num_knights

        spacing = max(2.0, (map_height - 20) / num_pikemen)
        start_y = max(10.0, center_y - (num_pikemen * spacing) / 2)

        # Dense pikemen wall (tight spacing)
        for i in range(num_pikemen):
            y = start_y + (i * spacing)
            unit = Pikeman(team=team, x=spawn_x, y=y)
            units.append(unit)

        # Knights in reserve (behind center)
        knight_spacing = max(3.0, (map_height - 40) / num_knights)
        knight_start_y = center_y - (num_knights * knight_spacing) / 2
        knight_x = spawn_x + (6 if team == 'A' else -6)

        for i in range(num_knights):
            y = knight_start_y + (i * knight_spacing)
            unit = Knight(team=team, x=knight_x, y=y)
            units.append(unit)

        # Crossbowmen behind (covering entire line)
        archer_spacing = max(2.5, (map_height - 20) / num_crossbowmen)
        archer_start_y = max(10.0, center_y - (num_crossbowmen * archer_spacing) / 2)
        archer_x = spawn_x + (10 if team == 'A' else -10)

        for i in range(num_crossbowmen):
            y = archer_start_y + (i * archer_spacing)
            unit = Crossbowman(team=team, x=archer_x, y=y)
            units.append(unit)

        return units

    @staticmethod
    def _create_offensive_formation(team: str, spawn_x: float, center_y: float,
                                    map_height: int, num_units: int, mirror: bool = False) -> list:
        """
        OFFENSIVE WEDGE FORMATION (Cavalry Charge)

        Structure:
        - Tip: 40% Knights
        - Wings: 30% Pikemen
        - Rear: 30% Crossbowmen
        """
        units = []

        num_knights = int(num_units * 0.40)
        num_pikemen = int(num_units * 0.30)
        num_crossbowmen = num_units - num_knights - num_pikemen

        direction = -1 if mirror else 1

        # Knights in triangle formation
        rows = int(math.sqrt(num_knights * 2))
        spacing = 3.0

        knight_index = 0
        for row in range(rows):
            units_in_row = min(row + 1, num_knights - knight_index)
            row_width = (units_in_row - 1) * spacing

            for col in range(units_in_row):
                if knight_index >= num_knights:
                    break

                x = spawn_x + (row * spacing * direction)
                y = center_y - row_width / 2 + (col * spacing)

                unit = Knight(team=team, x=x, y=y)
                units.append(unit)
                knight_index += 1

        # FLANKS: Pikemen on wings (above and below wedge)
        flank_offset = 25.0
        pikemen_per_flank = num_pikemen // 2

        # Upper flank
        for i in range(pikemen_per_flank):
            x = spawn_x + (i * 2.0 * direction)
            y = center_y - flank_offset
            unit = Pikeman(team=team, x=x, y=y)
            units.append(unit)

        # Lower flank
        for i in range(num_pikemen - pikemen_per_flank):
            x = spawn_x + (i * 2.0 * direction)
            y = center_y + flank_offset
            unit = Pikeman(team=team, x=x, y=y)
            units.append(unit)

        # REAR: Crossbowmen in line behind wedge
        archer_spacing = max(2.5, 50.0 / num_crossbowmen)
        archer_start_y = center_y - (num_crossbowmen * archer_spacing) / 2
        archer_x = spawn_x + (12 * direction)

        for i in range(num_crossbowmen):
            y = archer_start_y + (i * archer_spacing)
            unit = Crossbowman(team=team, x=archer_x, y=y)
            units.append(unit)

        return units

    @staticmethod
    def _create_hammer_anvil_formation(team: str, spawn_x: float, center_y: float,
                                       map_height: int, num_units: int, mirror: bool = False) -> list:
        """
        HAMMER AND ANVIL (Hannibal at Cannae)

        Structure:
        - Center: 30% Pikemen (anvil - holds enemy)
        - Flanks: 50% Knights (hammer - envelops enemy)
        - Rear: 20% Crossbowmen
        """
        units = []

        num_pikemen = int(num_units * 0.30)
        num_knights = int(num_units * 0.50)
        num_crossbowmen = num_units - num_pikemen - num_knights

        # CENTER (Anvil): Pikemen holding line
        pike_spacing = max(2.5, (map_height - 60) / num_pikemen)
        pike_start_y = center_y - (num_pikemen * pike_spacing) / 2

        for i in range(num_pikemen):
            y = pike_start_y + (i * pike_spacing)
            unit = Pikeman(team=team, x=spawn_x, y=y)
            units.append(unit)

        # FLANKS (Hammer): Knights split on wings
        knights_per_wing = num_knights // 2
        wing_offset = 30.0

        direction = -1 if mirror else 1

        # Upper wing
        for i in range(knights_per_wing):
            x = spawn_x + (i * 2.5 * direction)
            y = center_y - wing_offset
            unit = Knight(team=team, x=x, y=y)
            units.append(unit)

        # Lower wing
        for i in range(num_knights - knights_per_wing):
            x = spawn_x + (i * 2.5 * direction)
            y = center_y + wing_offset
            unit = Knight(team=team, x=x, y=y)
            units.append(unit)

        # REAR: Crossbowmen support
        archer_spacing = max(2.5, (map_height - 40) / num_crossbowmen)
        archer_start_y = center_y - (num_crossbowmen * archer_spacing) / 2
        archer_x = spawn_x + (8 * direction)

        for i in range(num_crossbowmen):
            y = archer_start_y + (i * archer_spacing)
            unit = Crossbowman(team=team, x=archer_x, y=y)
            units.append(unit)

        return units

    @staticmethod
    def _create_testudo_formation(team: str, spawn_x: float, center_y: float,
                                  num_units: int) -> list:
        """
        TESTUDO / TURTLE FORMATION (Roman Legion)

        Structure:
        - Core: 60% Pikemen
        - Corners: 25% Knights
        - Center: 15% Crossbowmen
        """
        units = []

        num_pikemen = int(num_units * 0.60)
        num_knights = int(num_units * 0.25)
        num_crossbowmen = num_units - num_pikemen - num_knights

        # Square of pikemen
        side = math.ceil(math.sqrt(num_pikemen))
        spacing = 2.5

        start_x = spawn_x - (side * spacing) / 2
        start_y = center_y - (side * spacing) / 2

        pike_index = 0
        for row in range(side):
            for col in range(side):
                if pike_index >= num_pikemen:
                    break

                x = start_x + (col * spacing)
                y = start_y + (row * spacing)

                unit = Pikeman(team=team, x=x, y=y)
                units.append(unit)
                pike_index += 1

        # Knights at corners
        corner_offset = (side * spacing) / 2 + 3
        corner_positions = [
            (spawn_x - corner_offset, center_y - corner_offset),
            (spawn_x + corner_offset, center_y - corner_offset),
            (spawn_x - corner_offset, center_y + corner_offset),
            (spawn_x + corner_offset, center_y + corner_offset)
        ]

        for i in range(num_knights):
            pos = corner_positions[i % 4]
            offset = (i // 4) * 2.5
            x = pos[0] + offset
            y = pos[1] + offset
            unit = Knight(team=team, x=x, y=y)
            units.append(unit)

        # Crossbowmen in center
        archer_side = math.ceil(math.sqrt(num_crossbowmen))
        archer_start_x = spawn_x - (archer_side * spacing) / 2
        archer_start_y = center_y - (archer_side * spacing) / 2

        archer_index = 0
        for row in range(archer_side):
            for col in range(archer_side):
                if archer_index >= num_crossbowmen:
                    break

                x = archer_start_x + (col * spacing)
                y = archer_start_y + (row * spacing)

                unit = Crossbowman(team=team, x=x, y=y)
                units.append(unit)
                archer_index += 1

        return units

    @staticmethod
    def _create_hollow_square_formation(team: str, spawn_x: float, center_y: float,
                                        num_units: int) -> list:
        """
        HOLLOW SQUARE (British Infantry vs Cavalry)

        Structure:
        - Perimeter: 70% Pikemen
        - Interior: 30% Crossbowmen
        """
        units = []

        num_pikemen = int(num_units * 0.70)
        num_crossbowmen = num_units - num_pikemen

        # Outer square perimeter (pikemen)
        side = math.ceil(math.sqrt(num_pikemen / 4))  # 4 sides
        spacing = 3.0

        pike_index = 0

        # Top side
        for i in range(side):
            if pike_index >= num_pikemen:
                break
            x = spawn_x - (side * spacing) / 2 + (i * spacing)
            y = center_y - (side * spacing) / 2
            unit = Pikeman(team=team, x=x, y=y)
            units.append(unit)
            pike_index += 1

        # Right side
        for i in range(side):
            if pike_index >= num_pikemen:
                break
            x = spawn_x + (side * spacing) / 2
            y = center_y - (side * spacing) / 2 + (i * spacing)
            unit = Pikeman(team=team, x=x, y=y)
            units.append(unit)
            pike_index += 1

        # Bottom side
        for i in range(side):
            if pike_index >= num_pikemen:
                break
            x = spawn_x + (side * spacing) / 2 - (i * spacing)
            y = center_y + (side * spacing) / 2
            unit = Pikeman(team=team, x=x, y=y)
            units.append(unit)
            pike_index += 1

        # Left side
        for i in range(num_pikemen - pike_index):
            x = spawn_x - (side * spacing) / 2
            y = center_y + (side * spacing) / 2 - (i * spacing)
            unit = Pikeman(team=team, x=x, y=y)
            units.append(unit)

        # Inner square (crossbowmen)
        inner_side = math.ceil(math.sqrt(num_crossbowmen))
        inner_spacing = 2.5

        archer_start_x = spawn_x - (inner_side * inner_spacing) / 2
        archer_start_y = center_y - (inner_side * inner_spacing) / 2

        archer_index = 0
        for row in range(inner_side):
            for col in range(inner_side):
                if archer_index >= num_crossbowmen:
                    break

                x = archer_start_x + (col * inner_spacing)
                y = archer_start_y + (row * inner_spacing)

                unit = Crossbowman(team=team, x=x, y=y)
                units.append(unit)
                archer_index += 1

        return units

    @staticmethod
    def _get_composition(units: list) -> dict:
        """Get army composition breakdown."""
        composition = {}
        for unit in units:
            unit_type = unit.name
            composition[unit_type] = composition.get(unit_type, 0) + 1
        return composition


# ============ PREDEFINED SCENARIOS ============

class PredefinedScenarios:
    """Collection of balanced, tactically sound scenarios."""

    @staticmethod
    def classic_medieval_battle() -> Scenario:
        """100v100 - Classic Medieval Battle (Agincourt style)"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=100,
            formation='classic',
            size_x=200,
            size_y=120
        )

    @staticmethod
    def defensive_siege() -> Scenario:
        """120v120 - Defensive Formation (Shield Wall)"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=120,
            formation='defensive',
            size_x=200,
            size_y=130
        )

    @staticmethod
    def cavalry_charge() -> Scenario:
        """150v150 - Offensive Wedge (Heavy Cavalry)"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=150,
            formation='offensive',
            size_x=220,
            size_y=140
        )

    @staticmethod
    def cannae_envelopment() -> Scenario:
        """180v180 - Hammer and Anvil (Hannibal's Tactics)"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=180,
            formation='hammer_anvil',
            size_x=240,
            size_y=150
        )

    @staticmethod
    def roman_legion() -> Scenario:
        """100v100 - Testudo Formation (Roman Tactics)"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=100,
            formation='testudo',
            size_x=200,
            size_y=120
        )

    @staticmethod
    def british_square() -> Scenario:
        """120v120 - Hollow Square (Anti-Cavalry)"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=120,
            formation='hollow_square',
            size_x=200,
            size_y=130
        )


# ============ TEST ============

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" " * 10 + "TACTICAL BATTLE SCENARIO GENERATOR - TEST SUITE")
    print("=" * 70)

    formations = ['classic', 'defensive', 'offensive', 'hammer_anvil', 'testudo', 'hollow_square']

    for form in formations:
        print(f"\n>>> TESTING: {form.upper()} FORMATION")
        scenario = MapGenerator.generate_battle_scenario(
            units_per_team=100,
            formation=form,
            size_x=200,
            size_y=120
        )

    print("\n" + "=" * 70)
    print(" " * 25 + "ALL TESTS COMPLETED ✅")
    print("=" * 70 + "\n")