import sys
import os
import time

# Add parent directory to path to allow imports from Model and View
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Controller.ParseCLI import args
from Model.Simulation import Simulation
from Model.Units import Knight, Pikeman, Crossbowman, UnitType
from Model.generals import General
from Model.strategies import StrategyStart, StrategieDAFT, StrategieBrainDead, StrategieStartSomeIQ, StrategieSimpleAttackBestAvoidWorst
from View.terminal_view import TerminalView

def create_default_scenario():
    units = []
    units_a = []
    units_b = []
    
    # Team A (Blue) - Left side
    for i in range(5):
        u = Knight(1, 20, 20 + i*5)
        units.append(u)
        units_a.append(u)
        
    for i in range(5):
        u = Pikeman(1, 25, 20 + i*5)
        units.append(u)
        units_a.append(u)
        
    # Team B (Red) - Right side
    for i in range(5):
        u = Knight(2, 100, 20 + i*5)
        units.append(u)
        units_b.append(u)
        
    for i in range(5):
        u = Pikeman(2, 95, 20 + i*5)
        units.append(u)
        units_b.append(u)
        
    return units, units_a, units_b

def get_strategy_by_name(name):
    # Simple mapping
    if name.lower() == "daft":
        return StrategyStart(), StrategieDAFT(None)
    elif name.lower() == "braindead":
        return StrategyStart(), StrategieBrainDead(None)
    elif name.lower() == "someiq":
        return StrategieStartSomeIQ(), StrategieSimpleAttackBestAvoidWorst()
    # Default
    return StrategyStart(), StrategieDAFT(None)

def main():
    if args.command == 'run':
        # Load scenario (ignoring name for now, using default)
        units, units_a, units_b = create_default_scenario()
        
        # Create generals
        sS_a, sT_a = get_strategy_by_name(args.ai1)
        sS_b, sT_b = get_strategy_by_name(args.ai2)
        
        gen_a = General(units_a, units_b, sS_a, sT_a)
        gen_b = General(units_b, units_a, sS_b, sT_b)
        
        # Initialize simulation
        sim = Simulation(units, units_a, gen_a, units_b, gen_b, tickSpeed=20, size_x=120, size_y=120)
        
        # Initialize view if requested
        if args.t:
            view = TerminalView(120, 120, tick_speed=args.t)
            try:
                view.init_curses()
                running = True
                while running:
                    if not view.paused:
                        # Use the monkey-patched step from TerminalView
                        if hasattr(sim, 'step'):
                            sim.step()
                        else:
                            # Fallback or error
                            print("Error: Simulation has no step method")
                            break
                    
                    running = view.update(sim)
            except KeyboardInterrupt:
                pass
            finally:
                # Ensure curses is cleaned up if view.update didn't do it (it usually does on exit)
                pass
        else:
            # Headless run
            sim.simulate()

if __name__ == "__main__":
    main()
