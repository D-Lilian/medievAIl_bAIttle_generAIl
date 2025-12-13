import sys
import time

# --- 1. IMPORTS ---
try:
    from View.terminal_view import TerminalView, UniteRepr, Team, UnitStatus
    from Model.simulation import Simulation
    from Model.orders import OrderManager, MoveOrder
except ImportError as e:
    print(f"❌ ERREUR D'IMPORT : {e}")
    print("Vérifie que 'generals.py' et 'units.py' sont bien dans le dossier Model")
    print("Vérifie que 'terminal_view.py' est bien dans le dossier View")
    sys.exit(1)

# --- 2. CLASSE UNITÉ DE TEST ---
# Une unité compatible à la fois avec la Simulation et la Vue
class TestUnit:
    def __init__(self, x, y, team, type_name="Knight"):
        self.x = float(x)
        self.y = float(y)
        self.team = team      # "A" ou "B"
        self.unit_type = type_name
        self.name = type_name
        self.hp = 100
        self.hp_max = 100
        self.speed = 1.0
        self.size = 0.5
        self.sight = 10
        self.range = 1
        self.alive = True
        self.distance_moved = 0
        self.damage_dealt = 0
        self.armor = {}
        self.attack = {}
        self.accuracy = 1.0
        
        # Le plus important : le gestionnaire d'ordres pour generals.py
        self.order_manager = OrderManager()

    # Méthodes bouchons pour satisfaire simulation.py
    def can_attack(self): return True
    def perform_attack(self): pass
    def update_reload(self, dt): pass
    
    # Propriétés pour satisfaire terminal_view.py
    @property
    def status(self): return UnitStatus.ALIVE if self.hp > 0 else UnitStatus.DEAD
    @property
    def letter(self): return self.unit_type[0].upper()

# --- 3. SCÉNARIO DE TEST ---
class TestScenario:
    def __init__(self):
        self.size_x = 120
        self.size_y = 120
        self.units = []
        self.units_a = []
        self.units_b = []
        # Généraux vides pour éviter les erreurs
        self.general_a = type('G',(),{'BeginStrategy':lambda:None, 'CreateOrders':lambda:None, 'notify':lambda x:None})()
        self.general_b = type('G',(),{'HandleUnitTypeDepleted':lambda x:None, 'BeginStrategy':lambda:None, 'CreateOrders':lambda:None})()

# --- 4. LE PONT (ADAPTATEUR) ---
class SimulationBridge(Simulation):
    def __init__(self, scenario):
        super().__init__(scenario, tick_speed=60)
        # Hack pour que la Vue trouve les unités (sim.board.units)
        self.board = type('Board', (), {'units': self.scenario.units})()

    # Connexion Generals -> Simulation
    def move_unit_closest_to_xy(self, unit, x, y):
        return self.move_unit_towards_coordinates(unit, x, y)

    # Fonction step pour avancer pas à pas
    def step(self):
        # Exécution des ordres
        for unit in self.scenario.units:
            if hasattr(unit, 'order_manager'):
                for order in list(unit.order_manager):
                    fini = unit.order_manager.TryOrder(self, order)
                    if fini:
                        unit.order_manager.Remove(order)
                    break 
        self.tick += 1
        self.as_unit_moved = False

# --- 5. LANCEMENT ---
if __name__ == "__main__":
    # Setup
    scenario = TestScenario()
    
    
    
    chevalier = TestUnit(50, 50, "A", "Knight")
    scenario.units.append(chevalier)
    scenario.units_a.append(chevalier)
    
    # On lance la simu
    sim = SimulationBridge(scenario)
    
    # On donne l'ordre d'aller en (100, 100)
    print("🚀 Ordre donné : Aller en bas à droite")
    
    chevalier.order_manager.Add(MoveOrder(chevalier, 60, 60), 1)
    # On lance la vue
    view = TerminalView(120, 120, tick_speed=30)
    try:
        view.init_curses()
        running = True
        while running:
            if not view.paused:
                sim.step()
            running = view.update(sim)
    except Exception as e:
        view.cleanup()
        print(f"Erreur : {e}")
        import traceback
        traceback.print_exc()
    finally:
        view.cleanup()