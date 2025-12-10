from ParseCLI import args
from Model.scenarios.Scenario import Scenario
from Controller.SimulationController import SimulationController
# importer le cotroleur de lilian


def run(args):
    print(f"Running scenario: {args.scenario} with AIs: {args.ai1} vs {args.ai2}")
    # Appel de la fonction correspondant
    if args.t == "None":
        print("No terminal view selected.")
        scenario = Scenario(
            units= #je ne sais pas qce qu'il a mis pour les unités
            units_a=50,
            units_b=50,
            general_a=args.ai1,
            general_b=args.ai2,
            size_x=120,
            size_y=120
        )
        start_simulation(self,args.scenario):

        # appeler le controleur en unlocked mode
    elif args.t == "-t":
        print("Terminal view enabled.")

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

def main():


    eval(f"{args.command}(args)", {'__builtins__': None})