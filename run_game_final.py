import sys
import random
import time

# --- 1. IMPORTS ---
try:
    # Modèle (Logique)
    from Model.Simulation import Simulation
    from Model.Scenario import Scenario
    from Model.Units import Unit, Knight, Pikeman, Crossbowman, UnitType
    from Model.generals import General
    from Model.Strategies import StrategieDAFT, StrategieKnightSomeIQ, StrategiePikemanSomeIQ, StrategieCrossbowmanSomeIQ
    
    # Vue (Uniquement Graphique)
    try:
        from View.pygame_view import PygameView
    except ImportError:
        print("❌ ERREUR : La bibliothèque 'pygame' n'est pas installée.")
        print("Installez-la avec : pip install pygame")
        sys.exit(1)

    # Logs (Silencieux)
    from Utils.logs import setup_logger
    setup_logger(level="WARNING", modules=[])

except ImportError as e:
    print(f"❌ ERREUR D'IMPORT CRITIQUE : {e}")
    sys.exit(1)


# --- 2. LE MOTEUR DE JEU ---
class SimulationRunner(Simulation):
    def __init__(self, scenario, tick_speed):
        super().__init__(scenario, tick_speed=tick_speed)
        self.board = type('Board', (), {'units': self.scenario.units})()

    def step(self):
        """Logique d'un tour de jeu"""
        # Stratégie
        self.scenario.general_a.CreateOrders()
        self.scenario.general_b.CreateOrders()

        # Ordres
        units_list = list(self.scenario.units)
        random.shuffle(units_list)

        for unit in units_list:
            if unit.hp <= 0: continue
            
            # FIX CRITIQUE DU MOUVEMENT
            self.as_unit_moved = False  

            if hasattr(unit, 'order_manager'):
                for order in list(unit.order_manager):
                    try:
                        finished = unit.order_manager.TryOrder(self, order)
                        if finished:
                            unit.order_manager.Remove(order)
                        break 
                    except Exception:
                        pass 

        # Physique
        self.tick += 1
        for unit in self.scenario.units:
            if unit.hp > 0:
                unit.update_reload(1.0 / self.tick_speed)
        self.as_unit_moved = False


# --- 3. CONFIGURATION ---
def setup_battle():
    """Prépare les armées"""
    units_a = []
    units_b = []

    # ÉQUIPE A (Cyan - Stratège)
    for i in range(5): units_a.append(Knight("A", 20, 20 + i*10))
    for i in range(5): units_a.append(Pikeman("A", 25, 30 + i*8))
    for i in range(5): units_a.append(Crossbowman("A", 15, 30 + i*8))

    # ÉQUIPE B (Rouge - Bourrin)
    for i in range(8): units_b.append(Pikeman("B", 100, 20 + i*6))
    for i in range(5): units_b.append(Knight("B", 90, 30 + i*8))
    for i in range(3): units_b.append(Crossbowman("B", 110, 40 + i*5))

    all_units = units_a + units_b

    # GÉNÉRAUX
    strat_smart = {
        UnitType.KNIGHT: StrategieKnightSomeIQ(),
        UnitType.PIKEMAN: StrategiePikemanSomeIQ(),
        UnitType.CROSSBOWMAN: StrategieCrossbowmanSomeIQ()
    }
    gen_a = General(units_a, units_b, None, strat_smart)

    strat_dumb = {
        UnitType.KNIGHT: StrategieDAFT(None),
        UnitType.PIKEMAN: StrategieDAFT(None),
        UnitType.CROSSBOWMAN: StrategieDAFT(None)
    }
    gen_b = General(units_b, units_a, None, strat_dumb)

    gen_a.BeginStrategy()
    gen_b.BeginStrategy()

    return Scenario(all_units, units_a, units_b, gen_a, gen_b)


# --- 4. MAIN ---
def main():
    print("🚀 Lancement du mode GRAPHIQUE direct...")

    # Configuration
    tick_speed = 30 
    scenario = setup_battle()
    sim = SimulationRunner(scenario, tick_speed)
    
    # CRÉATION DE LA VUE (Petite fenêtre 800x600)
    # Le fichier View/pygame_view.py s'occupera de la mettre au premier plan
    view = PygameView(sim, width=800, height=600)

    # Boucle de jeu
    try:
        running = True
        while running:
            if not view.paused:
                sim.step()
            
            # Mise à jour graphique
            running = view.update(sim)
            
            # Fin de partie
            alive_a = len([u for u in scenario.units_a if u.hp > 0])
            alive_b = len([u for u in scenario.units_b if u.hp > 0])
            if alive_a == 0 or alive_b == 0:
                pass 

    except KeyboardInterrupt:
        pass
    except Exception as e:
        if view: view.cleanup()
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
    finally:
        if view: view.cleanup()
        print("Fin de la simulation.")

if __name__ == "__main__":
    main()