# -*- coding: utf-8 -*-
"""
@file lanchester.py
@brief Lanchester Scenario Factory for Testing Lanchester's Laws

@details
Creates N vs 2N battle scenarios to test Lanchester's Laws:

- Linear Law (Melee): Casualties ∝ N, one-on-one combat
- Square Law (Ranged): Casualties ∝ N², focus fire possible

Usage:
    from Plotting.lanchester import LanchesterScenario, Lanchester
    
    scenario = Lanchester("Knight", 20)  # 20 vs 40 Knights
    scenario = LanchesterScenario.create("Crossbowman", 30)
"""

from Model.scenario import Scenario
from Model.units import Knight, Crossbowman, Pikeman


# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

# Map size limits
MAP_SIZE_MIN = 50
MAP_SIZE_MAX = 200
MAP_SIZE_BASE = 40  # Base size before scaling with units

# Unit positioning
ENGAGEMENT_GAP = 6  # Horizontal distance between teams (units engage quickly)
MARGIN = 5  # Distance from map edges
UNIT_SPACING_MAX = 2.0  # Maximum vertical spacing between units

# Performance limits
MAX_UNITS_PER_TEAM = 500  # Maximum N value (performance concern)


# =============================================================================
# UNIT TYPE REGISTRY
# =============================================================================

UNIT_TYPES = {
    'Knight': Knight,
    'Crossbowman': Crossbowman,
    'Crossbow': Crossbowman,
    'Pikeman': Pikeman,
    'Melee': Knight,
    'Ranged': Crossbowman,
    'Archer': Crossbowman,
}


class LanchesterScenario:
    """
    Factory for N vs 2N Lanchester test scenarios.
    
    Units are positioned in line formations facing each other,
    close enough for immediate engagement.
    """
    
    @staticmethod
    def get_supported_types() -> list:
        """Return list of supported unit type names."""
        return list(UNIT_TYPES.keys())
    
    @staticmethod
    def create(unit_type: str, n: int) -> Scenario:
        """
        Create a Lanchester scenario: N units (A) vs 2N units (B).
        
        @param unit_type: Unit type name (Knight, Crossbowman, Pikeman, etc.)
        @param n: Base unit count for Team A (Team B gets 2*n)
        @return: Scenario ready for simulation
        @raises ValueError: If unit_type is unknown or n is invalid
        @raises TypeError: If n is not an integer
        """
        # Validate unit type
        if unit_type not in UNIT_TYPES:
            available = ', '.join(UNIT_TYPES.keys())
            raise ValueError(f"Unknown unit type: '{unit_type}'. Available: {available}")
        
        # Validate unit count
        if not isinstance(n, int):
            raise TypeError(f"Unit count must be integer, got {type(n).__name__}")
        
        if n <= 0:
            raise ValueError(f"Unit count must be positive, got {n}")
        
        if n > MAX_UNITS_PER_TEAM:
            raise ValueError(f"Unit count {n} exceeds max {MAX_UNITS_PER_TEAM} (performance concern)")
        
        unit_class = UNIT_TYPES[unit_type]
        
        # Map size scales with unit count
        total_units = 3 * n  # N + 2N
        map_size = min(MAP_SIZE_MAX, max(MAP_SIZE_MIN, MAP_SIZE_BASE + total_units // 2))
        
        # Teams face each other in the center
        center_x = map_size // 2
        center_y = map_size // 2
        
        team_a_x = center_x - ENGAGEMENT_GAP // 2
        team_b_x = center_x + ENGAGEMENT_GAP // 2
        
        # Create line formations
        units_a = LanchesterScenario._create_line(
            unit_class, 'A', n, team_a_x, center_y, map_size
        )
        units_b = LanchesterScenario._create_line(
            unit_class, 'B', 2 * n, team_b_x, center_y, map_size
        )
        
        return Scenario(
            units=units_a + units_b,
            units_a=units_a,
            units_b=units_b,
            general_a=None,
            general_b=None,
            size_x=map_size,
            size_y=map_size
        )
    
    @staticmethod
    def _create_line(unit_class, team: str, count: int,
                     x: float, center_y: float, map_size: int) -> list:
        """
        Create a vertical line formation of units.
        
        @param unit_class: Unit class to instantiate
        @param team: 'A' or 'B'
        @param count: Number of units
        @param x: X position for all units
        @param center_y: Center Y position
        @param map_size: Map height for bounds checking
        @return: List of unit instances
        """
        units = []
        
        # Calculate spacing to fit all units
        available_height = map_size - 2 * MARGIN
        spacing = min(UNIT_SPACING_MAX, available_height / max(count, 1))
        
        # Start position to center the formation
        total_height = (count - 1) * spacing
        start_y = center_y - total_height / 2
        
        for i in range(count):
            y = start_y + i * spacing
            # Clamp to map bounds
            y = max(MARGIN, min(y, map_size - MARGIN))
            
            unit = unit_class(team=team, x=x, y=y)
            units.append(unit)
        
        return units


def Lanchester(unit_type: str, n: int) -> Scenario:
    """
    Convenience function to create a Lanchester scenario.
    
    @param unit_type: Type of units (Knight, Crossbowman, Pikeman)
    @param n: Base count for Team A (Team B = 2*n)
    @return: Configured Scenario
    
    Example:
        scenario = Lanchester("Knight", 20)  # 20 Knights vs 40 Knights
    """
    return LanchesterScenario.create(unit_type, n)
