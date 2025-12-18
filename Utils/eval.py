from Utils.parse_cli import args
from Controller.simulation_controller import SimulationController
from Controller.tournament_controller import TournamentController
from Controller.plot_controller import PlotController
from Model.scenario import Scenario
from Utils.predefined_scenarios import PredefinedScenarios
from Model.general_factory import create_general


def run(args):
    """Run a battle scenario."""
    from Controller.hybrid_controller import HybridController, ViewMode
    
    print(f"Running scenario: {args.scenario} with AIs: {args.ai1} vs {args.ai2}")
    
    # Use the centralized scenario registry
    try:
        selected_scenario = PredefinedScenarios.get_scenario(args.scenario)
    except ValueError as e:
        print(f"Error: {e}")
        print(f"Available scenarios: {PredefinedScenarios.list_scenarios()}")
        return

    # Create generals
    ai1 = create_general(args.ai1, selected_scenario.units_a, selected_scenario.units_b)
    ai2 = create_general(args.ai2, selected_scenario.units_b, selected_scenario.units_a)
    
    # Create Scenario
    game = Scenario(
        units=selected_scenario.units,
        units_a=selected_scenario.units_a,
        units_b=selected_scenario.units_b,
        general_a=ai1,
        general_b=ai2,
        size_x=selected_scenario.size_x,
        size_y=selected_scenario.size_y,
    )

    sim_controller = SimulationController()
    
    # Determine initial view mode
    initial_mode = ViewMode.TERMINAL if args.terminal else ViewMode.PYGAME
    initial_tick = 10 if args.terminal else 60
    
    print(f"Starting in {'Terminal' if args.terminal else 'Pygame (2.5D)'} view. Press F9 to switch views.")
    
    # Initialize simulation
    sim_controller.initialize_simulation(game, tick_speed=initial_tick, paused=True, unlocked=False)
    
    # Create hybrid controller (allows switching between views with F9)
    controller = HybridController(sim_controller, game, initial_mode=initial_mode)
    
    # Start simulation thread
    sim_controller.start_simulation()
    
    # Run view loop (blocking) - handles view switching internally
    controller.run()


def tourney(args):
    """Run a tournament between AI generals. Delegates to TournamentController."""
    TournamentController.run_tournament(args)


def load(args):
    """Load a saved game and run it."""
    from Controller.hybrid_controller import HybridController, ViewMode
    from Utils.save_load import SaveLoad
    
    print(f"Loading game from: {args.savefile}")
    
    # Load scenario from save file
    scenario = SaveLoad.load_game(args.savefile)
    if scenario is None:
        print("Failed to load game.")
        return
    
    sim_controller = SimulationController()
    
    # Default to pygame view for loaded games
    initial_mode = ViewMode.PYGAME
    initial_tick = 60
    
    print("Game loaded. Press F9 to switch views.")
    
    # Initialize simulation
    sim_controller.initialize_simulation(scenario, tick_speed=initial_tick, paused=True, unlocked=False)
    
    # Create hybrid controller
    controller = HybridController(sim_controller, scenario, initial_mode=initial_mode)
    
    # Start simulation thread
    sim_controller.start_simulation()
    
    # Run view loop
    controller.run()


def plot(args):
    """Execute plot command. Delegates to PlotController."""
    PlotController.run_plot(args)


def main():
    dispatch_env = {
        "__builtins__": __builtins__,
        "args": args,
        "run": run,
        "load": load,
        "tourney": tourney,
        "plot": plot,
    }
    eval(f"{args.command}(args)", dispatch_env)


if __name__ == "__main__":
    main()
