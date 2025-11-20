#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test scenarios for terminal_view.py.
Allows testing different situations without the full Model.
"""

import sys
from terminal_view import TerminalView

class DummyUnit:
    """Configurable dummy unit used for scenarios."""
    def __init__(self, x, y, team, unit_type, hp, hp_max):
        self.x = x
        self.y = y
        self.equipe = team
        self.hp = hp
        self.hp_max = hp_max
        self.name = unit_type

class DummyBoard:
    def __init__(self, units):
        self.units = units

class DummySimulation:
    def __init__(self, units):
        self.board = DummyBoard(units)
        self.elapsed_time = 0.0
    
    def step(self):
        # Simulate a simple movement
        for u in self.board.units:
            if u.hp > 0:
                u.x += 0.5 if u.equipe == 1 else -0.5
                # Simulate simple damage over time
                if u.hp > 0:
                    u.hp = max(0, u.hp - 1)
        self.elapsed_time += 0.05


def scenario_bataille_massive():
    """Scenario with many units (large battle)."""
    units = []
    # Team 1: line of 20 knights
    for i in range(20):
        units.append(DummyUnit(10 + i*2, 10, 1, 'Knight', 100, 100))
    
    # Team 2: line of 20 pikemen
    for i in range(20):
        units.append(DummyUnit(10 + i*2, 50, 2, 'Pikeman', 55, 55))
    
    return DummySimulation(units)


def scenario_unites_mourantes():
    """Scenario where units progressively die."""
    units = [
        DummyUnit(10, 10, 1, 'Knight', 100, 100),
        DummyUnit(12, 10, 1, 'Knight', 50, 100),
        DummyUnit(14, 10, 1, 'Knight', 10, 100),
        DummyUnit(16, 10, 1, 'Knight', 0, 100),  # Already dead
        DummyUnit(50, 50, 2, 'Pikeman', 55, 55),
        DummyUnit(52, 50, 2, 'Pikeman', 20, 55),
        DummyUnit(54, 50, 2, 'Pikeman', 0, 55),  # Already dead
    ]
    return DummySimulation(units)


def scenario_tous_types():
    """Scenario using all available unit types."""
    types = ['Knight', 'Pikeman', 'Crossbowman', 'Long Swordsman', 
             'Elite Skirmisher', 'Cavalry Archer', 'Onager', 'Light Cavalry',
             'Scorpion', 'Capped Ram', 'Trebuchet', 'Elite War Elephant', 
             'Monk', 'Castle', 'Wonder']
    
    units = []
    for i, unit_type in enumerate(types):
        # Team 1
        units.append(DummyUnit(10, 10 + i*3, 1, unit_type, 100, 100))
        # Team 2
        units.append(DummyUnit(60, 10 + i*3, 2, unit_type, 80, 100))
    
    return DummySimulation(units)


def run_scenario(name, scenario_func):
    """Run a given test scenario."""
    print(f"\n{'='*60}")
    print(f"Scenario: {name}")
    print(f"{'='*60}")
    
    sim = scenario_func()
    view = TerminalView(120, 120)
    
    # Headless test
    print("Initial snapshot:")
    snapshot = view.run_headless(sim, ticks=1)
    print(f"  Team 1: {snapshot['team1_alive']} alive, {snapshot['team1_dead']} dead")
    print(f"  Team 2: {snapshot['team2_alive']} alive, {snapshot['team2_dead']} dead")
    print(f"  Types team 1: {snapshot['types_team1']}")
    print(f"  Types team 2: {snapshot['types_team2']}")
    
    # Simulate a few ticks
    print("\nSimulating 20 ticks...")
    snapshot2 = view.run_headless(sim, ticks=20)
    print(f"  Team 1: {snapshot2['team1_alive']} alive, {snapshot2['team1_dead']} dead")
    print(f"  Team 2: {snapshot2['team2_alive']} alive, {snapshot2['team2_dead']} dead")
    
    # Option: generate HTML report
    view.update_units_cache(sim)
    print("\nGenerating HTML report...")
    view.generate_html_report()
    print("  Report generated and opened in the browser")


def main():
    """Simple menu to pick and run test scenarios."""
    scenarios = {
        '1': ('Massive battle (40 units)', scenario_bataille_massive),
        '2': ('Dying units', scenario_unites_mourantes),
        '3': ("All unit types", scenario_tous_types),
    }
    
    if '--all' in sys.argv:
        for name, func in scenarios.values():
            run_scenario(name, func)
    else:
        print("\nAvailable test scenarios:")
        for key, (name, _) in scenarios.items():
            print(f"  {key}. {name}")
        print("\nUsage:")
        print(f"  python {sys.argv[0]} <number>")
        print(f"  python {sys.argv[0]} --all  (run all scenarios)")
        print("\nExample:")
        print(f"  python {sys.argv[0]} 1")
        
        if len(sys.argv) > 1 and sys.argv[1] in scenarios:
            name, func = scenarios[sys.argv[1]]
            run_scenario(name, func)


if __name__ == '__main__':
    main()
