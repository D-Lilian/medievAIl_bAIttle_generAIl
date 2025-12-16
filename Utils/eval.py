from datetime import datetime
from Utils.parse_cli import args
from Controller.terminal_controller import TerminalController
from Controller.simulation_controller import SimulationController
from Controller.tournament_controller import TournamentController
from Controller.plot_controller import PlotController
from Model.scenario import Scenario
from Model.units import Knight, Pikeman, Team
from Utils.map_generator import MapGenerator
from Utils.predefined_scenarios import PredefinedScenarios

# Fabrique d'IA: à partir d'un nom, créer un General avec les stratégies correspondantes
from Model.generals import General
from Model.strategies import (
    StrategieBrainDead,
    StrategieDAFT,
    StrategieCrossbowmanSomeIQ,
    StrategieKnightSomeIQ,
    StrategiePikemanSomeIQ,
    StrategieStartSomeIQ,
)
from Model.units import UnitType


def create_general(name: str, unitsA, unitsB) -> General:
    name_up = name.upper()
    if name_up == "BRAINDEAD":
        sT = {
            UnitType.CROSSBOWMAN: StrategieBrainDead(None),
            UnitType.KNIGHT: StrategieBrainDead(None),
            UnitType.PIKEMAN: StrategieBrainDead(None),
        }
        return General(unitsA=unitsA, unitsB=unitsB, sS=None, sT=sT)
    elif name_up == "DAFT":
        sT = {
            UnitType.CROSSBOWMAN: StrategieDAFT(None),
            UnitType.KNIGHT: StrategieDAFT(None),
            UnitType.PIKEMAN: StrategieDAFT(None),
        }
        return General(unitsA=unitsA, unitsB=unitsB, sS=None, sT=sT)
    elif name_up == "SOMEIQ":
        sT = {
            UnitType.CROSSBOWMAN: StrategieCrossbowmanSomeIQ(),
            UnitType.KNIGHT: StrategieKnightSomeIQ(),
            UnitType.PIKEMAN: StrategiePikemanSomeIQ(),
        }
        sS = StrategieStartSomeIQ()
        return General(unitsA=unitsA, unitsB=unitsB, sS=sS, sT=sT)
    else:
        raise ValueError(f"Nom d'IA inconnu ")


def run(args):
    print(f"Running scenario: {args.scenario} with AIs: {args.ai1} vs {args.ai2}")
    # Préparer la sélection du scénario en dehors des branches terminal/non-terminal
    scenario_map = {
        "classical_medieval_battle": PredefinedScenarios.classic_medieval_battle,
        "defensive_siege": PredefinedScenarios.defensive_siege,
        "cavalry_charge": PredefinedScenarios.cavalry_charge,
        "cannae_envelopment": PredefinedScenarios.cannae_envelopment,
        "british_square": PredefinedScenarios.british_square,
    }
    requested = getattr(args, "scenario", None)
    if requested and requested in scenario_map:
        selected_scenario = scenario_map[requested]()
    else:
        # défaut: scénario classique
        selected_scenario = PredefinedScenarios.classic_medieval_battle()

    # Les unités du scénario sélectionné (communes aux deux branches)
    all_units = selected_scenario.units
    team_a_units = selected_scenario.units_a
    team_b_units = selected_scenario.units_b

    if not args.t:
        print("No terminal view selected.")
        # Créer les deux généraux selon les noms fournis
        ai1 = create_general(args.ai1, team_a_units, team_b_units)
        ai2 = create_general(args.ai2, team_b_units, team_a_units)
        # Construire le Scenario pour la simulation
        game = Scenario(
            units=all_units,
            units_a=team_a_units,
            units_b=team_b_units,
            general_a=ai1,
            general_b=ai2,
            size_x=120,
            size_y=120,
        )
        # Exécuter la simulation ici seulement (branche sans terminal)
        SimulationController.start_simulation(game)

    else:
        print("Terminal view enabled.")
        # Laisser la partie Terminal intacte (utilisation existante)
        ai1 = create_general(args.ai1, team_a_units, team_b_units)
        ai2 = create_general(args.ai2, team_b_units, team_a_units)
        # Construire le Scenario pour la simulation
        game2 = Scenario(
            units=all_units,
            units_a=team_a_units,
            units_b=team_b_units,
            general_a=ai1,
            general_b=ai2,
            size_x=120,
            size_y=120,
        )
        simulationController = SimulationController()
        controller = TerminalController(game2, simulationController)
        controller.run()
        simulationController.start_simulation(game2)


def tourney(args):
    """Run a tournament between AI generals. Delegates to TournamentController."""
    report_path = TournamentController.run_tournament(args)
    if report_path:
        print(f"\nFull report: {report_path}")


def load(args):
    print("")
    # Appel de la fonction correspondant voir avec jp


def save(args):
    print("")
    # Appel de la fonction correspondant voir avec jp


def plot(args):
    """Execute plot command. Delegates to PlotController."""
    PlotController.run_plot(args)


def Lanchester(args):
    print("")
    # pas d ecran terminal


def main():
    # Conserver eval et ajouter 'args' dans l'environnement pour éviter NameError
    dispatch_env = {
        "__builtins__": __builtins__,
        "args": args,
        "tourney": tourney,
        "run": run,
        "load": load,
        "save": save,
        "plot": plot,
        "Lanchester": Lanchester,
    }
    eval(f"{args.command}(args)", dispatch_env)


if __name__ == "__main__":
    main()
