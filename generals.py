from orders import OrderManager

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
    def __init__(self,
                 unitsA,
                 unitsB,
                 sS,
                 crossbows_depleted=None,
                 knights_depleted=None,
                 spikemen_depleted=None,
                 **sT):
        # Set UNits
        if(len(unitsB) != len(unitsA) != 200): #vérification de la longueur des unités
            raise WrongArguments("Not enough arguments")
        self.MyUnits = unitsA
        self.HistUnits = unitsB
        self.are_archers_left = True
        self.are_knights_left = True
        self.are_spikemen_left = True
        self.crossbows_depleted = crossbows_depleted
        self.knigts_depleted = knights_depleted
        self.spikemen_depleted = spikemen_depleted

        # Set strategie
        self.sT = sT
        # La clé  correspond au unit.Type des unités.
        self.sS = sS


    def notify(self, type_troupe: str):
        """À appeler quand `type_troupe` vient de tomber à 0."""
        if type_troupe == "crossbow":
            self.are_crossbows_left = False
        if type_troupe == "knight":
            self.are_knights_left = False
        if type_troupe == "spikeman":
            self.are_spikemen_left = False




    def BeginStrategy(self): #appliquer la stratégie associée à son type
        # Probleme ici la stratégie est invidivuelle à chaque troupe, on veut faire autrement
        # TODO trouver une strategie de départ qui dépend de l'etat/nombre d'un ou plusieurs autre type de troupes
        # N'est appelé qu'au début
        if(self.Ss):
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

        #for unit in self.MyUnits:
            # Pour chaque unité, on appli la stratégie lié à son type
        #    self.sT[unit.Type].ApplyOrder(self, unit)
            # Ex
            # self.St["archer"].Applyorder(self, a1)
            # ici ça applicuqe la stratégie du général sur les troupes de type archer
        if self.are_crossbows_left == False and self.crossbows_depleted is not None:
            self.crossbows_depleted()
        if self.are_knights_left == False and self.knigts_depleted is not None:
            self.knights_depleted()
        if self.are_spikemen_left == False  and self.spikemen_depleted is not None:
            self.spikemen_depleted()
# # Cert# 1. On appel simu pour effectuer notre action, simu nous appelle et se passe en paramètre. Depuis try, on renvoi True si l'ordre a reussi
# et false si non.

# Certains ordres sont incompatibles, par ex: on ne peut pas Formation et un movetogether

# Si un role est en Enforce(priorité -1), il est le seul a etre executé, tant qu'il ne reussit pas, aucun autre ordre n'est appelé.


    def get_units_by_type(self, unit_type): #retourne toutes mes unites d’un type donné
            return [u for u in self.MyUnits if u.type == unit_type]



    def get_squad(self, unit_type: str, count: int, squad_id: int): #selectionne jusqu’à count` unités de type `unit_type`qui ne sont pas encore dans un squad,leur assigne `squad_id`,et les retourne.
            # les unités sans squad
            available = [
                u for u in self.MyUnits
                if u.type== unit_type and u.squad_id == None # ajouter un None comme troisieme argument s'il ya la possibilté de ne pas avoir l'att id
            ]
            squad = available[:count]
            for u in squad:
                u.squad_id = squad_id
            return squad



if __name__ == '__main__':

    class MockUnit:
        def __init__(self, unit_type):
            self.Type = unit_type
            self.om = OrderManager()
    def __repr__(self):
        return f"Unit({self.Type})"

    unitsA = [MockUnit("Crossbow") for i in range(200)]
    unitsB = [MockUnit("Crossbow") for i in range(200)]

    DAFT1 = General(unitsA,
                    unitsB,
                    sS=None,
                    crossbow=StrategieBrainDead("Crossbow"),
                    knight=StrategieBrainDead("knight"),
                    spikeman=StrategieBrainDead("spikeman")
                    )

    DAFT2 = General(unitsB,
                    unitsA,
                    sS=None,
                    crossbow=StrategieBrainDead("Crossbow"),
                    knight=StrategieBrainDead("knight"),
                    spikeman=StrategieBrainDead("spikeman")
                    )

    BRAINDEAD1 = General(
        unitsA,
        unitsB,
        sS=None,
        crossbow=StrategieDaft("Crossbow"),
        knight=StrategieDaft("knight"),
        spikeman=StrategieDaft("spikeman")
    )
    BRAINDEAD2 = General(
        unitsA,
        unitsB,
        sS=None,
        crossbow=StrategieDaft("Crossbow"),
        knight=StrategieDaft("knight"),
        spikeman=StrategieDaft("spikeman")
    )


    SOMEIQ = General(
        unitsA,
        unitsB,
    )

    #SIMU Dumb
    DAFT1.BeginStrategy()
    DAFT2.BeginStrategy()

    while(True):
        DAFT1.CreateOrders()
        DAFT2.CreateOrders()










