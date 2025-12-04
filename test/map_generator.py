import math
import random
from unit import Crossbowman, Knight, Pikeman
from scenario import Scenario


class MapGenerator:

    @staticmethod
    def generate_scenario(width, height, count_per_team, formation='square'):

        units_a = []
        units_b = []
        all_units = []

        center_x = width // 2  
        start_y_a = 15  

        # positions pour Team A
        positions_a = MapGenerator.get_positions(count_per_team, center_x, start_y_a, formation, is_left=True)

        # Miroir pour avoir team B
        for (ax, ay) in positions_a:
            u_class = random.choice([Crossbowman, Knight, Pikeman])

            unit_a = u_class(team="A", x=ax, y=ay)
            units_a.append(unit_a)
            all_units.append(unit_a)

            bx = ax
            by = height - ay

            unit_b = u_class(team="B", x=bx, y=by)
            units_b.append(unit_b)
            all_units.append(unit_b)

        return Scenario(
            units=all_units,
            units_a=units_a,
            units_b=units_b,
            general_a=None,
            general_b=None,
            size_x=width,
            size_y=height
        )

    @staticmethod
    def get_positions(count, start_x, start_y, formation, is_left):
        positions = []
        spacing = 3

        if formation == 'line':
            length = (count - 1) * spacing
            top_x = start_x - (length / 2)
            for i in range(count):
                positions.append((top_x + i * spacing, start_y))

        else:
            side = math.ceil(math.sqrt(count))

            square_height = (side - 1) * spacing
            top_x = start_x - (square_height / 2)

            created = 0
            for col in range(side):
                for row in range(side):
                    if created >= count: break

                    x = top_x + row * spacing
                    if is_left:
                        y = start_y + col * spacing
                    else:
                        y = start_y - col * spacing

                    positions.append((x, y))
                    created += 1
        return positions