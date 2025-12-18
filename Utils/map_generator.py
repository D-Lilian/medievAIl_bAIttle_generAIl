# -*- coding: utf-8 -*-
"""
@file map_generator.py
@brief Map Generator - Creates battle scenarios

@details
Generates symmetric battle scenarios with various tactical formations.
Used to create balanced and interesting initial states for simulations.

"""

from Model.scenario import Scenario
from Model.units import Crossbowman, Knight, Pikeman
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
            size_x: int = 120,
            size_y: int = 120
    ) -> Scenario:
        """
        Generate a symmetric battle scenario with tactical formations.
        
        Design: Team A on left half, Team B mirrors on right half.
        Armies positioned close enough for fast battles (~2min max).

        :param units_per_team: Number of units per team (50-200)
        :param formation: Formation type
        :param size_x: Battlefield width
        :param size_y: Battlefield height
        :return: Scenario with tactically positioned armies
        """

        # Margin from map edges
        margin = 10
        
        # Usable area
        usable_y = size_y - 2 * margin  # e.g., 100 for 120 height
        
        # Team A spawns on left third, Team B mirrors on right third
        # Distance between armies: ~30-40 units for fast engagement
        team_a_x = size_x // 4  # 30 for 120 width
        team_b_x = size_x - team_a_x  # 90 for 120 width (mirrored)
        
        center_y = size_y // 2

        # Generate formations for Team A
        if formation == 'classic':
            units_a = MapGenerator._create_classic_formation_v2(
                'A', team_a_x, center_y, usable_y, margin, units_per_team
            )
        elif formation == 'defensive':
            units_a = MapGenerator._create_defensive_formation_v2(
                'A', team_a_x, center_y, usable_y, margin, units_per_team
            )
        elif formation == 'offensive':
            units_a = MapGenerator._create_offensive_formation_v2(
                'A', team_a_x, center_y, usable_y, margin, units_per_team
            )
        elif formation == 'hammer_anvil':
            units_a = MapGenerator._create_hammer_anvil_v2(
                'A', team_a_x, center_y, usable_y, margin, units_per_team
            )
        elif formation == 'testudo':
            units_a = MapGenerator._create_testudo_v2(
                'A', team_a_x, center_y, usable_y, margin, units_per_team
            )
        elif formation == 'hollow_square':
            units_a = MapGenerator._create_hollow_square_v2(
                'A', team_a_x, center_y, usable_y, margin, units_per_team
            )
        else:
            units_a = MapGenerator._create_classic_formation_v2(
                'A', team_a_x, center_y, usable_y, margin, units_per_team
            )
        
        # Mirror Team A to create Team B
        units_b = MapGenerator._mirror_units(units_a, size_x)
        
        # Combine all units
        all_units = units_a + units_b

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
    def _mirror_units(units_a: list, size_x: int) -> list:
        """
        Mirror Team A units to create Team B.
        X is mirrored: new_x = size_x - x
        Y stays the same.
        """
        units_b = []
        for unit in units_a:
            mirrored_x = size_x - unit.x
            # Create same unit type for team B
            if isinstance(unit, Knight):
                new_unit = Knight(team='B', x=mirrored_x, y=unit.y)
            elif isinstance(unit, Pikeman):
                new_unit = Pikeman(team='B', x=mirrored_x, y=unit.y)
            elif isinstance(unit, Crossbowman):
                new_unit = Crossbowman(team='B', x=mirrored_x, y=unit.y)
            else:
                new_unit = Knight(team='B', x=mirrored_x, y=unit.y)
            units_b.append(new_unit)
        return units_b

    # ============ FORMATION V2 (Tactical formations within map bounds) ============

    @staticmethod
    def _create_classic_formation_v2(team: str, spawn_x: float, center_y: float,
                                     usable_height: float, margin: float, 
                                     num_units: int) -> list:
        """
        CLASSIC MEDIEVAL FORMATION (Battle of Agincourt style)
        
        Three-line formation facing the enemy:
        - Front LINE: Pikemen in a wide horizontal line
        - Second LINE: Knights ready to charge through gaps
        - Back LINE: Crossbowmen for ranged support
        
        Shape: === (three horizontal lines)
        """
        units = []

        num_pikemen = int(num_units * 0.40)
        num_knights = int(num_units * 0.30)
        num_crossbowmen = num_units - num_pikemen - num_knights

        # Spacing for a wide front
        unit_spacing = min(2.5, usable_height / max(num_pikemen, 1))
        line_depth = 4.0  # Distance between lines

        # Center the formation vertically
        formation_height = num_pikemen * unit_spacing
        start_y = margin + (usable_height - formation_height) / 2

        # Front line: Pikemen in a single wide line
        for i in range(num_pikemen):
            y = start_y + i * unit_spacing
            units.append(Pikeman(team=team, x=spawn_x, y=y))

        # Second line: Knights (slightly narrower, centered)
        knight_spacing = min(3.0, usable_height / max(num_knights, 1))
        knight_height = num_knights * knight_spacing
        knight_start_y = margin + (usable_height - knight_height) / 2
        for i in range(num_knights):
            y = knight_start_y + i * knight_spacing
            units.append(Knight(team=team, x=spawn_x + line_depth, y=y))

        # Back line: Crossbowmen (spread out for firing lanes)
        crossbow_spacing = min(3.5, usable_height / max(num_crossbowmen, 1))
        crossbow_height = num_crossbowmen * crossbow_spacing
        crossbow_start_y = margin + (usable_height - crossbow_height) / 2
        for i in range(num_crossbowmen):
            y = crossbow_start_y + i * crossbow_spacing
            units.append(Crossbowman(team=team, x=spawn_x + 2 * line_depth, y=y))

        return units

    @staticmethod
    def _place_line(unit_class, team: str, x: float, start_y: float, 
                    count: int, spacing: float) -> list:
        """Place units in a horizontal line (same X, varying Y)."""
        units = []
        for i in range(count):
            y = start_y + i * spacing
            units.append(unit_class(team=team, x=x, y=y))
        return units

    @staticmethod
    def _place_centered_line(unit_class, team: str, x: float, center_y: float,
                             count: int, spacing: float) -> list:
        """Place units in a horizontal line centered on center_y."""
        start_y = center_y - (count - 1) * spacing / 2
        return MapGenerator._place_line(unit_class, team, x, start_y, count, spacing)

    @staticmethod
    def _create_defensive_formation_v2(team: str, spawn_x: float, center_y: float,
                                       usable_height: float, margin: float,
                                       num_units: int) -> list:
        """
        DEFENSIVE FORMATION - Shield Wall
        
        Dense front with multiple rows of pikemen:
        - Front 3 rows: Pikemen (dense shield wall)
        - Behind: Knights as counter-charge reserve
        - Rear: Crossbowmen protected behind the wall
        
        Shape: ≡≡≡ (thick horizontal wall)
        """
        units = []
        
        num_pikemen = int(num_units * 0.50)
        num_knights = int(num_units * 0.25)
        num_crossbowmen = num_units - num_pikemen - num_knights
        
        # Dense pikeman wall - 3 rows deep
        pikes_per_row = num_pikemen // 3
        pike_spacing = min(2.0, usable_height / max(pikes_per_row, 1))
        row_depth = 2.0  # Very tight rows
        
        pike_start_y = margin + (usable_height - pikes_per_row * pike_spacing) / 2
        
        for row in range(3):
            remaining = num_pikemen - row * pikes_per_row
            count = min(pikes_per_row, remaining)
            for i in range(count):
                y = pike_start_y + i * pike_spacing
                units.append(Pikeman(team=team, x=spawn_x + row * row_depth, y=y))

        # Knights behind in 2 rows
        knights_per_row = num_knights // 2
        knight_spacing = min(3.0, usable_height / max(knights_per_row, 1))
        knight_start_y = margin + (usable_height - knights_per_row * knight_spacing) / 2
        knight_x = spawn_x + 3 * row_depth + 2
        
        for row in range(2):
            remaining = num_knights - row * knights_per_row
            count = min(knights_per_row, remaining)
            for i in range(count):
                y = knight_start_y + i * knight_spacing
                units.append(Knight(team=team, x=knight_x + row * 3, y=y))

        # Crossbowmen at rear in a single line
        crossbow_spacing = min(2.5, usable_height / max(num_crossbowmen, 1))
        crossbow_start_y = margin + (usable_height - num_crossbowmen * crossbow_spacing) / 2
        crossbow_x = knight_x + 8
        
        for i in range(num_crossbowmen):
            y = crossbow_start_y + i * crossbow_spacing
            units.append(Crossbowman(team=team, x=crossbow_x, y=y))
        
        return units

    @staticmethod
    def _create_offensive_formation_v2(team: str, spawn_x: float, center_y: float,
                                       usable_height: float, margin: float,
                                       num_units: int) -> list:
        """
        OFFENSIVE FORMATION - Cavalry Wedge
        
        Knights in wedge/arrow formation at front:
        - Front: Knights in V-shape (wedge)
        - Behind: Pikemen in support column
        - Flanks: Crossbowmen for covering fire
        
        Shape: ▷ (arrow pointing at enemy)
        """
        units = []
        
        num_knights = int(num_units * 0.40)
        num_pikemen = int(num_units * 0.30)
        num_crossbowmen = num_units - num_knights - num_pikemen
        
        # Knights in wedge formation
        # Wedge: 1 at tip, then 3, then 5, etc.
        wedge_rows = int((2 * num_knights) ** 0.5)
        knight_idx = 0
        row_depth = 3.0
        
        for row in range(wedge_rows):
            units_in_row = min(1 + row * 2, num_knights - knight_idx)
            if units_in_row <= 0:
                break
            
            row_width = (units_in_row - 1) * 2.5
            start_y = center_y - row_width / 2
            
            for i in range(units_in_row):
                y = start_y + i * 2.5
                units.append(Knight(team=team, x=spawn_x + row * row_depth, y=y))
                knight_idx += 1
                if knight_idx >= num_knights:
                    break

        # Pikemen in column behind the wedge
        pike_x = spawn_x + wedge_rows * row_depth + 2
        pike_spacing = min(2.5, usable_height / max(num_pikemen, 1))
        pike_start_y = margin + (usable_height - num_pikemen * pike_spacing) / 2
        
        for i in range(num_pikemen):
            y = pike_start_y + i * pike_spacing
            units.append(Pikeman(team=team, x=pike_x, y=y))

        # Crossbowmen on flanks
        half_crossbow = num_crossbowmen // 2
        crossbow_x = spawn_x + 2  # Alongside the wedge
        
        # Top flank
        for i in range(half_crossbow):
            y = margin + i * 3.0
            units.append(Crossbowman(team=team, x=crossbow_x + i * 1.5, y=y))
        
        # Bottom flank
        for i in range(num_crossbowmen - half_crossbow):
            y = margin + usable_height - i * 3.0
            units.append(Crossbowman(team=team, x=crossbow_x + i * 1.5, y=y))
        
        return units

    @staticmethod
    def _create_hammer_anvil_v2(team: str, spawn_x: float, center_y: float,
                                usable_height: float, margin: float,
                                num_units: int) -> list:
        """
        HAMMER AND ANVIL - Cannae/Hannibal Tactics
        
        Center holds while flanks encircle:
        - Center (Anvil): Pikemen line to hold enemy
        - Flanks (Hammer): Knights on both wings for pincer
        - Rear: Crossbowmen for ranged harassment
        
        Shape:  K        K
               ====P====
                  C
        """
        units = []
        
        num_pikemen = int(num_units * 0.40)
        num_knights = int(num_units * 0.30)
        num_crossbowmen = num_units - num_pikemen - num_knights
        
        # Pikemen in center line (the Anvil)
        pike_spacing = min(2.0, usable_height * 0.5 / max(num_pikemen, 1))
        pike_width = num_pikemen * pike_spacing
        pike_start_y = center_y - pike_width / 2
        
        for i in range(num_pikemen):
            y = pike_start_y + i * pike_spacing
            units.append(Pikeman(team=team, x=spawn_x, y=y))

        # Knights on flanks (the Hammer) - positioned forward
        half_knights = num_knights // 2
        flank_x = spawn_x - 5  # Slightly forward
        knight_spacing = 3.0
        
        # Top flank (upper part of map)
        for i in range(half_knights):
            row = i // 3
            col = i % 3
            y = margin + col * knight_spacing
            x = flank_x + row * 3
            units.append(Knight(team=team, x=x, y=y))
        
        # Bottom flank (lower part of map)
        for i in range(num_knights - half_knights):
            row = i // 3
            col = i % 3
            y = margin + usable_height - col * knight_spacing
            x = flank_x + row * 3
            units.append(Knight(team=team, x=x, y=y))

        # Crossbowmen behind center
        crossbow_x = spawn_x + 6
        crossbow_spacing = min(2.5, usable_height * 0.6 / max(num_crossbowmen, 1))
        crossbow_start_y = center_y - (num_crossbowmen * crossbow_spacing) / 2
        
        for i in range(num_crossbowmen):
            y = crossbow_start_y + i * crossbow_spacing
            units.append(Crossbowman(team=team, x=crossbow_x, y=y))
        
        return units

    @staticmethod
    def _create_testudo_v2(team: str, spawn_x: float, center_y: float,
                           usable_height: float, margin: float,
                           num_units: int) -> list:
        """
        TESTUDO FORMATION - Roman Turtle
        
        Ultra-compact square with pikemen on all edges:
        - Outer shell: Pikemen forming a protective perimeter
        - Inner core: Knights and Crossbowmen protected inside
        
        Shape: ▢ (compact square)
        """
        units = []
        
        num_pikemen = int(num_units * 0.60)
        num_knights = int(num_units * 0.20)
        num_crossbowmen = num_units - num_pikemen - num_knights
        
        # Calculate square dimensions
        side_length = int(num_units ** 0.5)
        spacing = 2.0
        
        formation_size = side_length * spacing
        start_x = spawn_x
        start_y = center_y - formation_size / 2
        
        # Pikemen form the outer perimeter
        pike_idx = 0
        
        # Top edge
        for i in range(side_length):
            if pike_idx >= num_pikemen:
                break
            units.append(Pikeman(team=team, x=start_x + i * spacing, y=start_y))
            pike_idx += 1
        
        # Bottom edge
        for i in range(side_length):
            if pike_idx >= num_pikemen:
                break
            units.append(Pikeman(team=team, x=start_x + i * spacing, y=start_y + formation_size))
            pike_idx += 1
        
        # Left edge (excluding corners)
        for i in range(1, side_length - 1):
            if pike_idx >= num_pikemen:
                break
            units.append(Pikeman(team=team, x=start_x, y=start_y + i * spacing))
            pike_idx += 1
        
        # Right edge (excluding corners)
        for i in range(1, side_length - 1):
            if pike_idx >= num_pikemen:
                break
            units.append(Pikeman(team=team, x=start_x + formation_size, y=start_y + i * spacing))
            pike_idx += 1
        
        # Fill remaining pikemen in second ring if any
        inner_start = spacing
        for i in range(pike_idx, num_pikemen):
            row = (i - pike_idx) // (side_length - 2)
            col = (i - pike_idx) % (side_length - 2)
            if row >= side_length - 2:
                break
            units.append(Pikeman(team=team, 
                                x=start_x + inner_start + col * spacing,
                                y=start_y + inner_start + row * spacing))

        # Knights in the inner core
        inner_offset = 2 * spacing
        knight_area = side_length - 4
        if knight_area < 2:
            knight_area = 2
        
        for i in range(num_knights):
            row = i // knight_area
            col = i % knight_area
            units.append(Knight(team=team,
                               x=start_x + inner_offset + col * spacing,
                               y=start_y + inner_offset + row * spacing))

        # Crossbowmen in the center core
        for i in range(num_crossbowmen):
            row = i // knight_area
            col = i % knight_area
            units.append(Crossbowman(team=team,
                                    x=start_x + inner_offset + spacing + col * spacing,
                                    y=start_y + inner_offset + spacing + row * spacing))
        
        return units

    @staticmethod
    def _create_hollow_square_v2(team: str, spawn_x: float, center_y: float,
                                 usable_height: float, margin: float,
                                 num_units: int) -> list:
        """
        HOLLOW SQUARE - British Anti-Cavalry
        
        Square formation with hollow center for crossbowmen:
        - Outer ring: Pikemen facing outward (anti-cavalry)
        - Middle: Knights as mobile reserve
        - Center hollow: Crossbowmen firing outward
        
        Shape: □ with ○ inside (hollow square)
        """
        units = []
        
        num_pikemen = int(num_units * 0.50)
        num_knights = int(num_units * 0.20)
        num_crossbowmen = num_units - num_pikemen - num_knights
        
        # Square dimensions
        outer_side = int((num_pikemen / 4) + 1)  # Units per side
        spacing = 2.5
        
        square_size = outer_side * spacing
        start_x = spawn_x
        start_y = center_y - square_size / 2
        
        pike_idx = 0
        
        # Place pikemen on all 4 edges of the square
        # Front edge (facing enemy)
        for i in range(outer_side):
            if pike_idx >= num_pikemen:
                break
            units.append(Pikeman(team=team, x=start_x, y=start_y + i * spacing))
            pike_idx += 1
        
        # Back edge
        for i in range(outer_side):
            if pike_idx >= num_pikemen:
                break
            units.append(Pikeman(team=team, x=start_x + square_size, y=start_y + i * spacing))
            pike_idx += 1
        
        # Top edge (excluding corners)
        for i in range(1, outer_side - 1):
            if pike_idx >= num_pikemen:
                break
            units.append(Pikeman(team=team, x=start_x + i * spacing, y=start_y))
            pike_idx += 1
        
        # Bottom edge (excluding corners)
        for i in range(1, outer_side - 1):
            if pike_idx >= num_pikemen:
                break
            units.append(Pikeman(team=team, x=start_x + i * spacing, y=start_y + square_size))
            pike_idx += 1

        # Knights in a ring inside the pikemen
        inner_offset = spacing * 2
        inner_side = outer_side - 4
        if inner_side < 2:
            inner_side = 2
        
        knight_idx = 0
        inner_size = inner_side * spacing
        inner_start_x = start_x + inner_offset
        inner_start_y = start_y + inner_offset
        
        # Knights on inner edges
        for edge in range(4):
            for i in range(inner_side // 4 + 1):
                if knight_idx >= num_knights:
                    break
                if edge == 0:  # front
                    units.append(Knight(team=team, x=inner_start_x, y=inner_start_y + i * spacing))
                elif edge == 1:  # back
                    units.append(Knight(team=team, x=inner_start_x + inner_size, y=inner_start_y + i * spacing))
                elif edge == 2:  # top
                    units.append(Knight(team=team, x=inner_start_x + i * spacing, y=inner_start_y))
                else:  # bottom
                    units.append(Knight(team=team, x=inner_start_x + i * spacing, y=inner_start_y + inner_size))
                knight_idx += 1

        # Crossbowmen in the hollow center
        center_x = start_x + square_size / 2
        center_y_pos = start_y + square_size / 2
        crossbow_radius = spacing * 2
        
        for i in range(num_crossbowmen):
            angle = (2 * 3.14159 * i) / num_crossbowmen
            x = center_x + crossbow_radius * math.cos(angle) * 0.5
            y = center_y_pos + crossbow_radius * math.sin(angle)
            units.append(Crossbowman(team=team, x=x, y=y))
        
        return units

    @staticmethod
    def _place_unit_block(unit_class, team: str, start_x: float, start_y: float,
                          col_spacing: float, row_spacing: float,
                          num_units: int, units_per_row: int, 
                          direction: int = 1) -> list:
        """
        Place a block of units in a grid pattern (legacy helper).
        """
        units = []
        for i in range(num_units):
            row = i // units_per_row
            col = i % units_per_row
            
            x = start_x + (row * row_spacing * direction)
            y = start_y + (col * col_spacing)
            
            unit = unit_class(team=team, x=x, y=y)
            units.append(unit)
        return units

    @staticmethod
    def _get_composition(units: list) -> dict:
        """Get unit type composition of a list of units."""
        comp = {'Knight': 0, 'Pikeman': 0, 'Crossbowman': 0}
        for u in units:
            if isinstance(u, Knight):
                comp['Knight'] += 1
            elif isinstance(u, Pikeman):
                comp['Pikeman'] += 1
            elif isinstance(u, Crossbowman):
                comp['Crossbowman'] += 1
        return comp

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


