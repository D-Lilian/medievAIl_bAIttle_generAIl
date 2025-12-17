# -*- coding: utf-8 -*-
"""
@file units.py
@brief Unit Definitions - Classes and Enums for game units

@details
Defines UnitType, Team, and the base Unit class along with specific unit implementations.
Contains stats and attributes for all units.

"""
from enum import Enum


class UnitType(Enum):
    CROSSBOWMAN = 1
    KNIGHT = 2
    PIKEMAN = 3
#    LONGSWORDSMAN = 4
#    ELITESKIRMISHER = 5
#    CAVALRYARCHER = 6
#    ONAGER = 7
#    LIGHTCAVALRY = 8
#    SCORPION = 9
#    CAPPEDRAM = 10
#    CASTLE = 11
#    TREBUCHET = 12
    ALL = 0
    NONE = None

class Team(Enum):
    A = 0
    B = 1


class Unit:

    def __init__(self,
                 unit_type: UnitType,
                 name: str,
                 team: Team,
                 hp: int,
                 armor: dict,
                 attack: dict,
                 range: int,
                 size: int,
                 sight: int,
                 speed: float,
                 accuracy: float,
                 reload: float,
                 reload_time: float,
                 x: int,
                 y: int):
        from Model.orders import OrderManager
        self.unit_type = unit_type
        self.name = name
        self.hp = hp                        # <=0 si l'unite est morte
        self.hp_max = hp #pour le graphique on aura besoin pour la barre de vie
        self.team = team                    # choix de l'equipe
        self.armor = armor                  # valeur de l'armure
        self.attack = attack                # nombre de degats infliges
        self.damage_dealt = 0               # degats infliges lors de la derniere attaque
        self.range = range                  # portee de l'unite
        self.size = size                    # taille de l'unite
        self.sight = sight                  # Distance champ de vision
        self.speed = speed                  # vitesse de deplacement
        self.distance_moved = 0             # distance parcourue lors du dernier deplacement
        self.accuracy = accuracy            # precision de l'unite
        self.reload = reload                # avanncement du rechargement, peut attaquer a 0
        self.reload_time = reload_time      # temps pour recharger
        self.x = x                          # coordonnee en X
        self.y = y                          # coordonnee en Y
        self.order_manager = OrderManager()  # ordres donnees par le gerenal
        self.squad_id = None

    def can_attack(self):
        """Check if the unit can perform an attack."""
        return self.reload <= 0

    def perform_attack(self):
        """Perform an attack if the unit can attack. Resets reload timer."""
        if self.can_attack():
            self.reload = self.reload_time
            return True
        return False

    def update_reload(self, t):
        """Decrease reload timer by t simulated seconds."""
        if not self.can_attack():
            self.reload -= t

    def __str__(self):
        return f"{self.unit_type} {self.__hash__()} (Team {self.team}) at ({self.x},{self.y})"

class Crossbowman(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.CROSSBOWMAN, name="Crossbowman", team=team, hp=35, range=5, size=1, sight=5,
                         speed=0.96, accuracy=0.85, reload_time=2.0, x=x, y=y,  reload=0,
                         attack={
                             "Base Pierce": 5,
                             "Spearmen": 3,
                             "Rams": 0,
                             "Standard Buildings": 0,
                             "Stone Defense": 0
                         },
                         armor={
                             "Base Melee": 0,
                             "Base Pierce": 0,
                             "Archers": 0,
                             "Ignore Armor": 0
                         })


class Knight(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.KNIGHT, name="Knight", team=team, hp=100, range=0, size=1, sight=4,
                         speed=1.35, accuracy=1.0, reload_time=1.8, x=x, y=y,  reload=0,
                         attack={
                             "Base Melee": 10,
                             "Archers": 0,
                             "Standard Buildings": 0,
                             "All Buildings": 0,
                             "Skirmishers": 0,
                             "Mounted Unit Resistance": -3
                         },
                         armor={
                             "Base Melee": 2,
                             "Base Pierce": 2,
                             "Cavalry": 0,
                             "Ignore Armor": 0
                         })


class Pikeman(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.PIKEMAN, name="Pikeman", team=team, hp=55, range=0, size=1, sight=4,
                         speed=1.0, accuracy=1.0, reload_time=3.0, x=x, y=y,  reload=0,
                         attack={
                             "Base Melee": 4,
                             "Eagle Warriors": 1,
                             "Cavalry": 22,
                             "Camel Riders": 18,
                             "Mamelukes": 11,
                             "Elephants": 25,
                             "Ships": 16,
                             "Fishing ships": 16,
                             "Standard Buildings": 1
                         },
                         armor={
                             "Base Melee": 0,
                             "Base Pierce": 0,
                             "Infantry": 0,
                             "Spearmen": 0,
                             "Ignore Armor": 0
                         })

#these units have been placed here in case we need to use them.
"""
class LongSwordsman(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.LONGSWORDSMAN, name="Long Swordsman", team=team, hp=60, range=0, size=1, sight=4,
                         speed=0.9, accuracy=1.0, reload_time=2.0, x=x, y=y,  reload=0,
                         attack={
                             "Base Melee": 9,
                             "Eagle Warriors": 6,
                             "Cavalry": 0,
                             "Camel Riders": 0,
                             "Standard Buildings": 3
                         },
                         armor={
                             "Base Melee": 1,
                             "Base Pierce": 1,
                             "Infantry": 0,
                             "Ignore Armor": 0
                         })


class EliteSkirmisher(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.ELITESKIRMISHER, name="Elite Skirmisher", team=team, hp=35, range=5, size=1, sight=7,
                         speed=0.96, accuracy=0.9, reload_time=3.0, x=x, y=y,  reload=0,
                         attack={
                             "Base Pierce": 3,
                             "Archers": 4,
                             "Cavalry Archers": 2,
                             "Spearmen": 4,
                             "Rams": 0,
                             "Standard Buildings": 0
                         },
                         armor={
                             "Base Melee": 0,
                             "Base Pierce": 4,
                             "Archers": 4,
                             "Skirmishers": 0,
                             "Ignore Armor": 0
                         })


class CavalryArcher(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.CAVALRYARCHER, name="Cavalry Archer", team=team, hp=50, range=4, size=1, sight=5,
                         speed=1.4, accuracy=0.5, reload_time=2.0, x=x, y=y,  reload=0,
                         attack={
                             "Base Pierce": 6,
                             "Archers": 0,
                             "Spearmen": 2,
                             "Rams": 0,
                             "Standard Buildings": 0,
                             "Skirmishers": 0,
                             "Mounted Unit Resistance": -3
                         },
                         armor={
                             "Base Melee": 0,
                             "Base Pierce": 0,
                             "Archers": 0,
                             "Cavalry Archers": 0,
                             "SCavalry": 0,
                             "Ignore Armor": 0
                         })


class Onager(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.ONAGER, name="Onager", team=team, hp=60, range=8, size=1, sight=10,
                         speed=0.6, accuracy=1.0, reload_time=6.0, x=x, y=y,  reload=0,
                         attack={
                             "Base Melee": 50,
                             "Siege Weapons": 12,
                             "All Buildings": 45,
                             "Heavy Siege": 50
                         },
                         armor={
                             "Base Melee": 0,
                             "Base Pierce": 7,
                             "Siege Weapons": 0,
                             "Ignore Armor": 0
                         })


class LightCavalry(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.LIGHTCAVALRY, name="Light Cavalry", team=team, hp=60, range=0, size=1, sight=4,
                         speed=1.5, accuracy=1.0, reload_time=2.0, x=x, y=y,  reload=0,
                         attack={
                             "Base Melee": 7,
                             "Archers": 0,
                             "Monks": 10,
                             "Standard Buildings": 0,
                             "All Buildings": 0,
                             "Skirmishers": 0,
                             "Mounted Unit Resistance": -3
                         },
                         armor={
                             "Base Melee": 0,
                             "Base Pierce": 2,
                             "Cavalry": 0,
                             "Ignore Armor": 0
                         })


class Scorpion(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.SCORPION, name="Scorpion", team=team, hp=40, range=7, size=1, sight=9,
                         speed=0.65, accuracy=1.0, reload_time=3.6, x=x, y=y,  reload=0,
                         attack={
                             "Base Melee": 0,
                             "Base Pierce": 12,
                             "Elephants": 6,
                             "Rams": 1,
                             "All Buildings": 2
                         },
                         armor={
                             "Base Melee": 0,
                             "Base Pierce": 7,
                             "Siege Weapons": 0,
                             "Ignore Armor": 0
                         })


class CappedRam(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.CAPPEDRAM, name="Capped Ram", team=team, hp=200, range=0, size=1, sight=3,
                         speed=0.6, accuracy=1.0, reload_time=5.0, x=x, y=y,  reload=0,
                         attack={
                             "Base Melee": 0,
                             "Siege Weapons": 50,
                             "All Buildings": 160
                         },
                         armor={
                             "Base Melee": -3,
                             "Base Pierce": 190,
                             "Siege Weapons": 0,
                             "Rams": 1,
                             "Ignore Armor": 0
                         })


class Castle(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.CASTLE, name="Castel", team=team, hp=4800, range=8, size=1, sight=11,
                         speed=0.0, accuracy=1.0, reload_time=2.0, x=x, y=y,  reload=0,
                         attack={
                             "Base Pierce": 11,
                             "Infantry": 0,
                             "Spearmen": 2,
                             "Camel Riders": 0,
                             "Rams": 0,
                             "Ships": 0,
                             "Fishing Ships": 0,
                             "All Buildings": 0
                         },
                         armor={
                             "Base Melee": 8,
                             "Base Pierce": 11,
                             "Standard Buildings": 0,
                             "All Buildings": 8,
                             "Castles": 0,
                             "Ignore Armor": 8
                         })


class Trebuchet(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.TREBUCHET, name="Trebuchet", team=team, hp=150, range=16, size=1, sight=19,
                         speed=0.0, accuracy=0.15, reload_time=10.0, x=x, y=y,  reload=0,
                         attack={
                             "Base Pierce": 200,
                             "All Buildings": 250
                         },
                         armor={
                             "Base Melee": 1,
                             "Base Pierce": 150,
                             "Siege Weapons": 0,
                             "Rams": 0,
                             "Ignore Armor": 0
                         })
"""
