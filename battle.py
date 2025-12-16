#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file battle.py
@brief Main entry point for the Medieval Battle simulation CLI

@details
Provides a unified command-line interface for running battles,
tournaments, and generating analysis plots.

Usage:
    python battle.py run <scenario> --ai1 <AI1> --ai2 <AI2> [-t] [-d DATAFILE]
    python battle.py load <savefile>
    python battle.py tourney -G AI1 AI2 ... [-S SCENARIO1 SCENARIO2] [-N=10] [-na]
    python battle.py plot --ai <AI> --plotter <plotter> --scenario_params <scenario> <param> --range_params <values> [-N=10]

Examples:
    python battle.py run --scenario classical_medieval_battle --ai1 DAFT --ai2 BRAINDEAD
    python battle.py tourney -G DAFT BRAINDEAD SOMEIQ -N 5
    python battle.py plot --ai DAFT --plotter PlotLanchester --scenario_params Lanchester N --range_params Knight Crossbowman -N 10
"""

import sys
import os

# Ensure the project root is in the path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Utils.eval import main

if __name__ == "__main__":
    main()
