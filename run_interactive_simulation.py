import sys
import os

# Add workspace root to path
sys.path.append(os.getcwd())

from Utils.predefined_scenarios import PredefinedScenarios
from Controller.simulation_controller import SimulationController
from Controller.terminal_controller import TerminalController
from Model.generals import General
from Model.strategies import StrategyTroup
from Model.units import UnitType
from Model.orders import AttackNearestTroupOmniscient

# Define a strategy that works regardless of sight range for testing purposes
class StrategieOmniscient(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, UnitType.ALL, UnitType.NONE)

    def apply_order(self, general, unit):
        # Attack nearest enemy regardless of sight
        unit.order_manager.Add(AttackNearestTroupOmniscient(unit, self.favoriteTroup), 0)

def main():
    # 1. Setup Scenario with predefined battle
    print("Generating scenario...")
    scenario = PredefinedScenarios.classic_medieval_battle()
    
    # 2. Setup Generals if not already defined in scenario
    if scenario.general_a is None or scenario.general_b is None:
        # Create strategy maps for units (uses omniscient AI for immediate engagement)
        strat_map_a = {
            UnitType.PIKEMAN: StrategieOmniscient(None),
            UnitType.CROSSBOWMAN: StrategieOmniscient(None),
            UnitType.KNIGHT: StrategieOmniscient(None),
            UnitType.LONGSWORDSMAN: StrategieOmniscient(None),
            UnitType.ELITESKIRMISHER: StrategieOmniscient(None),
        }
        strat_map_b = strat_map_a.copy()

        # Create generals for both teams
        scenario.general_a = General(scenario.units_a, scenario.units_b, None, strat_map_a)
        scenario.general_b = General(scenario.units_b, scenario.units_a, None, strat_map_b)
    # 3. Initialize Controller
    print("Initializing simulation...")
    sim_controller = SimulationController()
    # Start paused so user can see the initial state
    # tick_speed: iterations per second (lower = slower)
    # Use higher tick_speed to smooth movement (reduce apparent teleporting)
    sim_controller.initialize_simulation(scenario, tick_speed=5, paused=True, unlocked=True)

    # 4. Start Simulation Loop (background thread)
    sim_controller.start_simulation()

    # 5. Run Terminal View with Controller
    try:
        terminal_controller = TerminalController(sim_controller, scenario)
        terminal_controller.run()
    except KeyboardInterrupt:
        print("Simulation interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return
    finally:
        print("Simulation ended.")

if __name__ == "__main__":
    # Set environment variable to avoid delay in ESC key
    os.environ.setdefault('ESCDELAY', '25')
    main()
