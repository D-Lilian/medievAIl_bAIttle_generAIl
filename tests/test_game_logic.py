#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de la TerminalView avec la logique de jeu simplifiée
Lance une vraie bataille avec les mécaniques AOE2
"""

import sys
sys.path.insert(0, '../View')

from terminal_view import TerminalView
from simple_game_logic import create_test_scenario


def main():
    """Lance une bataille avec la vue terminal"""
    
    # Choix du scénario
    if len(sys.argv) > 1:
        scenario_type = sys.argv[1]
    else:
        print("Scénarios disponibles:")
        print("  mirror       - Formations miroir (3K + 5P + 4C identiques)")
        print("  lanchester   - Test loi de Lanchester (8K vs 8K)")
        print("  counter_demo - Démo tactiques (3K + 5P + 4C identiques)")
        print("\nUsage: python test_game_logic.py [scenario]")
        print("Par défaut: mirror")
        print("\nNote: Compositions TOUJOURS identiques - seules les stratégies diffèrent\n")
        scenario_type = "mirror"
    
    # Créer la simulation
    print(f"Lancement du scénario: {scenario_type}")
    simulation = create_test_scenario(scenario_type)
    
    print(f"Équipe 1: {len(simulation.board.get_alive_units(1))} unités")
    print(f"Équipe 2: {len(simulation.board.get_alive_units(2))} unités")
    print("\nCommandes:")
    print("  P       : Pause/Resume")
    print("  M       : Zoom")
    print("  +/-     : Vitesse de simulation")
    print("  ZQSD    : Scroll (Maj pour rapide)")
    print("  TAB     : Rapport HTML")
    print("  D       : Debug")
    print("  F       : Masquer UI")
    print("  ESC     : Quitter")
    print("\nDémarrage de la simulation...\n")
    
    # Créer la vue
    view = TerminalView(120, 120, tick_speed=20)
    
    try:
        view.init_curses()
        
        # Boucle principale
        running = True
        while running:
            # Mise à jour de la vue
            running = view.update(simulation)
            
            if not running:
                break
            
            # Avance la simulation si non en pause
            if not view.paused:
                simulation.step()
                
                # Vérifie si la bataille est terminée
                if simulation.is_finished():
                    view.paused = True  # Pause automatique
                    # Affiche le gagnant dans les stats (on continue d'afficher)
    
    finally:
        view.cleanup()
        
        # Affichage final
        print("\n" + "="*60)
        print("RÉSULTATS DE LA BATAILLE")
        print("="*60)
        print(f"Temps écoulé: {simulation.elapsed_time:.1f}s")
        
        team1_alive = simulation.board.get_alive_units(1)
        team2_alive = simulation.board.get_alive_units(2)
        
        print(f"\nÉquipe 1 (Cyan): {len(team1_alive)} survivants")
        for u in team1_alive:
            print(f"  - {type(u).__name__}: {u.hp}/{u.hp_max} HP")
        
        print(f"\nÉquipe 2 (Rouge): {len(team2_alive)} survivants")
        for u in team2_alive:
            print(f"  - {type(u).__name__}: {u.hp}/{u.hp_max} HP")
        
        if simulation.is_finished():
            if len(team1_alive) > 0:
                print("\n*** VICTOIRE ÉQUIPE 1 (Cyan) ***")
            else:
                print("\n*** VICTOIRE ÉQUIPE 2 (Rouge) ***")
        else:
            print("\nBataille interrompue")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    main()
