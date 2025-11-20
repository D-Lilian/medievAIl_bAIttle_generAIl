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
    def __init__(self, unitsA, unitsB, sS, **sT, watch_archers, watch_knights, watch_spikemen): #sS: Strategie start
        # Set UNits
        if(len(unitsB) != len(unitsA) != 200): #vérification de la longueur des unités
            raise WrongArguments("Not enough arguments")
        self.MyUnits = unitsA
        self.HistUnits = unitsB

        # Set Orders
        for unit in self.MyUnits:
            unit.Orders = [] #On vide les ordres

        # Set strategie
        self.sT = sT
        self.sS = sS

        return

    self.subscriptions = {}
    if watch_archers:
        fn = self.sT.get("archer")
        if callable(fn):
            self.subscriptions["archer"] = fn
    if watch_knights:
        fn = self.sT.get("knight")
        if callable(fn):
            self.subscriptions["knight"] = fn
    if watch_spikemen:
        fn = self.sT.get("spikeman")
        if callable(fn):
            self.subscriptions["spikeman"] = fn


def notify(self, type_troupe: str):
    """À appeler quand `type_troupe` vient de tomber à 0."""
    fn = self.subscriptions.get(type_troupe)
    if callable(fn):
        fn()



        """Comportement spécifique quand il n'y a plus d'archers"""
        print("Plus d'archers ! Changement de formation")
        # Logique spécifique aux archers

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
            # Ex
            # self.St["archer"].Applyorder(self, a1)
            # ici ça applicuqe la stratégie du général sur les troupes de type archer

class StrategyStart:
    def __init__(self):
        raise NotImplemented

    def ApplyOrder(self, unit):
        # Ici donne a une troupe random par exemple le fait de se déplacer a l'autre bout de la map
        self.unit = unit
        raise NotImplemented

class StrategyTroup:
    def __init__(self, general, favoriteTroup, hatedTroup):
        if self.favoriteTroup == self.hatedTroup:
            raise WrongArguments("Favorite and hated troups cannot be the same")

        self.favoriteTroup = favoriteTroup
        self.hatedTroup = hatedTroup

        if not self.favoriteTroup in general.HistUnits:
            self.favoriteTroup = None
        pass

    def ApplyOrder(self, unit):
        self.unit = unit
        raise NotImplemented


# 1. On appel simu pour effectuer notre action, simu nous appelle et se passe en paramètre. Depuis try, on renvoi True si l'ordre a reussi
# et false si non.

# Certains ordres sont incompatibles, par ex: on ne peut pas Formation et un movetogether

# Si un role est en Enforce(priorité -1), il est le seul a etre executé, tant qu'il ne reussit pas, aucun autre ordre n'est appelé.
class MoveOrder:
    def __init__(self, unit, x, y):
        self.unit = unit
        self.x = x
        self.y = y

    def Try(self, simu):
        if simu.ComparePosition(self.unit, self.x, self.y):
            return True # L'ordre a bien été réussi
        simu.MoveUnitClosestToXY(self.unit, self.x, self.y) # l'appel peut echouer ou pas, c pas grave on reessayera au prochain tick
        return False

class SacrificeOrder:
    def __init__(self, unit, priority):
        self.unit = unit
        self.priority = -1;
        if(priority !=-1):
            raise InvalidArguments("this order is in enforce mode, so its priority must be -1")
    def Try(self, simu):
        raise NotImplemented
    # Fait la meme chose que avoid, + se déplace vers un coin opposé à la map






class MoveByStepOrder:
    def __init__(self, unit, nbStep, direction):
        self.unit = unit
        self.nbStep = nbStep
        self.direction = direction
       # self.type = "permanent"

    def Try(self, simu):
        if simu.MoveOneStepTowardsDir(self.unit, self.direction): # TODO angle
            simu.nbStep -= 1

        if self.nbStep == 0:
            return True
        elif self.nbStep < 0:
            raise GameEngineError("While trying to step back, nbStep got negative")
        return False

class AvoidOrder:
    def __init__(self, unit, typeUnits, priority):
        self.unit = unit
        self.typeUnits = typeUnits
        self.priority = priority
        self.type = "permanent"

    def Try(self, simu):
        target = simu.GetNearestTroupInSight(self.unit, typeUnits=self.typeUnits)
        if target is None:
            return False # Il ya aucune enemy nearby

        if simu.IsInRange(target, self.Unit): # NOTE l'ordre des arguments ici est inversée
            if simu.MoveOneStepAwayFromTarget(self.unit, self.Target): # Calcule les 4 steps FORWARD BACK LEFT RIGHT, et effectue un pas dans la direction qui se retrouve etre la plus loin de la target
             #if simu.MoveOneStepTowardsDir(self.unit,self.target, 180): # TODO angle
                return False
        else:
            return False

# Ici c'est un ordre qui vérifie systématiquement que l'unité n'est pas toute seule, cad que dans sa ligne of sight il ya au moins un allié, sinon, elle se dirige vers l'allié le plus proche
class StayInFriendlySpaceOrder:
    def __init__(self, unit, priority):
        self.unit = unit
        self.priority = priority
        self.type = "permanent"

    def Try(self, simu):
        raise NotImplemented #il faut que le knight se rend cpte s'il sera trop loin des archers et revenir

class GetBehindOrder:
    def __init__(self, unit, target, priority):
        self.unit = unit
        self.target = target
        self.priority = priority

    def Try(self, simu):
        raise NotImplemented

class MoveTowardEnemyWithSpecificAttribute:
    def __init__(self, unit, priority, attribute_name, attribute_value, fixed=False):
        self.unit = unit
        self.target = target
        self.priority = priority
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value

    def Try(self, simu):
        #TODO
        raise NotImplemented



class AttackOrder:
    "On assume ici que la target est forcément dans la list des troupes adverses"
    def __init__(self, unit, target, priority):
        self.unit = unit
        self.target = target
        self.priority = priority

    def Try(self, simu):
        # todo enlever le isinrgange
        if simu.IsInRange(self.unit, self.target):
            killed = simu.Kill(self.unit, self.target)
            if not killed:
                return False
            return True
        return False

class StayInReachOrder:
    def __init__(self, unit, target, priority):
        self.unit = unit
        self.target = target
        self.priority = priority
        self.type = "permanent"

    def Try(self, simu):
        if simu.IsInReach(self.unit, self.target):
            return False

        simu.MoveUnitClosestTo(self.unit, self.target) # se deplace le plus lioin possible en fonction de la capacité de la troupe
        #if simu.MoveOneStepTowardsDir(self.unit,self.target, 0): # TODO angle
        return False


class AttackOnReachOrder:
    def __init__(self, unit, typeTarget, priority):
        self.unit = unit
        self.typeTarget = typeTarget
        self.priority = priority

    def Try(self, simu):
        target = simu.GetNearestTroupInReach(self.unit, typeTarget=self.typeTarget)
        if target is None:
            return False
        simu.Kill(self.unit, target)
        return False

class AttackOnSightOrder:
    # Au debut de la partie les unités se "voient" forcément
    # Le AttackOnSightOrder peut toujours etre accompli, cad il ne peut jamais se terminer, cad que l'appel à Try renvoi toujours False

    def __init__(self, unit, typeTarget, priority):
        self.unit = unit
        self.typeTarget = typeTarget
        self.priority = priority

    def Try(self, simu):
        target = simu.GetNearestTroupInSight(self.unit, typeTarget=self.typeTarget)
        if target is None:
            return False

        if simu.IsInRange(self.unit, target):
            killed = simu.Kill(self.unit, target)
            if not killed:
                return False
                # Redondant mais besoin pour la clarté du code
            return False
        else:
            #self.unit.PushOrder(MoveOrder(self.priority+1))
            simu.MoveUnitClosestTo(self.unit, target) # se deplace le plus lioin possible en fonction de la capacité de la troupe
            return False
            # Redondant mais besoin pour la clarté du code
        return False


class FormationOrder:
    def __init__(self, units, priority):
        self.units = units
        self.priority = priority

    def Try(self, simu, typeFormation="GROUPE"):
        # Qu'un seul type de formation (le groupe=
        if simu.IsInFormation(self.units, typeFormation): # check un rayon par ex
            return True
        simu.DoFormation(typeFormation, self.units) # renvoi trrue ou false en fonction
        return False


class isInDangerOrder:
    def __init__(self,unit,friendly,typeTarget, priority):
        self.unit = unit
        self.friendly = friendly
        self.priority = priority
        self.typeTarget = typeTarget
        self.type = "permanent"

    def Try(self,simu):
        target = simu.GetNearestTroupInSight(self.friendly, self.typeTarget)
        if target is None:
            return False

        simu.MoveUnitClosestTo(self.unit, target)
        return False


# DAFT
# ----------------------
# Aucune hated troup
# Aucune favorite troup

class StrategieArcherDAFT(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def applyOrder(self, general, unit):
        pass

class StrategieKnightDAFT(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def applyOrder(self, general, unit):
        pass

class StrategieSpikemanDAFT(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def applyOrder(self, general, unit):
        pass

class StrategieStartDAFT(StrategyStart):
    def applyOrder(self, general, units):
        unit.PushOrder(AttackOnSightOrder, 0) # On push/insere/add un ordre de priorité 0

# ----------------------


# BrainDead
# ----------------------
# Aucune hated troup
# Aucune favorite troup
class StrategieArcherBrainDead(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def applyOrder(self, general, unit):
        pass

class StrategieKnightBrainDead(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def applyOrder(self, general, unit):
        pass

class StrategieSpikemanBrainDead(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")
    def applyOrder(self, general, unit):
        pass

class StrategieStartBrainDead(StrategyStart):
    def applyOrder(self, general, unit):
        unit.PushOrder(AttackOnReachOrder, 0) # On push/insere/add un ordre de priorité 0
# ----------------------

# Le but de SomeIQ est de battre Braindead et daft, pas de battre un autre SomeIQ
# SomeIQ
# ----------------------
class StrategieArcherSomeIQ(StrategyTroup):
    def __init__(self):
        super().__init__(None, "SpikeMan", "Knight")
    def applyOrder(self, general, unit):
        unit.PushOrder(AttackOnSightOrder(self.favoriteTroup), 1) # On push/insere/add un ordre de priorité 0
        #unit.PushOrder(MoveOrder(), 0) # On push/insere/add un ordre de priorité 0
        # deplace les archers pour quil se mettent ensemble
        unit.PushOrder(AvoidOrder(unit, self.hatedTroup), 0)
        # Il faut aussi un ordre qui dit genre si ya un knight qui te course, tu recules

class StrategieKnightSomeIQ(StrategyTroup):
    def __init__(self):
        super().__init__(None, "Archer", "SpikeMan")
    def applyOrder(self, general, unit):
        unit.PushOrder(AttackOnSightOrder, 0) # On push/insere/add un ordre de priorité 0

class StrategieSpikemanSomeIQ(StrategyTroup):
    def __init__(self):
        super().__init__(None, "Knight", "Archer")
    def applyOrder(self, general, unit):
        unit.PushOrder(StayInReachOrder(unit, "Archer"), 0)
        unit.PushOrder(AttackOnSightOrder, 1) # On push/insere/add un ordre de priorité 0

class StrategieStartSomeIQ(StrategyStart):
    def applyOrder(self, general):
        for unit in general.HistUnits:
            unit.PushOrder(MoveOneStepFromRef(unit, 10, "WORLD"), 0) # On push/insere/add un ordre de priorité 0

        soufredouleur = general.GetRandomUnit()
        soufredouleur.PushOrder(SacrificeOrder(soufredouleur), -1)





        # Pour chaque

# Mets tout les archers derrière le knight le plus proche d'eux, mets un avoid des range des autres archers
# Ils ont donc 2 ordres, un attackonsight, et un avoidorder
# faire une strtegie de coureur, il va devant les lignes enemis et cours de droite à gauche
# Les spikeman doivent protéger les archers, faire en sorte

# stratégie de début possible, toutes les troupes reculent de 10 pas, 5 knight foncent à droite de la map pour dégager toutes
# les torupes de devant, le reste des knights foncent sur les archers en passant par la gauche
# les archers se decale à gauche. les spikeman se mettent devant les archers
# les archers doivent être le plus séparé possible
# ----------------------

# Le but de RandomIQ est d'activer une stratégie aléatoire pour chaque troupe
# Utile pour se rendre compte après plusieurs milliersd d'essais, les stratégies qui fonctionnent
# RandomIQ
# ----------------------
# ----------------------


if __name__ == '__main__':
    unitsA = ["archer" for i in range(200)]
    unitsB = ["archer" for i in range(200)]

    DAFT1 = General(unitsA, unitsB)
    DAFT2 = General(unitsB, unitsA)

    pass


