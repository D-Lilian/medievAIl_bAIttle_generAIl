# map_generator.py
from adodbapi.ado_consts import directions

from scenario import Scenario
from unit import Crossbowman, Knight, Pikeman
import random
import math

import units


class MapGenerator:
    """
    Generate symmetric battle scenarios with mirrored formations.

    Design principles:
    - Symmetric battles (mirrored armies)
    - 100-200 units range
    - Fast battles (~2min max)
    - Moderate starting distance (time to form up before engagement)
    """

    UNIT_CLASSES = [Crossbowman, Knight, Pikeman]

    @staticmethod
    def generate_battle_scenario(
            units_per_team: int = 100,
            formation: str = 'line',
            size_x: int = 200,
            size_y: int = 120
    ) -> Scenario:
        """
        Generate a symmetric battle scenario.

        :param units_per_team: Number of units per team
        :param formation: 'line', 'square', 'wedge', 'scattered'
        :param size_x: Battlefield width
        :param size_y: Battlefield height
        :return: Scenario with mirrored armies
        """

        units_a = []
        units_b = []

        # Distance between armies
        distance = 60

        team_a_x = (size_x - distance) // 2
        team_b_x = team_a_x + distance
        center_y = size_y // 2

        # Generate formations
        if formation == 'line':
            units_a = MapGenerator._create_line_formation(
                'A', team_a_x, center_y, size_y, units_per_team
            )
            units_b = MapGenerator._create_line_formation(
                'B', team_b_x, center_y, size_y, units_per_team
            )

        elif formation == 'square':
            units_a = MapGenerator._create_square_formation(
                'A', team_a_x, center_y, units_per_team
            )
            units_b = MapGenerator._create_square_formation(
                'B', team_b_x, center_y, units_per_team
            )

        elif formation == 'wedge':
            units_a = MapGenerator._create_wedge_formation(
                'A', team_a_x, center_y, units_per_team
            )
            units_b = MapGenerator._create_wedge_formation(
                'B', team_b_x, center_y, units_per_team, mirror=True
            )

        elif formation == 'scattered':
            units_a = MapGenerator._create_scattered_formation(
                'A', team_a_x, center_y, size_y, units_per_team
            )
            units_b = MapGenerator._create_scattered_formation(
                'B', team_b_x, center_y, size_y, units_per_team
            )

        elif formation == 'circle':
            units_a = MapGenerator._create_circle_formation(
                'A', team_a_x, center_y, units_per_team
            )
            units_b = MapGenerator._create_circle_formation(
                'B', team_b_x, center_y, units_per_team
            )

        elif formation == 'flank':
            # Attaque en tenaille (écartement vertical)
            units_a = MapGenerator._create_flank_formation(
                'A', team_a_x, center_y, units_per_team
            )
            units_b = MapGenerator._create_flank_formation(
                'B', team_b_x, center_y, units_per_team, mirror=True
            )

        elif formation == 'checkerboard':
            # Formation romaine en damier
            units_a = MapGenerator._create_checkerboard_formation(
                'A', team_a_x, center_y, units_per_team
            )
            units_b = MapGenerator._create_checkerboard_formation(
                'B', team_b_x, center_y, units_per_team, mirror=True
            )

        else:
            units_a = MapGenerator._create_line_formation(
                'A', team_a_x, center_y, size_y, units_per_team
            )
            units_b = MapGenerator._create_line_formation(
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

    @staticmethod
    def _create_line_formation(team: str, spawn_x: float, center_y: float,
                               map_height: int, num_units: int) -> list:
        """
        Vertical line formation
        """
        units = []

        spacing = max(2.0, (map_height - 20) / (num_units + 1))
        total_height = spacing * (num_units - 1)
        start_y = max(10.0, center_y - total_height / 2)

        for i in range(num_units):
            y = start_y + (i * spacing)
            UnitClass = random.choice(MapGenerator.UNIT_CLASSES)
            unit = UnitClass(team=team, x=spawn_x, y=y)
            units.append(unit)

        return units

    @staticmethod
    def _create_square_formation(team: str, spawn_x: float, center_y: float,
                                 num_units: int) -> list:
        """
        Square/rectangular formation 
        """
        units = []

        side = math.ceil(math.sqrt(num_units))
        spacing = 3.0

        total_width = (side - 1) * spacing
        total_height = (side - 1) * spacing

        if team == 'A':
            start_x = spawn_x
        else:
            start_x = spawn_x - total_width

        start_y = center_y - total_height / 2

        unit_index = 0
        for row in range(side):
            for col in range(side):
                if unit_index >= num_units:
                    break

                x = start_x + (col * spacing)
                y = start_y + (row * spacing)

                UnitClass = random.choice(MapGenerator.UNIT_CLASSES)
                unit = UnitClass(team=team, x=x, y=y)
                units.append(unit)

                unit_index += 1

        return units

    @staticmethod
    def _create_wedge_formation(team: str, spawn_x: float, center_y: float,
                                num_units: int, mirror: bool = False) -> list:
        """
        Wedge/triangle formation - offensive spearhead.
        """
        units = []

        # Calculate wedge dimensions
        rows = int(math.sqrt(num_units * 2))
        spacing = 3.0

        unit_index = 0
        for row in range(rows):
            units_in_row = min(row + 1, num_units - unit_index)

            for col in range(units_in_row):
                if unit_index >= num_units:
                    break

                # Center each row
                row_width = (units_in_row - 1) * spacing

                if mirror:  # Team B - point to the left
                    x = spawn_x - (row * spacing)
                else:  # Team A - point to the right
                    x = spawn_x + (row * spacing)

                y = center_y - row_width / 2 + (col * spacing)

                UnitClass = random.choice(MapGenerator.UNIT_CLASSES)
                unit = UnitClass(team=team, x=x, y=y)
                units.append(unit)

                unit_index += 1

        return units

    @staticmethod
    def _create_scattered_formation(team: str, spawn_x: float, center_y: float,
                                    map_height: int, num_units: int) -> list:
        """
        Scattered formation 
        """
        units = []

        zone_width = 20.0
        zone_height = min(map_height - 20, 80)

        for i in range(num_units):
            x = spawn_x + random.uniform(-zone_width / 2, zone_width / 2)
            y = center_y + random.uniform(-zone_height / 2, zone_height / 2)

            UnitClass = random.choice(MapGenerator.UNIT_CLASSES)
            unit = UnitClass(team=team, x=x, y=y)
            units.append(unit)

        return units

    @staticmethod
    def _get_composition(units: list) -> dict:
        """Get army composition breakdown"""
        composition = {}
        for unit in units:
            unit_type = unit.name
            composition[unit_type] = composition.get(unit_type, 0) + 1
        return composition

    @staticmethod
    def _create_circle_formation(team: str, spawn_x: float, center_y: float, num_units: int) -> list:
        """
            Circle/Orb formation
        """
        units = []
        spacing = 2.5

        circumference = num_units * spacing
        radius = max(5.0, circumference / (2 * math.pi))

        for i in range(num_units):
            angle = (2 * math.pi / num_units) * i

            x = spawn_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            UnitClass = random.choice(MapGenerator.UNIT_CLASSES)
            unit = UnitClass(team=team, x=x, y=y)
            units.append(unit)
        return units

    @staticmethod
    def _create_flank_formation(team: str, spawn_x: float, center_y: float, num_units: int, mirror: bool = False) -> list:
            units = []
            spacing = 2.5

            units_wings_1 = num_units // 2
            units_wings_2 = num_units - units_wings_1

            wing_offset = 30.0

            side = math.ceil(math.sqrt(units_wings_1))

            direction= -1 if mirror else 1

            #create Wing 1
            unit_index = 0
            start_y_1 = center_y - wing_offset
            for row in range(side):
                for col in range(side):
                    if unit_index >= units_wings_1:
                        break
                    x = spawn_x + (row * spacing * direction)
                    y = start_y_1 + (col * spacing)

                    UnitClass = random.choice(MapGenerator.UNIT_CLASSES)
                    unit = UnitClass(team=team, x=x, y=y)
                    units.append(unit)
                    unit_index += 1

            #wing 2
            side = math.ceil(math.sqrt(units_wings_2))
            unit_index = 0
            start_y_2 = center_y + wing_offset - (side -1) * spacing
            for row in range(side):
                for col in range(side):
                    if unit_index >= units_wings_2:
                        break
                    x = spawn_x + (row * spacing * direction)
                    y = start_y_2 + (col * spacing)

                    UnitClass = random.choice(MapGenerator.UNIT_CLASSES)
                    unit = UnitClass(team=team, x=x, y=y)
                    units.append(unit)
                    unit_index += 1
            return units

    @staticmethod
    def _create_checkerboard_formation(team: str, spawn_x: float, center_y: float,
                                       num_units: int, mirror: bool = False) -> list:
            """
                Checkerboard Formation

            """
            units = []
                
            # Calculate grid size
            side = math.ceil(math.sqrt(num_units * 2))
            spacing = 3.0
                
            total_width = (side - 1) * spacing
            total_height = (side - 1) * spacing

            if not mirror: # Team A
                start_x = spawn_x
            else: # Team B
                start_x = spawn_x - total_width

                start_y = center_y - total_height / 2
                
                placed = 0
        
            # Iterate over a grid
            for row in range(side):
                for col in range(side):
                    if placed >= num_units: break
                    
                    # Check for checkerboard pattern: (row + col) is even
                    if (row + col) % 2 == 0:
                        x = start_x + (col * spacing)
                        y = start_y + (row * spacing)

                        UnitClass = random.choice(MapGenerator.UNIT_CLASSES)
                        unit = UnitClass(team=team, x=x, y=y)
                        units.append(unit)
                        placed += 1
            return units







# ============ PREDEFINED SCENARIOS ============

class PredefinedScenarios:
    """
    Collection of balanced, ready-to-use scenarios.
    """

    @staticmethod
    def small_skirmish() -> Scenario:
        """50v50"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=50,
            formation='line',
            size_x=150,
            size_y=100
        )

    @staticmethod
    def standard_battle() -> Scenario:
        """100v100"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=100,
            formation='line',
            size_x=200,
            size_y=120
        )

    @staticmethod
    def large_battle() -> Scenario:
        """150v150"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=150,
            formation='square',
            size_x=220,
            size_y=140
        )

    @staticmethod
    def epic_battle() -> Scenario:
        """200v200"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=200,
            formation='wedge',
            size_x=240,
            size_y=150
        )