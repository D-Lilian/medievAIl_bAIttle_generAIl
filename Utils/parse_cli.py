# -*- coding: utf-8 -*-
"""
@file parse_cli.py
@brief CLI Parser - Command Line Interface

@details
Command syntax:
    battle run <scenario> <AI1> <AI2> [-t] [-d DATAFILE]
    battle load <savefile>
    battle tourney [-G AI1 AI2 ...] [-S SCENARIO1 SCENARIO2 ...] [-N=10] [-na]
    battle plot <AI> <plotter> <scenario(args)> <range> [-N=10] [--stats]

Options:
    -t          Launch terminal view instead of 2.5D
    -d          Specify where to write battle data
    -N          Number of rounds for each matchup (default: 10)
    -na         Do not alternate player position across N matches
    --stats     Enable statistical analysis for plots
"""
import argparse


parser = argparse.ArgumentParser(
    prog='battle',
    description='Medieval Battle Simulator - Run battles, tournaments, and analysis'
)
subparsers = parser.add_subparsers(dest='command', required=True)

# =============================================================================
# 'run' command: battle run <scenario> <AI1> <AI2> [-t] [-d DATAFILE]
# =============================================================================
p_run = subparsers.add_parser('run', help='Run a battle between two AIs')
p_run.add_argument('scenario', type=str, help='Name of the scenario to run')
p_run.add_argument('ai1', type=str, help='AI for team A')
p_run.add_argument('ai2', type=str, help='AI for team B')
p_run.add_argument('-t', action='store_true', default=None, help='Launch terminal view instead of 2.5D')
p_run.add_argument('-d', '--datafile', type=str, default=None, help='File to write battle data to')

# =============================================================================
# 'load' command: battle load <savefile>
# =============================================================================
p_load = subparsers.add_parser('load', help='Load a battle from a save file')
p_load.add_argument('savefile', type=str, help='Path to the save file')

# =============================================================================
# 'tourney' command: battle tourney [-G AI1 AI2 ...] [-S SCENARIO1 ...] [-N=10] [-na]
# =============================================================================
p_tourney = subparsers.add_parser('tourney', help='Run a tournament between multiple AIs')
p_tourney.add_argument('-G', '--ais', nargs='+', required=True, help='List of AI names to compete')
p_tourney.add_argument('-S', '--scenarios', nargs='+', required=False, help='List of scenarios to play on')
p_tourney.add_argument('-N', type=int, default=10, help='Number of rounds for each matchup')
p_tourney.add_argument('-na', '--no-alternate', action='store_true', help='Do not alternate player positions across N matches')

# =============================================================================
# 'plot' command: battle plot <AI> <plotter> <scenario(args)> <range> [-N=10] [--stats]
# =============================================================================
p_plot = subparsers.add_parser('plot', help='Plot outcomes of a scenario with varying parameters')
p_plot.add_argument('ai', type=str, help='AI to use (e.g., DAFT, BRAINDEAD)')
p_plot.add_argument('plotter', type=str, help='Plotter name (e.g., PlotLanchester, GGPlotLanchester)')
p_plot.add_argument('scenario', type=str, help='Scenario name (e.g., Lanchester)')
p_plot.add_argument('types', type=str, help='Unit types as [Type1,Type2]')
p_plot.add_argument('range_expr', type=str, help='Range as range(min,max) or range(min,max,step)')
p_plot.add_argument('-N', type=int, default=10, help='Number of repetitions per parameter value')
p_plot.add_argument('--stats', action='store_true', help='Enable statistical analysis')

args = parser.parse_args()