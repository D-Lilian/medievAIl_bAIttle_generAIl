from enum import Enum

class Unit:
    
    def __init__(self, unit_type, name, team, hp, armor, attack, range, size, sight, speed, accuracy, reload, reload_time, x, y, Order_Manager, bonus_attack):
        self.unit_type = unit_type
        self.name =name 
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
        self.Order_Manager = Order_Manager  # ordres donnees par le gerenal
        self.bonus_attack = bonus_attack    # bonnus d'ataque selon l'unite attaquee
    
    def can_attack(self):
        """Check if the unit can perform an attack."""
        return self.reload <= 0

    def attach(self):
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
    ARCHER = "Archer"
    KNIGHT = "Knight"
    PIKEMAN = "Pikeman"

class Archer(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.ARCHER , name = "Archer", team = team, hp = 30, armor = 0, attack = 4, range = 4, size = 1, sight = 6, speed = 0.96, accuracy = 0.8, reload_time = 2.0, x = x, y = y, bonus_attack={"Spearmen":3 , "Base Pierce":4})

class Knight(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.KNIGHT , name = "Knight", team = team, hp = 100, armor = 2, attack = 10, range = 0, size = 1, sight = 4, speed = 1.35, accuracy = 1.0, reload_time = 1.8, x = x, y = y, bonus_attack={"Base Melee":10 , "Cavalry Resistance":-3})

class Pikeman(Unit):
    def __init__(self, team, x, y):
        super().__init__(unit_type=UnitType.PIKEMAN , name = "Pikeman", team = team, hp = 55, armor = 0, attack = 4, range = 0, size = 1, sight = 4, speed = 1.0, accuracy = 1.0, reload_time = 3.0, x = x, y = y, bonus_attack={"Shock Infantry":1 , "Base Melee":4 , "Mounted Units":22})

