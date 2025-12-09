"""
Scenario - Represents a battle scenario with units and generals.
"""

from Model.Units import Unit
from typing import List


class Scenario:
    """
    A battle scenario containing units, generals, and battlefield configuration.
    """
    
    def __init__(self, units: List[Unit], units_a: List[Unit], units_b: List[Unit],
                 general_a, general_b, size_x: int = 120, size_y: int = 120):
        """
        Initialize a battle scenario.
        
        Args:
            units: All units in the battle
            units_a: Units belonging to team A
            units_b: Units belonging to team B
            general_a: General commanding team A
            general_b: General commanding team B
            size_x: Battlefield width
            size_y: Battlefield height
        """
        self.units = units
        self.units_a = units_a
        self.units_b = units_b
        self.general_a = general_a
        self.general_b = general_b
        self.size_x = size_x
        self.size_y = size_y
