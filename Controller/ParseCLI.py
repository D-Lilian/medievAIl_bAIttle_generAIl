import argparse


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command', required=True)

# 'run' command
p_run = subparsers.add_parser('run', help='Run a battle between two AIs.')
p_run.add_argument('scenario', type=str, help='Name of the scenario to run.')
p_run.add_argument('ai1', type=str, help='Name of the AI for team 1.')
p_run.add_argument('ai2', type=str, help='Name of the AI for team 2.')
p_run.add_argument('-t', type=int, help="terminal view")
p_run.add_argument('-d', '--datafile', type=str, default=None, help='File to write battle data to.')


# 'load' command
p_load = subparsers.add_parser('load', help='Load a battle from a save battle.')
p_load.add_argument('savefile', type=str, help='Path to the (? .sav) file.')

# 'tourney' command
p_tourney = subparsers.add_parser('tourney', help='Run a tournament between multiple AIs.')
p_tourney.add_argument('-G', '--ais', nargs='+', required=True, help='List of AI names to compete.')
p_tourney.add_argument('-S', '--scenarios', nargs='+', required=True, help='List of scenarios to play on.')
p_tourney.add_argument('-N', type=int, default=10, help='Number of rounds for each matchup.')
p_tourney.add_argument('-na', '--no-alternate', action='store_true', help='Do not alternate player positions accros N matches.')

# 'plot' command
p_plot = subparsers.add_parser('plot', help='Plot outcomes of a scenario with varying parameters.')
p_plot.add_argument('<ai>', type=str, help='AI to use for the simulation.')
p_plot.add_argument('<plotter>', type=str, help='Name of the plotting function.')
p_plot.add_argument('<scenario_params>', nargs=2, help='Scenario name and the parameter to vary (e.g., Lanchester N).')
p_plot.add_argument('<range_params>', nargs='+', help='Range for the parameter (e.g., range(1,100)).')
p_plot.add_argument('-N', type=int, default=10, help='Number of repetitions for each parameter value.')

args = parser.parse_args()