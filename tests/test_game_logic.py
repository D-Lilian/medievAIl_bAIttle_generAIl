#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the TerminalView with simplified game logic.
Runs a real battle using AOE2-like mechanics.
"""

import sys
sys.path.insert(0, '../View')
from collections import Counter

from terminal_view import TerminalView
from simple_game_logic import create_test_scenario


def main():
    """Run a battle using the terminal view."""
    
    # Scenario selection
    if len(sys.argv) > 1:
        scenario_type = sys.argv[1]
    else:
        print("Available scenarios:")
        print("  mirror       - Mirror formations (3K + 5P + 4C identical)")
        print("  lanchester   - Lanchester law test (8K vs 8K)")
        print("  counter_demo - Tactics demo (3K + 5P + 4C identical)")
        print("\nUsage: python test_game_logic.py [scenario]")
        print("Default: mirror")
        print("\nNote: Compositions are ALWAYS identical - only strategies differ.\n")
        scenario_type = "mirror"
    
    # Create the simulation
    print(f"Starting scenario: {scenario_type}")
    simulation = create_test_scenario(scenario_type)
    
    print(f"Team 1 (Cyan): BRAINDEAD strategy - {len(simulation.board.get_alive_units(1))} units")
    print(f"Team 2 (Red): DAFT strategy - {len(simulation.board.get_alive_units(2))} units")
    print("\nControls:")
    print("  P       : Pause/Resume")
    print("  M       : Zoom")
    print("  +/-     : Simulation speed")
    print("  ZQSD    : Scroll (Shift for faster)")
    print("  TAB     : HTML report")
    print("  D       : Debug")
    print("  F       : Toggle UI")
    print("  ESC     : Quit")
    print("\nStarting simulation...\n")
    
    # Create the view
    view = TerminalView(120, 120, tick_speed=30)
    
    try:
        view.init_curses()
        
        # Main loop
        running = True
        while running:
            # Update the view
            running = view.update(simulation)
            if not running:
                break
            # Advance simulation
            simulation.step()
            # Stop immediately if the battle is finished
            if simulation.is_finished():
                break
    
    finally:
        view.cleanup()
        
        # Final summary in the console
        print("\n" + "="*60)
        print("BATTLE RESULTS")
        print("="*60)
        print(f"Elapsed time: {simulation.elapsed_time:.1f}s")
        
        team1_alive = simulation.board.get_alive_units(1)
        team2_alive = simulation.board.get_alive_units(2)
        
        print(f"\nTeam 1 (Cyan - BRAINDEAD): {len(team1_alive)} survivors")
        if team1_alive:
            unit_counts = Counter(type(u).__name__ for u in team1_alive)
            for unit_type, count in unit_counts.items():
                print(f"  - {unit_type}: {count} units")
        
        print(f"\nTeam 2 (Red - DAFT): {len(team2_alive)} survivors")
        if team2_alive:
            unit_counts = Counter(type(u).__name__ for u in team2_alive)
            for unit_type, count in unit_counts.items():
                print(f"  - {unit_type}: {count} units")
        
        if simulation.is_finished():
            if len(team1_alive) > 0:
                print("\n*** TEAM 1 (Cyan - BRAINDEAD) WINS ***")
                print("*** BRAINDEAD STRATEGY (General) WINS ***")
            else:
                print("\n*** TEAM 2 (Red - DAFT) WINS ***")
                print("*** DAFT STRATEGY (General) WINS ***")
        else:
            print("\nBattle interrupted")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    main()
