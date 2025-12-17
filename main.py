#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file main.py
@brief Main entry point for the Medieval Battle Simulator

Usage:
    python main.py run --scenario s1 --ai1 DAFT --ai2 DAFT
    python main.py plot --ai DAFT --plotter Lanchester --scenario Lanchester --types "[Knight,Crossbow]" --range "range(20,100,20)" -N 10
    python main.py tourney --scenario s1 --ais "[BRAINDEAD,DAFT,SOMEIQ]"
"""

from Utils.eval import main

if __name__ == "__main__":
    main()
