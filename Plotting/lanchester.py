# -*- coding: utf-8 -*-
"""
@file lanchester_scenario.py
@brief Lanchester Scenario - Creates scenarios for testing Lanchester's Laws

@details
Generates scenarios where N units fight against 2*N units of the same type.
Used to test and visualize Lanchester's Laws (Linear vs Square Law).

Lanchester's Laws:
- Linear Law: Losses proportional to N (applies to melee combat)
- Square Law: Losses proportional to N² (applies to ranged combat)

"""

from Model.scenario import Scenario
from Model.units import Knight, Crossbowman, Pikeman


class LanchesterScenario:
    """
    Factory for creating Lanchester test scenarios.
    
    Creates asymmetric battles where N units face 2*N units of the same type,
    positioned within range for immediate engagement.
    """
    
    # Mapping of unit type names to unit classes
    UNIT_CLASSES = {
        'Knight': Knight,
        'Crossbowman': Crossbowman, 
        'Crossbow': Crossbowman,
        'Pikeman': Pikeman,
        'Melee': Knight,       # Default melee type
        'Archer': Crossbowman,  # Default ranged type
    }
    
    @staticmethod
    def create(unit_type: str, n: int, size_x: int = 120, size_y: int = 120) -> Scenario:
        """
        Create a Lanchester scenario: N units (Team A) vs 2*N units (Team B).
        
        @param unit_type: Type of units ('Knight', 'Crossbowman', 'Pikeman', 'Melee', 'Archer')
        @param n: Base number of units for Team A (Team B gets 2*n)
        @param size_x: Battlefield width
        @param size_y: Battlefield height
        @return: Scenario ready for simulation
        """
        if unit_type not in LanchesterScenario.UNIT_CLASSES:
            raise ValueError(f"Unknown unit type: {unit_type}. Available: {list(LanchesterScenario.UNIT_CLASSES.keys())}")
        
        unit_class = LanchesterScenario.UNIT_CLASSES[unit_type]
        
        # Determine engagement distance based on unit type
        # Ranged units need to be within range, melee units need to be close
        is_ranged = unit_class in [Crossbowman]
        engagement_distance = 4 if is_ranged else 3  # Within attack range
        
        # Position teams facing each other at center
        center_y = size_y // 2
        team_a_x = (size_x // 2) - engagement_distance
        team_b_x = (size_x // 2) + engagement_distance
        
        # Create units with appropriate spacing
        units_a = LanchesterScenario._create_formation(
            unit_class, 'A', n, team_a_x, center_y, size_y
        )
        units_b = LanchesterScenario._create_formation(
            unit_class, 'B', 2 * n, team_b_x, center_y, size_y
        )
        
        all_units = units_a + units_b
        
        return Scenario(
            units=all_units,
            units_a=units_a,
            units_b=units_b,
            general_a=None,
            general_b=None,
            size_x=size_x,
            size_y=size_y
        )
    
    @staticmethod
    def _create_formation(unit_class, team: str, count: int, 
                          x_pos: float, center_y: float, map_height: int) -> list:
        """
        Create a line formation of units.
        
        @param unit_class: Class to instantiate (Knight, Crossbowman, etc.)
        @param team: Team identifier ('A' or 'B')
        @param count: Number of units to create
        @param x_pos: X position for the formation
        @param center_y: Center Y position
        @param map_height: Height of the map for spacing calculation
        @return: List of unit instances
        """
        units = []
        spacing = min(2.5, (map_height - 20) / max(count, 1))
        start_y = max(5, center_y - (count * spacing) / 2)
        
        for i in range(count):
            y = start_y + i * spacing
            # Clamp Y to stay within map bounds
            y = max(2, min(y, map_height - 2))
            unit = unit_class(team=team, x=x_pos, y=y)
            units.append(unit)
        
        return units


# Convenience function for CLI integration
def Lanchester(unit_type: str, n: int) -> Scenario:
    """
    Create a Lanchester scenario for testing Lanchester's Laws.
    
    @param unit_type: Type of units ('Knight', 'Crossbowman', 'Melee', 'Archer')
    @param n: Base number of units (Team A=N, Team B=2*N)
    @return: Configured Scenario
    """
    return LanchesterScenario.create(unit_type, n)
