#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scénarios de test pour terminal_view.py
Permet de tester différentes situations sans le Model complet
"""

import sys
from terminal_view import TerminalView

class DummyUnit:
    """Unité factice configurable"""
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
        # Simule un mouvement simple
        for u in self.board.units:
            if u.hp > 0:
                u.x += 0.5 if u.equipe == 1 else -0.5
                # Simule des dégâts aléatoires
                if u.hp > 0:
                    u.hp = max(0, u.hp - 1)
        self.elapsed_time += 0.05


def scenario_bataille_massive():
    """Test avec beaucoup d'unités"""
    units = []
    # Équipe 1 : ligne de 20 knights
    for i in range(20):
        units.append(DummyUnit(10 + i*2, 10, 1, 'Knight', 100, 100))
    
    # Équipe 2 : ligne de 20 pikemen
    for i in range(20):
        units.append(DummyUnit(10 + i*2, 50, 2, 'Pikeman', 55, 55))
    
    return DummySimulation(units)


def scenario_unites_mourantes():
    """Test avec des unités qui meurent progressivement"""
    units = [
        DummyUnit(10, 10, 1, 'Knight', 100, 100),
        DummyUnit(12, 10, 1, 'Knight', 50, 100),
        DummyUnit(14, 10, 1, 'Knight', 10, 100),
        DummyUnit(16, 10, 1, 'Knight', 0, 100),  # Déjà mort
        DummyUnit(50, 50, 2, 'Pikeman', 55, 55),
        DummyUnit(52, 50, 2, 'Pikeman', 20, 55),
        DummyUnit(54, 50, 2, 'Pikeman', 0, 55),  # Déjà mort
    ]
    return DummySimulation(units)


def scenario_tous_types():
    """Test avec tous les types d'unités"""
    types = ['Knight', 'Pikeman', 'Crossbowman', 'Long Swordsman', 
             'Elite Skirmisher', 'Cavalry Archer', 'Onager', 'Light Cavalry',
             'Scorpion', 'Capped Ram', 'Trebuchet', 'Elite War Elephant', 
             'Monk', 'Castle', 'Wonder']
    
    units = []
    for i, unit_type in enumerate(types):
        # Équipe 1
        units.append(DummyUnit(10, 10 + i*3, 1, unit_type, 100, 100))
        # Équipe 2
        units.append(DummyUnit(60, 10 + i*3, 2, unit_type, 80, 100))
    
    return DummySimulation(units)


def run_scenario(name, scenario_func):
    """Lance un scénario de test"""
    print(f"\n{'='*60}")
    print(f"Scénario: {name}")
    print(f"{'='*60}")
    
    sim = scenario_func()
    view = TerminalView(120, 120)
    
    # Test headless
    print("Snapshot initial:")
    snapshot = view.run_headless(sim, ticks=1)
    print(f"  Équipe 1: {snapshot['team1_alive']} vivants, {snapshot['team1_dead']} morts")
    print(f"  Équipe 2: {snapshot['team2_alive']} vivants, {snapshot['team2_dead']} morts")
    print(f"  Types équipe 1: {snapshot['types_team1']}")
    print(f"  Types équipe 2: {snapshot['types_team2']}")
    
    # Simule quelques ticks
    print("\nSimulation de 20 ticks...")
    snapshot2 = view.run_headless(sim, ticks=20)
    print(f"  Équipe 1: {snapshot2['team1_alive']} vivants, {snapshot2['team1_dead']} morts")
    print(f"  Équipe 2: {snapshot2['team2_alive']} vivants, {snapshot2['team2_dead']} morts")
    
    # Option: générer HTML
    view.update_units_cache(sim)
    print("\nGénération du rapport HTML...")
    view.generate_html_report()
    print("  Rapport généré et ouvert dans le navigateur")


def main():
    """Menu de test"""
    scenarios = {
        '1': ('Bataille massive (40 unités)', scenario_bataille_massive),
        '2': ('Unités mourantes', scenario_unites_mourantes),
        '3': ('Tous les types d\'unités', scenario_tous_types),
    }
    
    if '--all' in sys.argv:
        for name, func in scenarios.values():
            run_scenario(name, func)
    else:
        print("\nScénarios de test disponibles:")
        for key, (name, _) in scenarios.items():
            print(f"  {key}. {name}")
        print("\nUtilisation:")
        print(f"  python {sys.argv[0]} <numéro>")
        print(f"  python {sys.argv[0]} --all  (lance tous les scénarios)")
        print("\nExemple:")
        print(f"  python {sys.argv[0]} 1")
        
        if len(sys.argv) > 1 and sys.argv[1] in scenarios:
            name, func = scenarios[sys.argv[1]]
            run_scenario(name, func)


if __name__ == '__main__':
    main()
