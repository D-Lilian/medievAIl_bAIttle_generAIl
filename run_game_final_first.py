import sys
import random
import time

# --- 1. IMPORTS ---
try:
    from View.terminal_view import TerminalView
    from Model.Simulation import Simulation
    from Model.Scenario import Scenario
    from Model.Units import Unit, Knight, Pikeman, Crossbowman, UnitType
    from Model.generals import General
    
    # ON IMPORTE TOUTES LES STRATÉGIES
    from Model.Strategies import (
        StrategieDAFT, 
        StrategieBrainDead,
        StrategieKnightSomeIQ, 
        StrategiePikemanSomeIQ, 
        StrategieCrossbowmanSomeIQ
    )
    
    from Utils.logs import setup_logger
    setup_logger(level="WARNING", modules=[])

except ImportError as e:
    print(f"❌ ERREUR D'IMPORT : {e}")
    sys.exit(1)


# --- 2. MOTEUR DE JEU (Toujours avec le correctif de mouvement) ---
class SimulationRunner(Simulation):
    def __init__(self, scenario, tick_speed):
        super().__init__(scenario, tick_speed=tick_speed)
        self.board = type('Board', (), {'units': self.scenario.units})()

    def step(self):
        """Avance d'un tour"""
        self.scenario.general_a.CreateOrders()
        self.scenario.general_b.CreateOrders()

        units_list = list(self.scenario.units)
        random.shuffle(units_list)

        for unit in units_list:
            if unit.hp <= 0: continue
            
            # --- DÉBLOCAGE DU MOUVEMENT ---
            self.as_unit_moved = False  
            # ------------------------------

            if hasattr(unit, 'order_manager'):
                for order in list(unit.order_manager):
                    try:
                        finished = unit.order_manager.TryOrder(self, order)
                        if finished:
                            unit.order_manager.Remove(order)
                        break
                    except Exception:
                        pass

        self.tick += 1
        for unit in self.scenario.units:
            if unit.hp > 0:
                unit.update_reload(1.0 / self.tick_speed)
        self.as_unit_moved = False


# --- 3. LANCEMENT DU DUEL ---
def main():
    print("🧠 DUEL : INTELLIGENCE vs BRUTALITÉ 🦍")

    # --- PARAMÈTRES ---
    VITESSE_JEU = 20  # Un peu plus rapide pour le combat
    
    # --- ARMÉES ---
    units_a = []
    units_b = []

    # ÉQUIPE A (Cyan - INTELLIGENTE) : Composition tactique
    # Ils sont placés à GAUCHE (x=20)
    for i in range(4): units_a.append(Knight("A", 20, 20 + i*10))      # Flanc de cavalerie
    for i in range(4): units_a.append(Pikeman("A", 25, 30 + i*8))      # Garde du corps
    for i in range(4): units_a.append(Crossbowman("A", 15, 30 + i*8))  # Tireurs derrière

    # ÉQUIPE B (Rouge - BRUTALE) : Horde mélangée
    # Ils sont placés à DROITE (x=100)
    for i in range(5): units_b.append(Knight("B", 100, 20 + i*8))
    for i in range(5): units_b.append(Pikeman("B", 105, 20 + i*8))
    for i in range(2): units_b.append(Crossbowman("B", 110, 40 + i*5))

    all_units = units_a + units_b

    # --- GÉNÉRAUX ---
    
    # GÉNÉRAL A : STRATÉGIE "SomeIQ" (Spécifique par unité)
    # Knight -> Attaque Crossbowman en priorité
    # Pikeman -> Reste près des Crossbowman ou attaque Knight
    # Crossbowman -> Evite les Knight
    strat_map_smart = {
        UnitType.KNIGHT: StrategieKnightSomeIQ(),
        UnitType.PIKEMAN: StrategiePikemanSomeIQ(),
        UnitType.CROSSBOWMAN: StrategieCrossbowmanSomeIQ()
    }
    gen_a = General(units_a, units_b, None, strat_map_smart)

    # GÉNÉRAL B : STRATÉGIE "DAFT" (Fonce dans le tas)
    strat_map_dumb = {
        UnitType.KNIGHT: StrategieDAFT(None),
        UnitType.PIKEMAN: StrategieDAFT(None),
        UnitType.CROSSBOWMAN: StrategieDAFT(None)
    }
    gen_b = General(units_b, units_a, None, strat_map_dumb)

    # Démarrage
    gen_a.BeginStrategy()
    gen_b.BeginStrategy()

    scenario = Scenario(all_units, units_a, units_b, gen_a, gen_b)
    sim = SimulationRunner(scenario, tick_speed=VITESSE_JEU)

    # --- VUE ---
    view = TerminalView(120, 120, tick_speed=VITESSE_JEU)
    view.auto_follow = True 
    
    try:
        view.init_curses()
        running = True
        
        while running:
            if not view.paused:
                sim.step()
            
            running = view.update(sim)
            
            alive_a = len([u for u in units_a if u.hp > 0])
            alive_b = len([u for u in units_b if u.hp > 0])
            
            if alive_a == 0 or alive_b == 0:
                pass

    except Exception as e:
        view.cleanup()
        print(f"CRASH : {e}")
        import traceback
        traceback.print_exc()
    finally:
        view.cleanup()
        print("\n=== RÉSULTATS DU DUEL ===")
        print(f"Survivants Équipe A (SomeIQ) : {len([u for u in units_a if u.hp > 0])}")
        print(f"Survivants Équipe B (DAFT)   : {len([u for u in units_b if u.hp > 0])}")
        
        if len([u for u in units_a if u.hp > 0]) > len([u for u in units_b if u.hp > 0]):
            print("🏆 VICTOIRE DE L'INTELLIGENCE !")
        else:
            print("💪 VICTOIRE DE LA BRUTALITÉ !")

if __name__ == "__main__":
    main()