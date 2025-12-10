from ParseCLI import args
from Model.scenarios.Scenario import Scenario
from Controller.SimulationController import SimulationController
# importer le cotroleur de lilian
from Controller.simulation_controller import *

def run(args):
    print(f"Running scenario: {args.scenario} with AIs: {args.ai1} vs {args.ai2}")
    # Appel de la fonction correspondant
    if args.t == "None":
        print("No terminal view selected.")
        game = Scenario(
            units= #je ne sais pas qce qu'il a mis pour les unités
            units_a=50,
            units_b=50,
            general_a=args.ai1,
            general_b=args.ai2,
            size_x=120,
            size_y=120
        )
        start_simulation(game)


        # appeler le controleur en unlocked mode
    elif args.t == "-t":
        print("Terminal view enabled.")
        from Controller.terminal_controller import TerminalController
        from Model.scenario import Scenario
        from Model.units import Knight, Pikeman, Team

        units, units_a, units_b = [], [], []
        u1 = Knight(Team.A, 20, 20);
        units.append(u1);
        units_a.append(u1)
        u2 = Pikeman(Team.B, 95, 20);
        units.append(u2);
        units_b.append(u2)

        scenario = Scenario(units, units_a, units_b, None, None, size_x=120, size_y=40)
        controller = TerminalController(scenario, tick_speed=20)
        controller.run()

        # appeler le controleur sans unlocked mode



def tourney(args):
    print(f"Running tournament: {args.ais} on scenarios: {args.scenarios} for {args.N} rounds")
    # Appel de la fonction correspondant
 #pas d ecran terminal


def load(args):

    # Appel de la fonction correspondant voir avec jp

def save(args):

    # Appel de la fonction correspondant voir avec jp

def Lanchester(args):
    #pas d ecran terminal
    scenario = Scenario(
        units=  # je ne sais pas qce qu'il a mis pour les unités
        units_a = 50,
    units_b = 50,
    general_a = args.ai1,
    general_b = args.ai2,
    size_x = 120,
    size_y = 120
    )
def main():


    eval(f"{args.command}(args)", {'__builtins__': None})