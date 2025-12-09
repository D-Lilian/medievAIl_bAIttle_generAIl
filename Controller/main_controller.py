import sys
import os
import time

# Add parent directory to path to allow imports from Model and View
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Controller.ParseCLI import args
from Controller.TerminalViewController import TerminalViewController
from Model.Simulation import Simulation
from Model.Scenario import Scenario
from Model.Units import Knight, Pikeman, Crossbowman, UnitType, Team
from Model.generals import General
from Model.strategies import StrategyStart, StrategieDAFT, StrategieBrainDead, StrategieStartSomeIQ, StrategieSimpleAttackBestAvoidWorst

def create_default_scenario():
    """Create a default scenario with units and generals."""
    units = []
    units_a = []
    units_b = []
    
    # Team A (Blue) - Left side
    for i in range(5):
        u = Knight(Team.A, 20, 20 + i*5)
        units.append(u)
        units_a.append(u)
        
    for i in range(5):
        u = Pikeman(Team.A, 25, 20 + i*5)
        units.append(u)
        units_a.append(u)
        
    # Team B (Red) - Right side
    for i in range(5):
        u = Knight(Team.B, 100, 20 + i*5)
        units.append(u)
        units_b.append(u)
        
    for i in range(5):
        u = Pikeman(Team.B, 95, 20 + i*5)
        units.append(u)
        units_b.append(u)
        
    return units, units_a, units_b

def get_strategy_by_name(name):
    """Get strategies for a general by name.
    Returns: (StrategyStart, dict[UnitType, StrategyTroup])
    """
    if name.lower() == "daft":
        daft_strategy = StrategieDAFT(None)
        return StrategyStart(), {
            UnitType.KNIGHT: daft_strategy,
            UnitType.PIKEMAN: daft_strategy,
            UnitType.CROSSBOWMAN: daft_strategy
        }
    elif name.lower() == "braindead":
        braindead_strategy = StrategieBrainDead(None)
        return StrategyStart(), {
            UnitType.KNIGHT: braindead_strategy,
            UnitType.PIKEMAN: braindead_strategy,
            UnitType.CROSSBOWMAN: braindead_strategy
        }
    elif name.lower() == "someiq":
        return StrategieStartSomeIQ(), {
            UnitType.KNIGHT: StrategieSimpleAttackBestAvoidWorst(UnitType.CROSSBOWMAN, UnitType.PIKEMAN),
            UnitType.PIKEMAN: StrategieSimpleAttackBestAvoidWorst(UnitType.KNIGHT, UnitType.CROSSBOWMAN),
            UnitType.CROSSBOWMAN: StrategieSimpleAttackBestAvoidWorst(UnitType.PIKEMAN, UnitType.KNIGHT)
        }
    # Default
    daft_strategy = StrategieDAFT(None)
    return StrategyStart(), {
        UnitType.KNIGHT: daft_strategy,
        UnitType.PIKEMAN: daft_strategy,
        UnitType.CROSSBOWMAN: daft_strategy
    }

def main():
    if args.command == 'run':
        # Load scenario (ignoring name for now, using default)
        units, units_a, units_b = create_default_scenario()
        
        # Create generals
        sS_a, sT_a = get_strategy_by_name(args.ai1)
        sS_b, sT_b = get_strategy_by_name(args.ai2)
        
        gen_a = General(units_a, units_b, sS_a, sT_a)
        gen_b = General(units_b, units_a, sS_b, sT_b)
        
        # Create scenario
        scenario = Scenario(
            units=units,
            units_a=units_a,
            units_b=units_b,
            general_a=gen_a,
            general_b=gen_b,
            size_x=120,
            size_y=120
        )
        
        # Run with or without terminal view
        if args.t:
            controller = TerminalViewController(scenario, 120, 120, tick_speed=args.t)
            controller.run_interactive()
        else:
            # Headless run
            sim = Simulation(scenario, tick_speed=20)
            sim.simulate()

if __name__ == "__main__":
    main()
