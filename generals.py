from operator import truediv

from lxml.proxy import fixThreadDictNamesForDtd
from mesonbuild.build import InvalidArguments


class WrongArguments(Exception):
    pass
class GameEngineError(Exception):
    pass
# Le general ne se préocupe pas de savoir "ou" sont les troupes, il n'a pas logique de réprésentation "logique" du jeu
# si il veut qu'une de ses troupes attaquent l'unité la plus proche, alors il le demande, il ne va pas aller chercher l'unité la plus proche

class General:
    # Il lui faut un moyen de detecter les différents etats du jeu adverse:
    # -il n'ya plus d'archers
    # -il ya + d'archers que de knights
    # etc
    def __init__(self, unitsA, unitsB, sS, **sT,are_archers_left=true,are_knights_left=true,are_spikemen_left=true,archer_depleted=None,knights_depleted=None,spikemen_depleted=None): #sS: Strategie start
        # Set UNits
        if(len(unitsB) != len(unitsA) != 200): #vérification de la longueur des unités
            raise WrongArguments("Not enough arguments")
        self.MyUnits = unitsA
        self.HistUnits = unitsB
        self.are_archers_left = are_archers_left
        self.are_knights_left = are_knights_left
        self.are_spikemen_left = are_spikemen_left
        self.archer_depleted = archer_depleted
        self.knigts_depleted = knigts_depleted
        self.spikemen_depleted = spikemen_depleted
        # Set Orders
        for unit in self.MyUnits:
            unit.Orders = [] #On vide les ordres

        # Set strategie
        self.sT = sT
        self.sS = sS

        return



def notify(self, type_troupe: str):
    """À appeler quand `type_troupe` vient de tomber à 0."""
    if type_troupe == "archer":
        self.are_archers_left = False
    if type_troupe == "knight":
        self.are_knights_left = False
    if type_troupe == "spikeman":
        self.are_spikemen_left = False



    def on_knights_depleted(self):
        """Comportement spécifique quand il n'y a plus de knights"""
        print("Plus de knights ! Attaque frontale")
        # Logique spécifique aux knights

    def on_spikemen_depleted(self):
        """Comportement spécifique quand il n'y a plus d'infanterie"""

        # Logique spécifique à l'infanterie
        # Logique spécifique aux knights

    def BeginStrategy(self): #appliquer la stratégie associée à son type
        # Probleme ici la stratégie est invidivuelle à chaque troupe, on veut faire autrement
        # TODO trouver une strategie de départ qui dépend de l'etat/nombre d'un ou plusieurs autre type de troupes
        # N'est appelé qu'au début
        self.Ss(self) # On passe le general en paramère de la stratégie
        #for unit in self.MyUnits:
        #    self.sT[unit.Type].ApplyOrder(self, unit)

## On peut s'en servir pour appliquer des stratégies différentes
    def GetNumberOfEnemyType(self, unitType): # récuperer le nbre des unités d'un type spécifique
        c = 0
        for u in self.HistUnits:
            if u == unitType:
                c+=1
        return c

    def CreateOrders(self): # réappliquer la stratégie par type sur chaque unité
        # Est appelé à chaque tour

        for unit in self.MyUnits:
            # Pour chaque unité, on appli la stratégie lié à son type
            self.sT[unit.Type].ApplyOrder(self, unit)
            if self.
            # Ex
            # self.St["archer"].Applyorder(self, a1)
            # ici ça applicuqe la stratégie du général sur les troupes de type archer
        if self.are_archers_left == false and self.archers_depleted is not None:
            self.archers_depleted()
            self.check_archers = true
        if self.are_knights_left == false and self.knigts_depleted is not None:
            self.knights_depleted()
            self.check_knights = true
        if self.are_spikemen_left == false  and self.spikemen_depleted is not None:
            self.spikemen_depleted()
            self.check_spikemen = true
# # Cert# 1. On appel simu pour effectuer notre action, simu nous appelle et se passe en paramètre. Depuis try, on renvoi True si l'ordre a reussi
# et false si non.

# Certains ordres sont incompatibles, par ex: on ne peut pas Formation et un movetogether

# Si un role est en Enforce(priorité -1), il est le seul a etre executé, tant qu'il ne reussit pas, aucun autre ordre n'est appelé.




if __name__ == '__main__':
    unitsA = ["archer" for i in range(200)]
    unitsB = ["archer" for i in range(200)]

    DAFT1 = General(unitsA, unitsB)
    DAFT2 = General(unitsB, unitsA)

    pass


