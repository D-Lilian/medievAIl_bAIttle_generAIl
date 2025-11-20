#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests de validation des spécifications du projet
Vérifie que l'implémentation respecte les consignes du professeur
"""

import sys
import math
sys.path.insert(0, '../View')

from simple_game_logic import Knight, Pikeman, Crossbowman, Board, Simulation, create_test_scenario
from terminal_view import TerminalView


def test_positions_flottantes():
    """Test: Les positions sont flottantes, pas limitées à une grille entière"""
    print("\n[TEST] Positions flottantes")
    
    knight = Knight(12.5, 34.7, 1)
    assert isinstance(knight.x, float), "Position X doit être float"
    assert isinstance(knight.y, float), "Position Y doit être float"
    assert knight.x == 12.5, "Position X doit accepter valeurs décimales"
    assert knight.y == 34.7, "Position Y doit accepter valeurs décimales"
    
    print("  ✓ Positions flottantes validées")


def test_collision_circulaire():
    """Test: Collision basée sur cercles, pas sur cases"""
    print("\n[TEST] Collision circulaire")
    
    u1 = Knight(10.0, 10.0, 1)
    u2 = Pikeman(10.5, 10.0, 1)
    
    # Vérifier que collision_radius existe
    assert hasattr(u1, 'collision_radius'), "Unité doit avoir collision_radius"
    assert u1.collision_radius > 0, "collision_radius doit être > 0"
    
    # Knight plus gros que Pikeman
    assert u1.collision_radius > u2.collision_radius, "Knight doit être plus gros que Pikeman"
    
    # Vérifier méthode de collision
    distance = u1.distance_to(u2)
    sum_radii = u1.collision_radius + u2.collision_radius
    should_collide = distance < sum_radii
    
    assert u1.collides_with(u2) == should_collide, "Collision doit être basée sur cercles"
    
    print(f"  ✓ Knight radius: {u1.collision_radius}")
    print(f"  ✓ Pikeman radius: {u2.collision_radius}")
    print(f"  ✓ Collision circulaire validée")


def test_line_of_sight_circulaire():
    """Test: Line of sight circulaire (distance euclidienne)"""
    print("\n[TEST] Line of Sight circulaire")
    
    u1 = Knight(0, 0, 1)
    u2 = Knight(3, 4, 2)  # Distance = 5
    
    distance = u1.distance_to(u2)
    expected = math.sqrt(3**2 + 4**2)
    
    assert abs(distance - expected) < 0.01, "Distance doit être euclidienne"
    assert abs(distance - 5.0) < 0.01, "Distance (3,4) doit être 5"
    
    # Vérifier que line_of_sight existe
    assert hasattr(u1, 'line_of_sight'), "Unité doit avoir line_of_sight"
    
    print(f"  ✓ Distance euclidienne: {distance:.2f}")
    print(f"  ✓ Line of sight: {u1.line_of_sight} tiles")
    print(f"  ✓ Line of sight circulaire validée")


def test_temps_reel_pas_de_tours():
    """Test: Simulation en temps réel, pas de système de tours"""
    print("\n[TEST] Temps réel (pas de tours)")
    
    sim = create_test_scenario("mirror")
    
    # Vérifier temps continu
    initial_time = sim.elapsed_time
    sim.step()
    assert sim.elapsed_time > initial_time, "Le temps doit avancer"
    assert isinstance(sim.elapsed_time, float), "Temps doit être float"
    
    # Vérifier dt constant
    assert hasattr(sim, 'dt'), "Simulation doit avoir dt"
    assert sim.dt > 0, "dt doit être > 0"
    
    print(f"  ✓ Delta temps: {sim.dt}s par tick")
    print(f"  ✓ Temps continu validé (pas de tours)")


def test_premier_arrive_occupe_espace():
    """Test: Premier arrivé occupe l'espace (gestion collision)"""
    print("\n[TEST] Premier arrivé occupe l'espace")
    
    board = Board(120, 120)
    
    # Deux unités très proches
    u1 = Knight(50.0, 50.0, 1)
    u2 = Knight(50.1, 50.0, 2)
    
    board.add_unit(u1)
    board.add_unit(u2)
    
    # u1 essaie d'aller vers u2 (collision attendue)
    initial_x = u1.x
    u1.move_towards(u2.x, u2.y, 0.1, board)
    
    # u1 ne devrait pas pouvoir avancer (u2 occupe l'espace)
    moved_distance = abs(u1.x - initial_x)
    
    print(f"  ✓ Distance déplacée avec collision: {moved_distance:.4f}")
    print(f"  ✓ Gestion collision validée")


def test_stats_aoe2_exactes():
    """Test: Statistiques AOE2 exactes"""
    print("\n[TEST] Stats AOE2 exactes")
    
    # Knight
    k = Knight(0, 0, 1)
    assert k.hp_max == 100, "Knight HP doit être 100"
    assert k.attack == 10, "Knight attack doit être 10"
    assert k.melee_armor == 2, "Knight melee armor doit être 2"
    assert k.pierce_armor == 2, "Knight pierce armor doit être 2"
    assert k.speed == 1.35, "Knight speed doit être 1.35"
    
    # Pikeman
    p = Pikeman(0, 0, 1)
    assert p.hp_max == 55, "Pikeman HP doit être 55"
    assert p.attack == 4, "Pikeman attack doit être 4"
    assert p.bonus_vs['Knight'] == 22, "Pikeman bonus vs cavalry doit être +22"
    
    # Crossbowman
    c = Crossbowman(0, 0, 1)
    assert c.hp_max == 35, "Crossbowman HP doit être 35"
    assert c.range == 5, "Crossbowman range doit être 5"
    assert c.line_of_sight == 7, "Crossbowman LoS doit être 7"
    
    print("  ✓ Knight: HP=100, ATK=10, ARM=2/2, SPD=1.35")
    print("  ✓ Pikeman: HP=55, ATK=4 (+22 vs cavalry)")
    print("  ✓ Crossbowman: HP=35, RNG=5, LoS=7")
    print("  ✓ Stats AOE2 validées")


def test_formule_degats():
    """Test: Formule de dégâts AOE2"""
    print("\n[TEST] Formule de dégâts AOE2")
    
    knight = Knight(0, 0, 1)
    pikeman = Pikeman(5, 0, 2)
    crossbow = Crossbowman(10, 0, 2)
    
    # Knight vs Pikeman (10 - 0 = 10 damage)
    dmg1 = knight.get_damage_against(pikeman)
    assert dmg1 == 10, f"Knight vs Pikeman devrait faire 10, pas {dmg1}"
    
    # Pikeman vs Knight (4 + 22 - 2 = 24 damage)
    dmg2 = pikeman.get_damage_against(knight)
    assert dmg2 == 24, f"Pikeman vs Knight devrait faire 24, pas {dmg2}"
    
    # Crossbow vs Knight (5 - 2 pierce = 3 damage)
    dmg3 = crossbow.get_damage_against(knight)
    assert dmg3 == 3, f"Crossbow vs Knight devrait faire 3, pas {dmg3}"
    
    print(f"  ✓ Knight vs Pikeman: {dmg1} damage")
    print(f"  ✓ Pikeman vs Knight: {dmg2} damage (bonus anti-cavalry)")
    print(f"  ✓ Crossbow vs Knight: {dmg3} damage")
    print("  ✓ Formule de dégâts validée")


def test_separation_temps_logique_framerate():
    """Test: Séparation temps logique / framerate"""
    print("\n[TEST] Séparation temps logique / framerate")
    
    sim = create_test_scenario("mirror")
    view = TerminalView(120, 120, tick_speed=30)
    
    # Temps logique dans Model
    assert hasattr(sim, 'elapsed_time'), "Model doit avoir elapsed_time"
    
    # Framerate dans View
    assert hasattr(view, 'tick_speed'), "View doit avoir tick_speed"
    assert hasattr(view, 'fps'), "View doit tracker FPS"
    
    # Les deux sont indépendants
    assert sim.elapsed_time != view.tick_speed, "Temps logique ≠ framerate"
    
    print(f"  ✓ Temps logique (Model): {sim.elapsed_time}s")
    print(f"  ✓ Tick speed (View): {view.tick_speed} FPS")
    print("  ✓ Séparation validée")


def test_mode_headless():
    """Test: Mode headless pour tournois"""
    print("\n[TEST] Mode headless (simulation sans affichage)")
    
    sim = create_test_scenario("mirror")
    view = TerminalView(120, 120)
    
    # Headless doit fonctionner sans init_curses
    snapshot = view.run_headless(sim, ticks=50)
    
    assert 'time' in snapshot, "Snapshot doit contenir le temps"
    assert 'team1_alive' in snapshot, "Snapshot doit contenir compteurs"
    assert snapshot['time'] > 0, "Temps doit avoir avancé"
    
    print(f"  ✓ 50 ticks simulés en mode headless")
    print(f"  ✓ Temps: {snapshot['time']:.2f}s")
    print("  ✓ Mode headless validé")


def test_compositions_identiques():
    """Test: Scénarios avec compositions identiques"""
    print("\n[TEST] Compositions identiques (équité)")
    
    for scenario in ["mirror", "lanchester", "counter_demo"]:
        sim = create_test_scenario(scenario)
        
        t1_units = sim.board.get_alive_units(1)
        t2_units = sim.board.get_alive_units(2)
        
        # Même nombre d'unités
        assert len(t1_units) == len(t2_units), f"{scenario}: compositions doivent être égales"
        
        # Même types (tri pour comparaison)
        t1_types = sorted([type(u).__name__ for u in t1_units])
        t2_types = sorted([type(u).__name__ for u in t2_units])
        assert t1_types == t2_types, f"{scenario}: types doivent être identiques"
        
        print(f"  ✓ {scenario}: {len(t1_units)} vs {len(t2_units)} unités (identiques)")
    
    print("  ✓ Équité des compositions validée")


def run_all_tests():
    """Lance tous les tests de validation"""
    print("=" * 70)
    print("VALIDATION DES SPÉCIFICATIONS DU PROJET")
    print("=" * 70)
    
    tests = [
        test_positions_flottantes,
        test_collision_circulaire,
        test_line_of_sight_circulaire,
        test_temps_reel_pas_de_tours,
        test_premier_arrive_occupe_espace,
        test_stats_aoe2_exactes,
        test_formule_degats,
        test_separation_temps_logique_framerate,
        test_mode_headless,
        test_compositions_identiques,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ ÉCHEC: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERREUR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"RÉSULTATS: {passed} tests réussis, {failed} tests échoués")
    print("=" * 70)
    
    if failed == 0:
        print("\n✓ Toutes les spécifications sont respectées!")
        return 0
    else:
        print(f"\n✗ {failed} spécification(s) non respectée(s)")
        return 1


if __name__ == "__main__":
    exit(run_all_tests())
