# Exemple minimal : récupérer 'scenario' depuis ParseCLI et appeler une fonction via eval()
# Utilisation :
#   python .\eval.py run scenario_example dummyAI1 dummyAI2
# Ici 'scenario_example' est à la fois le nom du scénario et le nom de la fonction à appeler.

from ParseCLI import args

# pattern de dispatch minimal en Python

def run(args):
    print(f"Running scenario: {args.scenario} with AIs: {args.ai1} vs {args.ai2}")
    # Appel de la fonction correspondant
    if args.t == "None":
        print("No terminal view selected.")
        # appeler le controleur en unlocked mode
    elif args.t == "-t":
        print("Terminal view enabled.")
        # appeler le controleur sans unlocked mode



def tourney(args):
    print(f"Running tournament: {args.ais} on scenarios: {args.scenarios} for {args.N} rounds")
    # Appel de la fonction correspondant
 #pas d ecran terminal


def load(args):

    # Appel de la fonction correspondant

def save(args):

    # Appel de la fonction correspondant

def Lanchester(args):
    #pas d ecran terminal

def main():

eval(f"{args.command}(args)", {'__builtins__': None})