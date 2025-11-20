#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logique de jeu basique pour tester la Vue
3 unités avec stats AOE2, combat simple
"""

import math
from typing import List, Optional


class Unit:
    """Classe de base pour toutes les unités"""
    
    # Taille de collision (rayon du cercle occupé par l'unité)
    collision_radius = 0.5  # Défaut, redéfini dans les sous-classes
    
    def __init__(self, x: float, y: float, team: int):
        self.x = x
        self.y = y
        self.equipe = team
        self.hp = self.hp_max
        self.reload_timer = 0.0
        self.target: Optional['Unit'] = None
        
    def distance_to(self, other: 'Unit') -> float:
        """Calcule la distance euclidienne vers une autre unité (centre à centre)"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def collides_with(self, other: 'Unit') -> bool:
        """Vérifie si cette unité entre en collision avec une autre (cercles)"""
        distance = self.distance_to(other)
        return distance < (self.collision_radius + other.collision_radius)
    
    def can_attack(self, target: 'Unit') -> bool:
        """Vérifie si l'unité peut attaquer la cible"""
        if self.reload_timer > 0:
            return False
        return self.distance_to(target) <= self.range
    
    def get_damage_against(self, target: 'Unit') -> int:
        """Calcule les dégâts infligés à la cible selon la formule AOE2"""
        total_attack = self.attack
        
        # Bonus damage (système simplifié)
        if hasattr(self, 'bonus_vs') and type(target).__name__ in self.bonus_vs:
            total_attack += self.bonus_vs[type(target).__name__]
        
        # Formule AOE2: max(1, Attack - Armor)
        # On utilise melee_armor ou pierce_armor selon le type d'attaque
        armor = target.pierce_armor if self.range > 0 else target.melee_armor
        damage = max(1, total_attack - armor)
        
        return damage
    
    def attack_unit(self, target: 'Unit', dt: float):
        """Attaque une unité cible"""
        if self.can_attack(target):
            damage = self.get_damage_against(target)
            target.hp -= damage
            self.reload_timer = self.reload_time
    
    def move_towards(self, target_x: float, target_y: float, dt: float, board: 'Board' = None):
        """Déplace l'unité vers une position en évitant les collisions"""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normaliser et appliquer la vitesse
            dx /= distance
            dy /= distance
            move_distance = self.speed * dt
            
            if move_distance < distance:
                new_x = self.x + dx * move_distance
                new_y = self.y + dy * move_distance
                
                # Vérifier les collisions avec autres unités (premier arrivé occupe l'espace)
                collision = False
                if board:
                    for other in board.units:
                        if other is not self and other.hp > 0:
                            # Distance entre nouvelle position et autre unité
                            dist_to_other = math.sqrt((new_x - other.x)**2 + (new_y - other.y)**2)
                            if dist_to_other < (self.collision_radius + other.collision_radius):
                                collision = True
                                break
                
                # Si pas de collision, on se déplace
                if not collision:
                    self.x = new_x
                    self.y = new_y
                # Sinon on reste sur place (l'autre occupe déjà l'espace)
            else:
                self.x = target_x
                self.y = target_y
    
    def update(self, dt: float):
        """Met à jour l'état de l'unité"""
        if self.reload_timer > 0:
            self.reload_timer = max(0, self.reload_timer - dt)


class Knight(Unit):
    """Knight - Cavalerie lourde, forte contre archers"""
    
    name = "Knight"
    hp_max = 100
    attack = 10
    melee_armor = 2
    pierce_armor = 2
    range = 0  # Mêlée
    line_of_sight = 4
    speed = 1.35  # tiles/seconde
    reload_time = 1.8  # secondes
    collision_radius = 0.6  # Cavalerie = plus gros
    
    def __init__(self, x: float, y: float, team: int):
        super().__init__(x, y, team)


class Pikeman(Unit):
    """Pikeman - Infanterie anti-cavalerie"""
    
    name = "Pikeman"
    hp_max = 55
    attack = 4
    melee_armor = 0
    pierce_armor = 0
    range = 0
    line_of_sight = 4
    speed = 1.0
    reload_time = 3.0
    collision_radius = 0.45  # Infanterie = taille normale
    
    def __init__(self, x: float, y: float, team: int):
        super().__init__(x, y, team)
        # Bonus massif contre cavalerie
        self.bonus_vs = {'Knight': 22, 'Cavalry Archer': 22}


class Crossbowman(Unit):
    """Crossbowman - Archer à distance, faible en mêlée"""
    
    name = "Crossbowman"
    hp_max = 35
    attack = 5
    melee_armor = 0
    pierce_armor = 0
    range = 5  # tiles
    line_of_sight = 7
    speed = 0.96
    reload_time = 2.0
    collision_radius = 0.45  # Archers = taille normale
    
    def __init__(self, x: float, y: float, team: int):
        super().__init__(x, y, team)


class Board:
    """Plateau de jeu contenant toutes les unités"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.units: List[Unit] = []
    
    def add_unit(self, unit: Unit):
        """Ajoute une unité au plateau"""
        self.units.append(unit)
    
    def get_alive_units(self, team: Optional[int] = None) -> List[Unit]:
        """Retourne les unités vivantes (optionnellement d'une équipe)"""
        units = [u for u in self.units if u.hp > 0]
        if team is not None:
            units = [u for u in units if u.equipe == team]
        return units
    
    def get_nearest_enemy(self, unit: Unit) -> Optional[Unit]:
        """Trouve l'ennemi le plus proche d'une unité"""
        # Convertir 'A'/'B' ou 1/2 vers l'équipe opposée
        if unit.equipe in ('A', 'a', 1):
            enemy_team = 'B'
        else:
            enemy_team = 'A'
        enemies = self.get_alive_units(team=enemy_team)
        if not enemies:
            return None
        
        nearest = min(enemies, key=lambda e: unit.distance_to(e))
        return nearest


class Simulation:
    """
    Simulation de bataille en temps réel (pas de tours).
    
    Basée sur les specs du prof:
    - Positions flottantes (x, y) continues
    - Collision circulaire (rayon par type d'unité)
    - Line of sight circulaire (distance euclidienne)
    - Premier arrivé occupe l'espace (pas de priorité de tour)
    - Le général contrôle toutes ses unités en temps réel
    """
    
    def __init__(self, board: Board, ai1_type: str = "DAFT", ai2_type: str = "DAFT"):
        self.board = board
        self.elapsed_time = 0.0  # Temps logique de la simulation
        self.dt = 0.05  # Delta temps par tick (50ms) - indépendant du framerate
        self.ai1_type = ai1_type
        self.ai2_type = ai2_type
    
    def step(self):
        """Avance la simulation d'un tick"""
        # IA pour chaque équipe
        self._run_ai(1, self.ai1_type)
        self._run_ai(2, self.ai2_type)
        
        # Mise à jour des unités
        for unit in self.board.get_alive_units():
            unit.update(self.dt)
        
        self.elapsed_time += self.dt
    
    def _run_ai(self, team: int, ai_type: str):
        """Exécute l'IA pour une équipe"""
        units = self.board.get_alive_units(team)
        
        if ai_type == "BRAINDEAD":
            # Ne fait rien - les unités n'attaquent que si en vue
            pass
        
        elif ai_type == "DAFT":
            # Attaque l'ennemi le plus proche sans réfléchir
            for unit in units:
                nearest_enemy = self.board.get_nearest_enemy(unit)
                if nearest_enemy:
                    # Si à portée, attaque
                    if unit.can_attack(nearest_enemy):
                        unit.attack_unit(nearest_enemy, self.dt)
                    else:
                        # Sinon, se rapproche
                        # Pour archers, se rapprocher jusqu'à portée optimale
                        distance = unit.distance_to(nearest_enemy)
                        if distance > unit.range:
                            unit.move_towards(nearest_enemy.x, nearest_enemy.y, self.dt, self.board)
                        elif distance < unit.range * 0.8:  # Trop proche pour archer
                            # Reculer un peu
                            dx = unit.x - nearest_enemy.x
                            dy = unit.y - nearest_enemy.y
                            dist = math.sqrt(dx**2 + dy**2)
                            if dist > 0:
                                unit.move_towards(
                                    unit.x + (dx/dist) * 2,
                                    unit.y + (dy/dist) * 2,
                                    self.dt,
                                    self.board
                                )
    
    def is_finished(self) -> bool:
        """Vérifie si la bataille est terminée"""
        team_a_alive = len(self.board.get_alive_units('A'))
        team_b_alive = len(self.board.get_alive_units('B'))
        return team_a_alive == 0 or team_b_alive == 0


def create_test_scenario(scenario_type: str = "mirror") -> Simulation:
    """
    Crée un scénario de test pour la simulation de bataille.
    
    Args:
        scenario_type: Type de scénario ("mirror", "lanchester", "counter_demo")
    
    Returns:
        Simulation: Instance de simulation configurée avec le scénario choisi
    """
    board = Board(120, 120)
    
    if scenario_type == "mirror":
        # Formations miroir face à face - TRÈS RAPPROCHÉES pour combat immédiat
        formations = [
            (Knight, 3),
            (Pikeman, 5),
            (Crossbowman, 4),
        ]
        
        y_pos = 40
        for unit_class, count in formations:
            # Équipe A (gauche) - position 50
            for i in range(count):
                board.add_unit(unit_class(50, y_pos + i*2, 'A'))
            
            # Équipe B (droite) - position 70 (distance = 20 tiles)
            for i in range(count):
                board.add_unit(unit_class(70, y_pos + i*2, 'B'))
            
            y_pos += count * 2 + 3
    
    elif scenario_type == "lanchester":
        # Test lois de Lanchester - compositions identiques
        N = 8
        
        # N Knights équipe A
        for i in range(N):
            board.add_unit(Knight(45, 35 + i*3, 'A'))
        
        # N Knights équipe B (même nombre!)
        for i in range(N):
            board.add_unit(Knight(75, 35 + i*3, 'B'))
    
    elif scenario_type == "counter_demo":
        # Démonstration du système de counters avec compositions identiques
        # Chaque équipe a: 3 Knights, 5 Pikemen, 4 Crossbowmen
        # Mais positionnement différent pour tester les tactiques
        
        # Équipe A: Formation classique mixte
        y = 35
        for i in range(3):
            board.add_unit(Knight(42, y + i*2, 'A'))
        y += 8
        for i in range(5):
            board.add_unit(Pikeman(42, y + i*2, 'A'))
        y += 12
        for i in range(4):
            board.add_unit(Crossbowman(42, y + i*2, 'A'))
        
        # Équipe B: Même composition, formation miroir
        y = 35
        for i in range(3):
            board.add_unit(Knight(78, y + i*2, 'B'))
        y += 8
        for i in range(5):
            board.add_unit(Pikeman(78, y + i*2, 'B'))
        y += 12
        for i in range(4):
            board.add_unit(Crossbowman(78, y + i*2, 'B'))
    
    return Simulation(board, ai1_type="DAFT", ai2_type="DAFT")


if __name__ == "__main__":
    # Test rapide avec vérification des specs
    sim = create_test_scenario("mirror")
    
    print("=== Test de la simulation ===")
    print(f"Unités équipe A: {len(sim.board.get_alive_units('A'))}")
    print(f"Unités équipe B: {len(sim.board.get_alive_units('B'))}")
    
    # Vérification specs prof
    print("\n--- Vérification spécifications ---")
    u = sim.board.units[0]
    print(f"Position flottante: ({u.x}, {u.y}) - Type: {type(u.x).__name__}")
    print(f"Collision radius: {u.collision_radius}")
    print(f"Line of sight: {u.line_of_sight} (circulaire)")
    
    # Simule jusqu'à bataille complète (max 1000 ticks)
    print("\n--- Simulation de bataille ---")
    for i in range(1000):
        sim.step()
        if i % 200 == 0:
            t_a = len(sim.board.get_alive_units('A'))
            t_b = len(sim.board.get_alive_units('B'))
            print(f"t={sim.elapsed_time:5.1f}s: ÉquipeA={t_a:2} vs ÉquipeB={t_b:2}")
        if sim.is_finished():
            print(f"  Bataille terminée au tick {i}")
            break
    
    print(f"\nRésultat après {sim.elapsed_time:.2f}s:")
    t_a_alive = len(sim.board.get_alive_units('A'))
    t_b_alive = len(sim.board.get_alive_units('B'))
    print(f"Unités équipe A: {t_a_alive}")
    print(f"Unités équipe B: {t_b_alive}")
    
    if sim.is_finished():
        winner = 'A' if t_a_alive > 0 else 'B'
        print(f"\nVICTOIRE: Équipe {winner}")
    else:
        print("\nSimulation arrêtée (limite de ticks atteinte)")
