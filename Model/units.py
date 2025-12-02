from enum import Enum


class Unit:

    def __init__(self, unit_type, name, team, hp, armor, attack, range, size, sight, speed, accuracy, reload,
                 reload_time, x, y, order_manager):
        self.unit_type = unit_type
        self.name = name
        self.hp = hp                        # <=0 si l'unite est morte
        self.team = team                    # choix de l'equipe
        self.armor = armor                  # valeur de l'armure
        self.attack = attack                # nombre de degats infliges
        self.range = range                  # portee de l'unite
        self.size = size                    # taille de l'unite
        self.sight = sight                  # Distance champ de vision
        self.speed = speed                  # vitesse de deplacement
        self.accuracy = accuracy            # precision de l'unite
        self.reload = reload                # avanncement du rechargement, peut attaquer a 0
        self.reload_time = reload_time      # temps pour recharger
        self.x = x                          # coordonnee en X
        self.y = y                          # coordonnee en Y
        self.order_manager = order_manager  # ordres donnees par le gerenal

    def can_attack(self):
        """Check if the unit can perform an attack."""
        return self.reload <= 0

    def attack(self):
        """Perform an attack if the unit can attack. Resets reload timer."""
        if self.can_attack():
            self.reload = self.reload_time
            return True
        return False

    def update_reload(self, t):
        """Decrease reload timer by t simulated seconds."""
        if not self.can_attack():
            self.reload -= t


class UnitType(Enum):
    CROSSBOWMAN = "Crossbowman"
    KNIGHT = "Knight"
    PIKEMAN = "Pikeman"


class Crossbowman(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.CROSSBOWMAN, name="Crossbowman", team=team, hp=35, range=5, size=1,
                         sight=5, speed=0.96, accuracy=0.85, reload_time=2.0, x=x, y=y,
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
                         speed=1.35, accuracy=1.0, reload_time=1.8, x=x, y=y,
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
                         speed=1.0, accuracy=1.0, reload_time=3.0, x=x, y=y,
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
