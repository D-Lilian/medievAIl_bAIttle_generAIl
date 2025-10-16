import math
import random

class Unit:
    
    def __init__(self, nom, team, hp, armure, attaque, portee, size, vue, vitesse, precision, rechargement, temps_recharg, x, y, order):
        self.nom =nom 
        self.hp = hp                            # =0 si l'unite est morte
        self.team = team                        # choix de l'equipe
        self.armure = armure
        self.attaque = attaque
        self.portee = portee
        self.size = size                        # taille de l'unite
        self.vue = vue                          # Distance champ de vision
        self.vitesse = vitesse                  # vitesse de deplacement
        self.precision = precision
        self.rechargement = rechargement        # avanncement du rechargement, peut attaquer a 0
        self.temps_recharg = temps_recharg      # temps pour recharger
        self.x = x
        self.y = y
        self.order = order

    def vivant(self):
        return (self.hp > 0)
    
    def peut_attaquer(self):
        if self.rechargement == 0:
            self.attaquer
        else :
            self.recharger
    
    def recharger(self):
        if self.rechargement == 0:
            return None
        else :
            self.rechargement -= 1
    
    def attaquer(self):
        pass

    def deplacer(self):
        pass


class Archer(Unit):
    def __init__(self, team, x, y):
        super().__init__(nom = "Archer", team = team, hp = 30, armure = 0, attaque = 4, portee = 4, size = , vue = 6, vitesse = 0.96, precision = 0.8, rechargement = 2.0, x = x, y = y, order = )

class Knight(Unit):
    def __init__(self, team, x, y):
        super().__init__(nom = "Knight", team = team, hp = 100, armure = 2, attaque = 10, portee = 0, size = , vue = 4, vitesse = 1.35, precision = 1.0, rechargement = 1.8, x = x, y = y, order =  )

class Pikeman(Unit):
    def __init__(self, team, x, y):
        super().__init__(nom = "Pikeman", team = team, hp = 55, armure = 0, attaque = 4, portee = 0, size = , vue = 4, vitesse = 1.0, precision = 1.0, rechargement = 3.0, x = x, y = y, order = )