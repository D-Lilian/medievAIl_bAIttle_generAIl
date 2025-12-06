from Model.Units import Unit, Crossbowman, Knight, Pikeman
from Utils.errors import GameEngineError
from strategies import *
from Utils.logs import setup_logger,logger


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
                 UnitSubscriptions: dict = None,
                 ):

        self.MyUnits = unitsA
        self.HistUnits = unitsB
        self.UnitsDepleted = {
            UnitType.CROSSBOWMAN: False,
            UnitType.KNIGHT: False,
            UnitType.PIKEMAN: False,
        }


        self.UnitSubscriptions = UnitSubscriptions
        if self.UnitSubscriptions != None:
            assert(all(isinstance(i, UnitType) for i in UnitSubscriptions.keys()))


        # Set strategie
        self.sT = sT
        # La clé  correspond au unit.Type des unités.
        self.sS = sS

        log = logger.bind(general=str(self))
        log.info(f"Initialisation terminée.")
        log.info(f"Initialisation d'un nouveau Général avec {len(unitsA)} unités.")
        self.log = log
        self.log.info(f"Init general done")


    def notify(self, depleted_type: UnitType):
        """À appeler quand par simu `type_troupe` adverse vient de tomber à 0."""
        if self.UnitsDepleted.get(depleted_type, False):
            return # On a déjà géré cette perte adver, on ne fait rien

        if self.UnitSubscriptions is None:
            self.log.warning(f"Aucune stratégie de repli définie ")
            return


        self.log.info(f"Unités adverse de type {depleted_type.name} ont été finito.")

        self.UnitsDepleted[depleted_type] = True;
        fallback_strategy = self.UnitSubscriptions.get(depleted_type)
        if fallback_strategy is not None:
            self.log.info(f"Déclenchement de la stratégie de repli: {fallback_strategy.__class__.__name__}")
            for unit in self.MyUnits:
                if unit.hp > 0:
                    # On ne donne pas d'ordres aux unités mortes
                    # La stratégie de repli doit elle-même vider les anciens ordres
                    fallback_strategy.apply_order(self, unit)
        else:
            self.log.warning(f"Aucune stratégie de repli définie pour la perte de {depleted_type.name}.")


    def BeginStrategy(self): #appliquer la stratégie associée à son type
        # Probleme ici la stratégie est invidivuelle à chaque troupe, on veut faire autrement
        # TODO trouver une strategie de départ qui dépend de l'etat/nombre d'un ou plusieurs autre type de troupes
        # N'est appelé qu'au début
        self.log.info(f"Beggining strategy")
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

    def __str__(self):
        return f"General({len(self.MyUnits)}U , sS={self.sS.__name__ if self.sS else "None"}, sT={[type(s).__name__ for s in self.sT.values()] if self.sT else "None"})"


    def CreateOrders(self): # réappliquer la stratégie par type sur chaque unité
        self.log.debug("Creating orders")
        # Est appelé à chaque tour

        #for unit in self.MyUnits:
            # Pour chaque unité, on appli la stratégie lié à son type
        #    self.sT[unit.Type].ApplyOrder(self, unit)
            # Ex
            # self.St["crossbowman"].Applyorder(self, a1)
            # ici ça applicuqe la stratégie du général sur les troupes de type Crossbowman
        #if self.are_crossbows_left == False and self.crossbows_depleted is not None:
        #    self.crossbows_depleted()
        #if self.are_knights_left == False and self.knights_depleted is not None:
        #    self.knights_depleted()
        #if self.are_pikemen_left == False  and self.pikemen_depleted is not None:
        #    self.pikemen_depleted()
# # Cert# 1. On appel simu pour effectuer notre action, simu nous appelle et se passe en paramètre. Depuis try, on renvoi True si l'ordre a reussi
# et false si non.

# Certains ordres sont incompatibles, par ex: on ne peut pas Formation et un movetogether

# Si un role est en Enforce(priorité -1), il est le seul a etre executé, tant qu'il ne reussit pas, aucun autre ordre n'est appelé.


    def get_units_by_type(self, unit_type: UnitType ): #retourne toutes mes unites d’un type donné
            return [u for u in self.MyUnits if u.type == unit_type]



    def generate_squad(self, desired_units: dict):
            #selectionne jusqu’à count` unités de type `unit_type`qui ne sont pas encore dans un squad,leur assigne `squad_id`,et les retourne.  les unités sans squad
            from random import randint
            # desired_units= { Crossbowman:10 }

            available = []
            for unit_type, count in desired_units.items():
                available += [u for u in self.MyUnits if u.unit_type == unit_type and u.squad_id is None][:count]

            if len(available) != sum(desired_units.values()):
                raise GameEngineError(f"Il ne reste plus d'unités disponibles de type {desired_units} but got {available}")

            # genere un id aleatoire pas deja uttilisé
            used_squad_ids = {unit.squad_id for unit in self.MyUnits if unit.squad_id is not None}
            while True:
                squad_id = randint(1, 1000000)
                if squad_id not in used_squad_ids:
                    break

            for unit in available:
                unit.squad_id = squad_id

            self.log.debug(f"Squad generated with id {squad_id} and troups {available}")

            return available

    def flush_all_squads(self):
        for unit in self.MyUnits:
            unit.squad_id = None
            unit.order_manager.remove_squad_orders()
        self.log.debug("All squads flushed.")



if __name__ == '__main__':
    setup_logger(level="INFO", modules=["generals", "orders"])

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
        unitsA=unitsA,
        unitsB=unitsB,
        sS=None,
        sT={
            UnitType.CROSSBOWMAN:StrategieBrainDead(UnitType.CROSSBOWMAN),
            UnitType.KNIGHT:StrategieBrainDead(UnitType.KNIGHT),
            UnitType.PIKEMAN:StrategieBrainDead(UnitType.PIKEMAN)
        }
    )
    BRAINDEAD2 = General(
        unitsA=unitsB,
        unitsB=unitsA,
        sS=None,
        UnitSubscriptions={UnitType.CROSSBOWMAN: None},
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
    #    knights_depleteB,d=StrategieNoKnightFallbackSomeIQ(),
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
            logger.info(o)

    BRAINDEAD2.notify(UnitType.CROSSBOWMAN)

    #while(True):
    #    DAFT1.CreateOrders()
    #    DAFT2.CreateOrders()
