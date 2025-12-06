from Model.orders import OrderManager
from Model.Units import Unit, UnitType, Crossbowman, Knight, Pikeman
from Model.strategies import *

from Model.errors import *

# Le general ne se préocupe pas de savoir "ou" sont les troupes, il n'a pas logique de réprésentation "logique" du jeu
# si il veut qu'une de ses troupes attaquent l'unité la plus proche, alors il le demande, il ne va pas aller chercher l'unité la plus proche

class General:
    # Il lui faut un moyen de detecter les différents etats du jeu adverse:
    # -il n'ya plus de crossbowmen
    # -il ya + de crossbowmen que de knights
    # etc
    def __init__(self,
                 unitsA: list[Unit],
                 unitsB: list[Unit],
                 sS,
                 sT,
                 crossbows_depleted=None,
                 knights_depleted=None,
                 pikemen_depleted=None,
                 ):

        self.MyUnits = unitsA
        self.HistUnits = unitsB
        self.are_crossbows_left = True
        self.are_knights_left = True
        self.are_pikemen_left = True
        self.crossbows_depleted = crossbows_depleted
        self.knights_depleted = knights_depleted
        self.pikemen_depleted = pikemen_depleted

        # Set strategie
        self.sT = sT
        # La clé  correspond au unit.Type des unités.
        self.sS = sS


    def notify(self, type_troupe: UnitType):
        """À appeler quand `type_troupe` vient de tomber à 0."""
        if type_troupe == UnitType.CROSSBOWMAN:
            self.are_crossbows_left = False
        if type_troupe == UnitType.KNIGHT:
            self.are_knights_left = False
        if type_troupe == UnitType.PIKEMAN:
            self.are_pikemen_left = False




    def BeginStrategy(self): #appliquer la stratégie associée à son type
        # Probleme ici la stratégie est invidivuelle à chaque troupe, on veut faire autrement
        # TODO trouver une strategie de départ qui dépend de l'etat/nombre d'un ou plusieurs autre type de troupes
        # N'est appelé qu'au début
        if(self.sS):
            self.sS(self) # On passe le general en paramère de la stratégie

        for unit in self.MyUnits:
            self.sT[unit.unit_type].apply_order(self,unit)

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
            # self.St["crossbowman"].Applyorder(self, a1)
            # ici ça applicuqe la stratégie du général sur les troupes de type Crossbowman
        if self.are_crossbows_left == False and self.crossbows_depleted is not None:
            self.crossbows_depleted()
        if self.are_knights_left == False and self.knights_depleted is not None:
            self.knights_depleted()
        if self.are_pikemen_left == False  and self.pikemen_depleted is not None:
            self.pikemen_depleted()
# # Cert# 1. On appel simu pour effectuer notre action, simu nous appelle et se passe en paramètre. Depuis try, on renvoi True si l'ordre a reussi
# et false si non.

# Certains ordres sont incompatibles, par ex: on ne peut pas Formation et un movetogether

# Si un role est en Enforce(priorité -1), il est le seul a etre executé, tant qu'il ne reussit pas, aucun autre ordre n'est appelé.


    def get_units_by_type(self, unit_type: UnitType ): #retourne toutes mes unites d’un type donné
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

    class MockUnit(Unit):
        def __init__(self, unit_type):
            self.Type = unit_type
            self.om = OrderManager()
    def __repr__(self):
        return f"Unit({self.Type})"

    unitsA = [Crossbowman('A', 0, 0) for i in range(200)] + [Knight('A', 0, 0) for i in range(200)] + [Pikeman('A', 0, 0) for i in range(200)]
    unitsB = [Crossbowman('B', 0, 0) for i in range(200)] + [Knight('B', 0, 0) for i in range(200)] + [Pikeman('B', 0, 0) for i in range(200)]


   # DAFT1 = General(unitsA,
   #                 unitsB,
   #                 sS=None,
   #                 sT={
   #                     UnitType.CROSSBOWMAN:StrategieBrainDead(UnitType.CROSSBOWMAN),
   #                     UnitType.KNIGHT:StrategieBrainDead(UnitType.KNIGHT),
   #                     UnitType.PIKEMAN:StrategieBrainDead(UnitType.PIKEMAN)
   #                 }
   #                 )

   # DAFT2 = General(unitsB,
   #                 unitsA,
   #                 sS=None,
   #                 sT=cart_prod ("ab", {1,2,3}){
   #                     UnitType.CROSSBOWMAN:StrategieBrainDead(UnitType.CROSSBOWMAN),
   #                     UnitType.KNIGHT:StrategieBrainDead(UnitType.KNIGHT),
   #                     UnitType.PIKEMAN:StrategieBrainDead(UnitType.PIKEMAN)
   #                 }
   #                 )

    BRAINDEAD1 = General(
        unitsA,
        unitsB,
        sS=None,
        sT={
            UnitType.CROSSBOWMAN:StrategieBrainDead(UnitType.CROSSBOWMAN),
            UnitType.KNIGHT:StrategieBrainDead(UnitType.KNIGHT),
            UnitType.PIKEMAN:StrategieBrainDead(UnitType.PIKEMAN)
        }
    )
    BRAINDEAD2 = General(
        unitsB,
        unitsA,
        sS=None,
        sT={
            UnitType.CROSSBOWMAN:StrategieBrainDead(UnitType.CROSSBOWMAN),
            UnitType.KNIGHT:StrategieBrainDead(UnitType.KNIGHT),
            UnitType.PIKEMAN:StrategieBrainDead(UnitType.PIKEMAN)
        }
    )
    #SOMEIQ = General(
    #    unitsA,
    #    unitsB,
    #    crossbows_depleted=StrategieCrossbowmanFallbackSomeIQ(),
    #    knights_depleted=StrategieNoKnightFallbackSomeIQ(),
    #    pikemen_depleted=StrategieNoPikemanFallback(),

    #    sS=None,
    #    sT={ # TODO: Fix the strategies to use the enum
    #        UnitType.KNIGHT:StrategieKnightSomeIQ(),
    #        UnitType.PIKEMAN:StrategiePikemanSomeIQ(),
    #        UnitType.CROSSBOWMAN:StrategieCrossbowmanSomeIQ(),
    #    }
    #)

    #SIMU Dumb
    #DAFT1.BeginStrategy()
    #DAFT2.BeginStrategy()
    BRAINDEAD1.BeginStrategy()
    BRAINDEAD2.BeginStrategy()
    for u in unitsA:
        for o in u.order_manager:
            print(o)

    #while(True):
    #    DAFT1.CreateOrders()
    #    DAFT2.CreateOrders()
