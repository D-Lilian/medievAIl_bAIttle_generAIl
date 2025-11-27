import math
import random

class Unit:
    
    def __init__(self, name, team, hp, armor, attack, range, size, sight, speed, accuracy, reload, reload_time, x, y, Order_Manager, bonus_attack):
        self.name =name 
        self.hp = hp                        # =0 si l'unite est morte
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

    def alive(self):
        return (self.hp > 0)
    
    def can_attack(self):
        if self.reload == 0:
            self.attack()
        else :
            self.update_reload()
    
    def update_reload(self, t):
        if self.reload == 0:
            return None
        else :
            self.reload -= t # !!! verifier la valeur selon le nb de tics par seconde !!!


class Archer(Unit):
    def __init__(self, team, x, y):
        super().__init__(name = "Archer", team = team, hp = 30, armor = 0, attack = 4, range = 4, size = 1, sight = 6, speed = 0.96, accuracy = 0.8, reload_time = 2.0, x = x, y = y, bonus_attack={"Spearmen":3 , "Base Pierce":4})

class Knight(Unit):
    def __init__(self, team, x, y):
        super().__init__(name = "Knight", team = team, hp = 100, armor = 2, attack = 10, range = 0, size = 1, sight = 4, speed = 1.35, accuracy = 1.0, reload_time = 1.8, x = x, y = y, bonus_attack={"Base Melee":10 , "Cavalry Resistance":-3})

class Pikeman(Unit):
    def __init__(self, team, x, y):
        super().__init__(name = "Pikeman", team = team, hp = 55, armor = 0, attack = 4, range = 0, size = 1, sight = 4, speed = 1.0, accuracy = 1.0, reload_time = 3.0, x = x, y = y, bonus_attack={"Shock Infantry":1 , "Base Melee":4 , "Mounted Units":22})

