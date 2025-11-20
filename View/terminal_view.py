# -*- coding: utf-8 -*-
"""
@file terminal_view.py
@brief Terminal View - Vue curses pour bataille médiévale

@details
Implémentation MVC : affiche l'état du Model sans le modifier
- Mode interactif (curses)  
- Mode headless (tests)
- Compatible équipes A/B

@author Marie
@date 2025

@usage
python terminal_view.py [--test]

@controls
P(pause) M(zoom) ZQSD(scroll) ESC(quit)
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum, auto
import curses
from typing import List
import time
import sys


class Team(Enum):
    """
    @brief Énumération des équipes possibles
    
    @details Définit les identifiants d'équipe pour le jeu.
    Compatible avec la nomenclature des collègues (A/B).
    """
    A = 1  ##< Équipe A (cyan)
    B = 2  ##< Équipe B (rouge)


class UnitStatus(Enum):
    """
    @brief Statut d'une unité dans le jeu
    
    @details Indique si une unité est vivante ou morte,
    utilisé pour l'affichage et la logique de jeu.
    """
    ALIVE = auto()  ##< Unité vivante
    DEAD = auto()   ##< Unité morte


@dataclass
class UniteRepr:
    """
    @brief Représentation d'une unité pour l'affichage
    
    @details Structure de données contenant toutes les informations
    nécessaires à l'affichage d'une unité dans la vue terminal.
    Sépare clairement les données Model des données View.
    
    @param type Nom du type d'unité (Knight, Pikeman, etc.)
    @param team Équipe de l'unité (Team.A ou Team.B)
    @param letter Caractère d'affichage de l'unité
    @param x Position X (coordonnée flottante)
    @param y Position Y (coordonnée flottante)
    @param hp Points de vie actuels
    @param hp_max Points de vie maximum
    @param status Statut de l'unité (ALIVE/DEAD)
    """
    type: str
    team: Team
    letter: str
    x: float
    y: float
    hp: int
    hp_max: int
    status: UnitStatus
    
    @property
    def alive(self) -> bool:
        """
        @brief Vérifie si l'unité est vivante
        @return True si l'unité est vivante, False sinon
        """
        return self.status == UnitStatus.ALIVE
    
    @property
    def hp_percent(self) -> float:
        """
        @brief Calcule le pourcentage de HP restants
        @return Pourcentage de HP (0-100)
        """
        return (self.hp / self.hp_max * 100) if self.hp_max > 0 else 0.0


class ViewInterface(ABC):
    """
    @brief Interface abstraite pour toutes les vues
    
    @details Définit le contrat que toutes les vues doivent respecter
    dans l'architecture MVC. Garantit la séparation entre View et Model.
    """
    
    @abstractmethod
    def update(self, simulation):
        """
        @brief Met à jour l'affichage avec l'état actuel de la simulation
        @param simulation Instance de simulation contenant l'état du jeu
        @return bool True pour continuer, False pour quitter
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """
        @brief Nettoie les ressources de la vue
        @details Libère les ressources (curses, fichiers, etc.)
        """
        pass


class ColorPair(Enum):
    """
    @brief Paires de couleurs pour l'affichage curses
    
    @details Définit les couleurs utilisées pour différencier
    les équipes et éléments d'interface.
    """
    TEAM_A = 1   ##< Cyan pour équipe A
    TEAM_B = 2   ##< Rouge pour équipe B
    UI = 3       ##< Jaune pour l'interface
    DEAD = 4     ##< Gris pour les unités mortes


@dataclass
class Camera:
    """
    @brief Gestion de la position et du zoom de la caméra
    
    @details Encapsule toute la logique de déplacement et zoom de la caméra.
    Applique le principe de responsabilité unique (SOLID).
    
    @param x Position X de la caméra
    @param y Position Y de la caméra  
    @param zoom_level Niveau de zoom (1=normal, 2=zoom out)
    @param scroll_speed_normal Vitesse de défilement normale
    @param scroll_speed_fast Vitesse de défilement rapide (Shift)
    """
    x: int = 0
    y: int = 0
    zoom_level: int = 1
    scroll_speed_normal: int = 2
    scroll_speed_fast: int = 5
    
    def move(self, dx: int, dy: int, fast: bool = False):
        """
        @brief Déplace la caméra
        @param dx Déplacement en X (-1, 0, 1)
        @param dy Déplacement en Y (-1, 0, 1) 
        @param fast True pour déplacement rapide (Shift pressé)
        """
        speed = self.scroll_speed_fast if fast else self.scroll_speed_normal
        self.x += dx * speed
        self.y += dy * speed
    
    def toggle_zoom(self):
        """
        @brief Bascule entre zoom normal et zoom out
        @details Alterne entre zoom_level 1 (normal) et 2 (zoom out)
        """
        self.zoom_level = 1 if self.zoom_level == 2 else 2
    
    def clamp(self, board_width: int, board_height: int, term_w: int, term_h: int, ui_height: int = 0):
        """
        @brief Contraint la caméra aux limites du plateau
        @param board_width Largeur du plateau de jeu
        @param board_height Hauteur du plateau de jeu
        @param term_w Largeur du terminal
        @param term_h Hauteur du terminal
        @param ui_height Hauteur de l'interface utilisateur
        """
        visible_w = int(term_w * self.zoom_level)
        visible_h = int((term_h - ui_height) * self.zoom_level)
        max_x = max(0, board_width - visible_w)
        max_y = max(0, board_height - visible_h)
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))


class TerminalView(ViewInterface):
    """
    @brief Vue Terminal utilisant curses pour afficher la bataille
    
    @details Implémentation principale de la vue dans l'architecture MVC.
    Fournit un affichage terminal avec curses pour visualiser les batailles
    en temps réel. Supporte les modes interactif et headless.
    
    @features
    - Affichage coloré des unités par équipe
    - Contrôles clavier (pause, zoom, scroll)
    - Mode headless pour tests automatisés
    - Génération de rapports HTML
    - Compatible équipes A/B
    
    @controls
    - P: Pause/Resume
    - M: Toggle zoom
    - ZQSD/Flèches: Déplacement caméra
    - +/-: Ajuster vitesse
    - TAB: Générer rapport HTML
    - ESC: Quitter
    """
    
    ##< @brief Mapping des types d'unités vers leurs lettres d'affichage
    UNIT_LETTERS = {
        'Knight': 'K',           ##< Chevalier
        'Pikeman': 'P',          ##< Piquier  
        'Crossbowman': 'C',      ##< Arbalétrier
        'Long Swordsman': 'L',   ##< Épéiste
        'Elite Skirmisher': 'S', ##< Éclaireur d'élite
        'Cavalry Archer': 'A',   ##< Archer à cheval
        'Onager': 'O',           ##< Onagre
        'Light Cavalry': 'V',    ##< Cavalerie légère
        'Scorpion': 'R',         ##< Scorpion
        'Capped Ram': 'M',       ##< Bélier
        'Trebuchet': 'T',        ##< Trébuchet
        'Elite War Elephant': 'E', ##< Éléphant de guerre d'élite
        'Monk': 'N',             ##< Moine
        'Castle': '#',           ##< Château
        'Wonder': 'W'            ##< Merveille
    }
    
    def __init__(self, board_width: int, board_height: int, tick_speed: int = 20):
        """
        @brief Initialise la vue terminal
        
        @param board_width Largeur du plateau de jeu
        @param board_height Hauteur du plateau de jeu  
        @param tick_speed Nombre de ticks par seconde (framerate)
        
        @details Configure tous les paramètres nécessaires à l'affichage:
        caméra, état de la vue, cache des unités, statistiques.
        """
        self.board_width = board_width
        self.board_height = board_height
        self.tick_speed = tick_speed
        
        # Caméra
        self.camera = Camera()
        
        # État de la vue
        self.paused = False
        self.show_debug = False
        self.show_ui = True
        
        # Fenêtre curses
        self.stdscr = None
        self.windows = {}
        
        # Cache pour les unités
        self.units_cache: List[UniteRepr] = []
        
        # Stats
        self.team1_units = 0
        self.team2_units = 0
        self.simulation_time = 0.0
        self.dead_team1 = 0
        self.dead_team2 = 0
        self.type_counts_team1 = {}
        self.type_counts_team2 = {}
        self.unit_hp_memory = {}  # id(unit) -> hp_max estimé
        
        # FPS
        self.fps = 0.0
        self._last_frame_time = time.perf_counter()
        # Suivi des unités récemment mortes pour les faire clignoter
        self._death_times = {}  # id(unit_repr) -> time_of_death
        
    def init_curses(self):
        """
        @brief Initialise l'environnement curses
        
        @details Configure curses pour l'affichage terminal:
        - Initialise l'écran et les couleurs
        - Configure l'entrée clavier non-bloquante
        - Définit les paires de couleurs pour les équipes
        
        @note À appeler avant toute utilisation de l'affichage curses
        """
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)  # Cache le curseur
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)  # Non bloquant pour les inputs
        
        # Initialisation des paires de couleurs
        curses.init_pair(ColorPair.TEAM_A.value, curses.COLOR_CYAN, -1)
        curses.init_pair(ColorPair.TEAM_B.value, curses.COLOR_RED, -1)
        curses.init_pair(ColorPair.UI.value, curses.COLOR_YELLOW, -1)
        curses.init_pair(ColorPair.DEAD.value, curses.COLOR_BLACK, -1)
        
    def cleanup(self):
        """
        @brief Nettoie et restaure l'environnement terminal
        
        @details Restaure le terminal à son état normal:
        - Désactive l'écho clavier
        - Restaure le mode canonique
        - Libère l'écran curses
        
        @note À appeler impérativement en fin de programme
        """
        if self.stdscr:
            self.stdscr.keypad(False)
            curses.nocbreak()
            curses.echo()
            curses.endwin()
    
    def handle_input(self) -> bool:
        """
        @brief Gère les entrées clavier utilisateur
        
        @details Traite toutes les interactions clavier:
        - Navigation: ZQSD, flèches (avec vitesse Shift)
        - Zoom: M (cycle entre niveaux)
        - Contrôles: P(pause), +/-(vitesse), TAB(rapport), F(UI), D(debug)
        - Sortie: Échap
        
        @return bool False pour quitter l'application, True pour continuer
        @note Utilise getch() non-bloquant pour éviter les freezes
        """
        try:
            key = self.stdscr.getch()
        except (KeyboardInterrupt, curses.error):
            return True
        
        if key == -1:  # Pas d'entrée
            return True
        
        # Ajustement vitesse ticks
        if key in (ord('+'), ord('=')):
            self.tick_speed = min(240, self.tick_speed + 5)
            return True
        if key in (ord('-'), ord('_')):
            self.tick_speed = max(1, self.tick_speed - 5)
            return True
        
        # Pause/Resume
        if key in (ord('p'), ord('P')):
            self.paused = not self.paused
            return True
        
        # Zoom
        if key in (ord('m'), ord('M')):
            self.camera.toggle_zoom()
            return True
        
        # Debug view
        if key in (ord('d'), ord('D')):
            self.show_debug = not self.show_debug
            return True
        
        # Toggle UI
        if key in (ord('f'), ord('F')):
            self.show_ui = not self.show_ui
            return True
        
        # Génération HTML
        if key == ord('\t'):  # TAB
            self.generate_html_report()
            return True
        
        # Quitter
        if key == 27:  # ESC uniquement
            return False
        
        # Scroll avec ZQSD
        if key in (ord('z'), ord('Z'), curses.KEY_UP):
            fast = key == ord('Z')
            self.camera.move(0, -1, fast)
        elif key in (ord('s'), ord('S'), curses.KEY_DOWN):
            fast = key == ord('S')
            self.camera.move(0, 1, fast)
        elif key in (ord('q'), ord('Q'), curses.KEY_LEFT):
            fast = key == ord('Q')
            self.camera.move(-1, 0, fast)
        elif key in (ord('d'), ord('D'), curses.KEY_RIGHT):
            fast = key == ord('D')
            self.camera.move(1, 0, fast)
        
        return True
    
    def _resolve_letter(self, unit_type: str) -> str:
        """Retourne la lettre pour un type ou '?' par défaut."""
        return self.UNIT_LETTERS.get(unit_type, unit_type[:1].upper() if unit_type else '?')
    
    def _get_unit_display_attributes(self, unit: UniteRepr) -> tuple[str, ColorPair, int]:
        """
        @brief Détermine les attributs visuels d'affichage d'une unité
        
        @param unit Unité à afficher
        @return tuple Triplet (caractère, couleur, attributs_curses)
        
        @details Logique d'affichage:
        - Unités vivantes: lettre de type + couleur équipe + gras
        - Unités mortes: 'x' gris + clignotement
        """
        if unit.alive:
            color = ColorPair.TEAM_A if unit.team == Team.A else ColorPair.TEAM_B
            char = unit.letter
            attr = curses.color_pair(color.value) | curses.A_BOLD
        else:
            # Unités mortes : 'x' en gris avec clignotement
            color = ColorPair.DEAD
            char = 'x'
            attr = curses.color_pair(color.value) | curses.A_BLINK
        
        return char, color, attr

    def _draw_border(self, width: int, height: int):
        """
        @brief Dessine un cadre décoratif autour du plateau de jeu
        
        @param width Largeur du cadre en caractères
        @param height Hauteur du cadre en caractères
        
        @details Utilise des caractères Unicode pour un rendu professionnel:
        - Coins: ┌┐└┘  
        - Bordures: ─ │
        - Couleur UI distinctive
        """
        ui_color = curses.color_pair(ColorPair.UI.value)
        try:
            # Coins
            self.stdscr.addch(0, 0, '┌', ui_color)
            self.stdscr.addch(0, width - 1, '┐', ui_color)
            self.stdscr.addch(height - 1, 0, '└', ui_color)
            self.stdscr.addch(height - 1, width - 1, '┘', ui_color)
            
            # Lignes horizontales
            for x in range(1, width - 1):
                self.stdscr.addch(0, x, '─', ui_color)
                self.stdscr.addch(height - 1, x, '─', ui_color)
            
            # Lignes verticales
            for y in range(1, height - 1):
                self.stdscr.addch(y, 0, '│', ui_color)
                self.stdscr.addch(y, width - 1, '│', ui_color)
        except curses.error:
            pass  # Ignore les erreurs si le terminal est trop petit

    def _extract_unit_fields(self, unit):
        """Adapte les différences de noms d'attributs du model."""
        # team/equipe
        team = getattr(unit, 'equipe', getattr(unit, 'team', 1))
        # hp / hp_max
        hp = getattr(unit, 'hp', 0)
        # hp_max: si absent, mémoriser la première valeur vivante
        if hasattr(unit, 'hp_max'):
            hp_max = getattr(unit, 'hp_max')
        else:
            uid = id(unit)
            if uid not in self.unit_hp_memory and hp > 0:
                self.unit_hp_memory[uid] = hp
            hp_max = self.unit_hp_memory.get(uid, hp)
        # type/name
        unit_type = getattr(unit, 'name', type(unit).__name__)
        # position
        x = getattr(unit, 'x', 0.0)
        y = getattr(unit, 'y', 0.0)
        # alive()
        alive = hp > 0
        # stats facultatives
        armor = getattr(unit, 'armor', None)
        attack = getattr(unit, 'attack', None)
        rng = getattr(unit, 'range', None)
        reload_time = getattr(unit, 'reload_time', None)
        reload_val = getattr(unit, 'reload', None)
        return {
            'team': team, 'hp': hp, 'hp_max': hp_max, 'type': unit_type,
            'x': x, 'y': y, 'alive': alive,
            'armor': armor, 'attack': attack, 'range': rng,
            'reload_time': reload_time, 'reload_val': reload_val
        }

    def update_units_cache(self, simulation):
        """
        Met à jour le cache des unités depuis la simulation
        
        Args:
            simulation: Instance de la simulation contenant les unités
        """
        # self.units_cache.clear()
        self.units_cache.clear()
        self.team1_units = 0
        self.team2_units = 0
        self.dead_team1 = 0
        self.dead_team2 = 0
        self.type_counts_team1 = {}
        self.type_counts_team2 = {}
        
        # Récupération des unités depuis la simulation
        # Adapté selon votre architecture Model
        if hasattr(simulation, 'board') and hasattr(simulation.board, 'units'):
            for unit in simulation.board.units:
                if not hasattr(unit, 'hp'):
                    continue
                fields = self._extract_unit_fields(unit)
                letter = self._resolve_letter(fields['type'])
                status = UnitStatus.ALIVE if fields['alive'] else UnitStatus.DEAD
                # Support pour team = 1/2, 'A'/'B', ou Team.A/Team.B
                team_val = fields['team']
                if isinstance(team_val, Team):
                    team = team_val
                elif team_val in (1, 'A', 'a'):
                    team = Team.A
                else:
                    team = Team.B
                
                repr_obj = UniteRepr(
                    type=fields['type'],
                    team=team,
                    letter=letter,
                    x=fields['x'],
                    y=fields['y'],
                    hp=max(0, fields['hp']),
                    hp_max=fields['hp_max'],
                    status=status
                )
                self.units_cache.append(repr_obj)

                # Enregistrer l'heure de décès pour clignotement temporaire
                uid = id(repr_obj)
                if not fields['alive']:
                    # Si l'unité vient de mourir, mémoriser le temps
                    if uid not in self._death_times:
                        self._death_times[uid] = time.perf_counter()
                else:
                    # Si elle est vivante, s'assurer qu'elle n'est pas marquée comme morte
                    if uid in self._death_times:
                        del self._death_times[uid]
                
                # Comptages (supporter team = 1/2, 'A'/'B' ou Team enum)
                team_val = fields['team']
                if isinstance(team_val, Team):
                    is_team_a = (team_val == Team.A)
                elif team_val in (1, 'A', 'a'):
                    is_team_a = True
                else:
                    is_team_a = False
                    
                target_counts = self.type_counts_team1 if is_team_a else self.type_counts_team2
                
                if fields['alive']:
                    target_counts[fields['type']] = target_counts.get(fields['type'], 0) + 1
                    if is_team_a:
                        self.team1_units += 1
                    else:
                        self.team2_units += 1
                else:
                    if is_team_a:
                        self.dead_team1 += 1
                    else:
                        self.dead_team2 += 1
        
        # Mise à jour du temps de simulation
        if hasattr(simulation, 'elapsed_time'):
            self.simulation_time = simulation.elapsed_time
    
    def draw_map(self):
        """
        @brief Dessine la carte et les unités sur l'écran
        
        @details Fonction principale de rendu qui:
        - Efface l'écran précédent
        - Calcule la zone d'affichage disponible  
        - Applique les contraintes de caméra
        - Dessine le cadre, unités et éléments visuels
        
        @note Appelée à chaque frame pour mettre à jour l'affichage
        """
        max_y, max_x = self.stdscr.getmaxyx()
        
        # Efface l'écran
        self.stdscr.clear()
        
        # Zone de jeu (laisse de la place pour l'UI en bas)
        game_height = max_y - (5 if self.show_ui else 0)
        
        # Contrainte caméra
        ui_height = 5 if self.show_ui else 0
        self.camera.clamp(self.board_width, self.board_height, max_x, max_y, ui_height)
        
        # Dessine le cadre autour du plateau de jeu
        self._draw_border(max_x, game_height)
        
        # Dessin direct (sans grille intermédiaire)
        # Ajuste pour laisser 1 ligne/colonne pour le cadre
        now = time.perf_counter()
        for unit in self.units_cache:
            # Position sur l'écran avec zoom et caméra
            screen_x = int((unit.x - self.camera.x) / self.camera.zoom_level) + 1  # +1 pour le cadre
            screen_y = int((unit.y - self.camera.y) / self.camera.zoom_level) + 1  # +1 pour le cadre
            
            # Vérification des limites (en tenant compte du cadre)
            if 1 <= screen_x < max_x - 1 and 1 <= screen_y < game_height - 1:
                # Affichage distinct pour les unités mortes
                if unit.alive:
                    color = self.COLOR_TEAM1 if unit.team == 1 else self.COLOR_TEAM2
                    char = unit.letter
                    attr = curses.color_pair(color) | curses.A_BOLD
                else:
                    # Unités mortes : caractère 'x' en gris
                    color = self.COLOR_DEAD
                    char = 'x'
                    # Clignotement pendant une courte période après la mort
                    blink = False
                    uid = id(unit)
                    death_time = self._death_times.get(uid)
                    if death_time is not None and (now - death_time) < 2.0:
                        blink = True
                    attr = curses.color_pair(color)
                    if blink:
                        attr |= curses.A_BLINK
                try:
                    self.stdscr.addstr(screen_y, screen_x, char, attr)
                except curses.error:
                    pass  # Ignore les erreurs en bordure d'écran
    
    def draw_ui(self):
        """
        @brief Dessine l'interface utilisateur
        
        @details Affiche en bas de l'écran:
        - Ligne de séparation avec la zone de jeu
        - Statistiques des équipes (unités, santé)
        - Commandes de contrôle disponibles
        - Informations de caméra et zoom
        
        @note Uniquement si self.show_ui est True
        """
        if not self.show_ui:
            return
        
        max_y, max_x = self.stdscr.getmaxyx()
        ui_start_y = max_y - 5
        
        # Ligne de séparation
        try:
            self.stdscr.addstr(ui_start_y, 0, "─" * max_x, curses.color_pair(ColorPair.UI.value))
        except curses.error:
            pass
        
        stats_line = (
            f"Temps:{self.simulation_time:.1f}s | Éq1 V:{self.team1_units} M:{self.dead_team1} | "
            f"Éq2 V:{self.team2_units} M:{self.dead_team2} | Total:{len(self.units_cache)} | FPS:{self.fps:.0f}"
        )
        try:
            self.stdscr.addstr(ui_start_y + 1, 2, stats_line, curses.color_pair(ColorPair.UI.value) | curses.A_BOLD)
        except curses.error:
            pass
        
        state_line = (
            f"{'PAUSE' if self.paused else 'PLAY'} | Zoom:x{self.camera.zoom_level} "
            f"| Caméra:({self.camera.x},{self.camera.y}) | Tick:{self.tick_speed}"
        )
        try:
            self.stdscr.addstr(ui_start_y + 2, 2, state_line)
        except curses.error:
            pass
        
        # Ligne des types principaux (archer/knight/pikeman si présents)
        summary = []
        for label in ['Archer', 'Knight', 'Pikeman']:
            c1 = self.type_counts_team1.get(label, 0)
            c2 = self.type_counts_team2.get(label, 0)
            if c1 or c2:
                summary.append(f"{label}:{c1}/{c2}")
        types_line = " | ".join(summary)
        if types_line:
            try:
                self.stdscr.addstr(ui_start_y + 3, 2, types_line, curses.color_pair(ColorPair.UI.value))
            except curses.error:
                pass
        
        # Commandes (décalée si types_line vide ou non)
        commands_y = ui_start_y + (4 if types_line else 3)
        commands_line = "P:Pause M:Zoom +/-:Tick ZQSD/Flèches:Scroll TAB:Rapport F:UI D:Debug ESC:Quitter"
        try:
            self.stdscr.addstr(commands_y, 2, commands_line, curses.color_pair(ColorPair.UI.value))
        except curses.error:
            pass
    
    def draw_debug_info(self):
        """
        @brief Affiche des informations de debug en overlay
        
        @details Mode développeur qui affiche:
        - Détails des 5 premières unités (position, santé, équipe)
        - Informations système si nécessaire
        - État interne pour diagnostic
        
        @note Uniquement si self.show_debug est True (touche D)
        """
        if not self.show_debug:
            return
        
        max_y, max_x = self.stdscr.getmaxyx()
        
        # Affiche les 5 premières unités avec leurs infos détaillées
        debug_y = 1
        try:
            self.stdscr.addstr(debug_y, max_x - 48, "═══ DEBUG ═══", curses.color_pair(ColorPair.UI.value) | curses.A_BOLD)
            debug_y += 1
            
            for i, unit in enumerate(self.units_cache[:6]):
                status = "ALV" if unit.alive else "DED"
                debug_text = f"{status} {unit.type[:10]:10} ({unit.letter}) HP:{unit.hp:3}/{unit.hp_max:3} {unit.hp_percent:3.0f}%"
                color = ColorPair.TEAM1 if unit.team == Team.TEAM1 else ColorPair.TEAM2
                if not unit.alive:
                    color = ColorPair.DEAD
                self.stdscr.addstr(debug_y + i, max_x - 48, debug_text[:48], curses.color_pair(color.value))
        except curses.error:
            pass
    
    def update(self, simulation):
        """
        Met à jour l'affichage avec l'état actuel de la simulation
        
        Args:
            simulation: Instance de Simulation du Model
        """
        # Gère les entrées utilisateur
        if not self.handle_input():
            return False  # Signal pour quitter
        
        # Si en pause, on ne met pas à jour le cache mais on redessine
        if not self.paused:
            self.update_units_cache(simulation)
        
        self.draw_map()
        self.draw_ui()
        self.draw_debug_info()
        
        # Rafraîchit l'écran
        self.stdscr.refresh()
        
        # Calcul FPS avant sleep
        now = time.perf_counter()
        dt = now - self._last_frame_time
        if dt > 0:
            self.fps = 1.0 / dt
        self._last_frame_time = now
        
        # Contrôle du framerate
        time.sleep(max(0.0, 1.0 / self.tick_speed))
        
        return True
    
    def generate_html_report(self):
        """
        Génère un rapport HTML avec l'état actuel de toutes les unités
        Appelé avec la touche TAB
        """
        import datetime
        import os
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"battle_report_{timestamp}.html"
        
        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Battle Report - {timestamp}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            text-align: center;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .stats {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .team-section {{
            margin: 20px 0;
        }}
        .team1 {{ color: #00bcd4; }}
        .team2 {{ color: #f44336; }}
        .unit-list {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .unit {{
            padding: 10px;
            margin: 5px 0;
            background: #fafafa;
            border-left: 4px solid #ddd;
            border-radius: 4px;
        }}
        .unit.team1 {{ border-left-color: #00bcd4; }}
        .unit.team2 {{ border-left-color: #f44336; }}
        .unit-header {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .unit-details {{
            font-size: 0.9em;
            color: #666;
        }}
        .hp-bar {{
            height: 10px;
            background: #ddd;
            border-radius: 5px;
            overflow: hidden;
            margin-top: 5px;
        }}
        .hp-fill {{
            height: 100%;
            background: #4CAF50;
            transition: width 0.3s;
        }}
        .hp-low {{ background: #ff9800; }}
        .hp-critical {{ background: #f44336; }}
        details {{
            margin: 10px 0;
        }}
        summary {{
            cursor: pointer;
            padding: 10px;
            background: #4CAF50;
            color: white;
            border-radius: 4px;
            font-weight: bold;
        }}
        summary:hover {{
            background: #45a049;
        }}
    </style>
</head>
<body>
    <h1>Battle Report</h1>
    
    <div class="stats">
        <h2>Statistiques Générales</h2>
        <p><strong>Temps de simulation:</strong> {self.simulation_time:.2f} secondes</p>
        <p><strong>Équipe 1:</strong> <span class="team1">{self.team1_units} unités</span></p>
        <p><strong>Équipe 2:</strong> <span class="team2">{self.team2_units} unités</span></p>
        <p><strong>Total:</strong> {len(self.units_cache)} unités actives</p>
    </div>
"""
        
        # Séparer les unités par équipe
        team1_units = [u for u in self.units_cache if u.team == Team.TEAM1]
        team2_units = [u for u in self.units_cache if u.team == Team.TEAM2]
        
        for team_num, team_units in [(1, team1_units), (2, team2_units)]:
            html_content += f"""
    <div class="team-section">
        <details open>
            <summary>Équipe {team_num} - {len(team_units)} unités</summary>
            <div class="unit-list">
"""
            
            for i, unit in enumerate(team_units, 1):
                hp_percent = (unit.hp / unit.hp_max) * 100 if unit.hp_max > 0 else 0
                hp_class = "hp-critical" if hp_percent < 25 else "hp-low" if hp_percent < 50 else ""
                
                status_label = "Alive" if unit.alive else "Dead"
                html_content += f"""
                <div class="unit team{team_num}">
                    <div class="unit-header">
                        #{i} - {unit.type} ({unit.letter}) - Position: ({unit.x:.1f}, {unit.y:.1f}) - {status_label}
                    </div>
                    <div class="unit-details">
                        HP: {unit.hp}/{unit.hp_max} ({hp_percent:.1f}%)
                    </div>
                    <div class="hp-bar">
                        <div class="hp-fill {hp_class}" style="width: {hp_percent}%"></div>
                    </div>
                </div>
"""
            
            html_content += """
            </div>
        </details>
    </div>
"""
        
        html_content += """
    <div class="stats">
        <h2>Légende des Unités</h2>
        <ul>
"""
        
        for unit_type, letter in sorted(self.UNIT_LETTERS.items()):
            html_content += f"            <li><strong>{letter}</strong>: {unit_type}</li>\n"
        
        html_content += """
        </ul>
    </div>
    
    <footer style="text-align: center; margin-top: 40px; color: #666;">
        <p>Généré le """ + datetime.datetime.now().strftime("%d/%m/%Y à %H:%M:%S") + """</p>
    </footer>
</body>
</html>
"""
        
        # Sauvegarde du fichier
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Ouvre le fichier dans le navigateur
            import webbrowser
            webbrowser.open('file://' + os.path.abspath(filename))
            
        except Exception:
            # En cas d'erreur, on ne fait rien (le jeu continue)
            pass

    def debug_snapshot(self) -> dict:
        """Retourne un snapshot des stats courantes (pour tests)."""
        return {
            "time": self.simulation_time,
            "team1_alive": self.team1_units,
            "team2_alive": self.team2_units,
            "team1_dead": self.dead_team1,
            "team2_dead": self.dead_team2,
            "types_team1": dict(self.type_counts_team1),
            "types_team2": dict(self.type_counts_team2),
            "total_units_cached": len(self.units_cache)
        }

    def run_headless(self, simulation, ticks: int = 10):
        """Exécute quelques ticks sans curses pour tests automatisés."""
        for _ in range(ticks):
            if not self.paused:
                simulation.step() if hasattr(simulation, "step") else None
                self.update_units_cache(simulation)
        return self.debug_snapshot()


def create_dummy_simulation():
    """Fixture de simulation simple pour tests unitaires."""
    class DummyUnit:
        def __init__(self, x, y, equipe, unit_type, hp, hp_max):
            self.x = x
            self.y = y
            self.equipe = equipe
            self.hp = hp
            self.hp_max = hp_max
            self.name = unit_type

    class DummyBoard:
        def __init__(self):
            self.units = []
            # Formation miroir : équipe 1 à gauche, équipe 2 à droite
            formations = [
                ('Knight', 100, 100),
                ('Pikeman', 55, 55),
                ('Crossbowman', 30, 30),
            ]
            
            # Équipe A (gauche) - Cyan
            for i, (unit_type, hp, hp_max) in enumerate(formations):
                self.units.append(DummyUnit(20, 30 + i*5, 'A', unit_type, hp, hp_max))
            
            # Équipe B (droite) - Rouge - miroir exact
            for i, (unit_type, hp, hp_max) in enumerate(formations):
                self.units.append(DummyUnit(100, 30 + i*5, 'B', unit_type, hp, hp_max))

    class DummySimulation:
        def __init__(self):
            self.board = DummyBoard()
            self.elapsed_time = 0.0
        def step(self):
            # Les deux équipes s'approchent l'une de l'autre
            for u in self.board.units:
                if u.hp > 0:
                    u.x += 0.3 if u.equipe == 1 else -0.3
            self.elapsed_time += 0.05

    return DummySimulation()

def main_test():
    """Mode test headless: python terminal_view.py --test"""
    sim = create_dummy_simulation()
    view = TerminalView(120, 120)
    
    print("=== Mode Test Headless ===")
    print("Simulation: 50 ticks avec dummy data")
    
    snapshot = view.run_headless(sim, ticks=50)
    
    print("\nRésultats:")
    print(f"  Temps simulé: {snapshot['time']:.2f}s")
    print(f"  Équipe 1: {snapshot['team1_alive']} vivants, {snapshot['team1_dead']} morts")
    print(f"  Équipe 2: {snapshot['team2_alive']} vivants, {snapshot['team2_dead']} morts")
    print(f"  Types équipe 1: {snapshot['types_team1']}")
    print(f"  Types équipe 2: {snapshot['types_team2']}")
    print(f"  Total unités: {snapshot['total_units_cached']}")
    
    # Génération facultative du rapport HTML (désactivée par défaut)
    # view.generate_html_report()
    
    print("\nTest headless: OK")


def main_demo():
    """Fonction de démonstration de la vue terminal"""
    
    # Classe factice de simulation pour la démo
    class DummyUnit:
        def __init__(self, x, y, equipe, unit_type, hp, hp_max):
            self.x = x
            self.y = y
            self.equipe = equipe
            self.hp = hp
            self.hp_max = hp_max
            self.name = unit_type
    
    class DummyBoard:
        def __init__(self):
            self.units = []
            # Formations face à face : équipe 1 à gauche, équipe 2 à droite
            formations = [
                ('Knight', 100, 100),
                ('Knight', 100, 100),
                ('Pikeman', 55, 55),
                ('Pikeman', 55, 55),
                ('Crossbowman', 35, 35),
                ('Crossbowman', 35, 35),
                ('Long Swordsman', 60, 60),
            ]
            
            # Équipe A (gauche, cyan)
            for i, (unit_type, hp, hp_max) in enumerate(formations):
                self.units.append(DummyUnit(15, 20 + i*3, 'A', unit_type, hp, hp_max))
            
            # Équipe B (droite, rouge) - formation miroir
            for i, (unit_type, hp, hp_max) in enumerate(formations):
                self.units.append(DummyUnit(105, 20 + i*3, 'B', unit_type, hp, hp_max))
    
    class DummySimulation:
        def __init__(self):
            self.board = DummyBoard()
            self.elapsed_time = 0.0
        
        def step(self):
            # Les deux armées se rapprochent
            for unit in self.board.units:
                if unit.equipe == 1:
                    unit.x += 0.5
                else:
                    unit.x -= 0.5
            self.elapsed_time += 0.05
    
    # Création de la vue
    view = TerminalView(120, 120, tick_speed=20)
    
    try:
        view.init_curses()
        simulation = DummySimulation()
        
        # Boucle principale
        running = True
        while running:
            if not view.paused:
                simulation.step()
            
            running = view.update(simulation)
            
    finally:
        view.cleanup()


if __name__ == "__main__":
    if "--test" in sys.argv:
        main_test()
    else:
        main_demo()
