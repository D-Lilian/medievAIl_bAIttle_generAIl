import sys
import random
import time


try:
    from Controller.simulation_controller import SimulationController
    from Model.scenario import Scenario
    from Model.units import Unit, Knight, Pikeman, Crossbowman, UnitType
    from Model.generals import General
    from Model.strategies import StrategieDAFT, StrategieKnightSomeIQ, StrategiePikemanSomeIQ, StrategieCrossbowmanSomeIQ
    from View.pygame_view import PygameView
   
    from Utils.logs import setup_logger
    setup_logger(level="WARNING", modules=[])

except ImportError as e:
    print(f"erreur {e}")
    sys.exit(1)

# --- 4. MAIN ---
def main():
    print("Lancement du mode GRAPHIQUE")

    # Configuration
    tick_speed = 30
    
    # CRÉATION DE LA VUE (Petite fenêtre 800x600)
    view = PygameView(scenario, simulation_controller, width=800, height=600)


if __name__ == "__main__":
    main()