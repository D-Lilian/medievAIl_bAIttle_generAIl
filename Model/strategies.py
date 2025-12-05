from Model.units import UnitType
from errors import WrongArguments
from orders import AttackOnSightOrder, AvoidOrder, AttackOnReachOrder, StayInReachOrder, SacrificeOrder, \
    MoveByStepOrder, StayInFriendlySpaceOrder, AttackNearestTroupOmniscient


class StrategyStart:

    def __init__(self):
        pass

    def ApplyOrder(self, unit):
        # Ici donne a une troupe random par exemple le fait de se déplacer a l'autre bout de la map
        self.unit = unit
        raise NotImplemented #attaquer tout le monde par défaut pas sure

class StrategyTroup:
    def __init__(self, general, favoriteTroup, hatedTroup):
        if favoriteTroup == hatedTroup:
            raise WrongArguments("Favorite and hated troups cannot be the same")

        self.favoriteTroup = favoriteTroup
        self.hatedTroup = hatedTroup

        #if not self.favoriteTroup in general.HisUnits:
        #    self.favoriteTroup = None
        #pass

    def ApplyOrder(self, unit):
        self.unit = unit
        raise NotImplemented

# DAFT
# ----------------------
# Aucune hated troup
# Aucune favorite troup
class StrategieDAFT(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def apply_order(self, general, unit):
        print("Applying order")
        unit.order_manager.Add(AttackNearestTroupOmniscient(unit, self.favoriteTroup), 0)

## Deprecated
class StrategieCrossbowmanDAFT(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def apply_order(self, general, unit):
        unit.order_manager.Add(AttackOnSightOrder(unit, None), 0)

class StrategieKnightDAFT(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def apply_order(self, general, unit):
        unit.order_manager.Add(AttackOnSightOrder(unit, None), 0)

class StrategiePikemanDAFT(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def apply_order(self, general, unit):
        unit.order_manager.Add(AttackOnSightOrder(unit, None), 0)

class StrategieStartDAFT(StrategyStart):
    def apply_order(self, general, units):
        units.PushOrder(AttackOnSightOrder, 0) # On push/insere/add un ordre de priorité 0

# ----------------------


# BrainDead
# ----------------------
# Aucune hated troup
# Aucune favorite troup
class StrategieBrainDead(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def apply_order(self, general, unit):
        #unit.order_manager.Add(AttackOnReachOrder(unit, self.favoriteTroup), 0)
        unit.order_manager.Add(AttackOnSightOrder(unit, self.favoriteTroup), 0)


## DEPRECATED
class StrategieCrossbowmanBrainDead(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def apply_order(self, general, unit):
        unit.order_manager.Add(AttackOnReachOrder(unit, None), 0)

class StrategieKnightBrainDead(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def applyOrder(self, general, unit):
        unit.order_manager.Add(AttackOnReachOrder(unit, None), 0)

class StrategiePikemanBrainDead(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")
    def apply_order(self, general, unit):
        unit.order_manager.Add(AttackOnReachOrder(unit, None), 0)

class StrategieStartBrainDead(StrategyStart):
    def apply_order(self, general, unit):
        unit.order_manager.Add(AttackOnReachOrder, 0) # On push/insere/add un ordre de priorité 0
# ----------------------

# Le but de SomeIQ est de battre Braindead et daft, pas de battre un autre SomeIQ
# SomeIQ
# ----------------------
class StrategieCrossbowmanSomeIQ(StrategyTroup): #focus Pikeman (faibles au tir), évitent les Knights, restent groupés
    def __init__(self):
        super().__init__(None, UnitType.PIKEMAN, UnitType.KNIGHT)

    def apply_order(self, general, unit):
        unit.order_manager.Add(AvoidOrder(unit,UnitType.KNIGHT),0)  #éviter les knights

        if self.favoriteTroup is not None:
            unit.order_manager.Add(AttackOnSightOrder(unit,self.favoriteTroup), 1) # attaquer en priorité les pikemen
        else:
            unit.order_manager.Add(AttackOnSightOrder(unit,"All"), 1)


class StrategieKnightSomeIQ(StrategyTroup):
    def __init__(self):
        super().__init__(None, UnitType.CROSSBOWMAN, UnitType.PIKEMAN)
    
    def apply_order(self, general, unit):
        unit.order_manager.Add(AttackOnSightOrder(unit,UnitType.CROSSBOWMAN), 0)
        unit.order_manager.Add(AttackOnSightOrder(unit,"ALL"), 1)

class StrategiePikemanSomeIQ(StrategyTroup):
    def __init__(self):
        super().__init__(None, UnitType.KNIGHT, UnitType.CROSSBOWMAN)

    def applyOrder(self, general, unit):
        unit.order_manager.Add(StayInReachOrder(unit,UnitType.CROSSBOWMAN), 0)
        unit.order_manager.Add(AttackOnSightOrder(unit,"All"), 1) # On push/insere/add un ordre de priorité 0
       # stay in friendly zone a cote des srossbowmen et attaquer
    """for crossbowman in [u for u in general.MyUnits if u.Type == "Crossbowman"]:
        unit.order_manager.Add(StayInFriendlySpaceOrder(unit, "Crossbowman"), 0)
        # Attaque automatique des ennemis visibles"""


#rester collés des Crossbowmen pour les défendre et attaquer


class StrategieStartSomeIQ(StrategyStart):
    def apply_order(self, general):
        for unit in general.MyUnits: 
            #unit.order_manager.Add(MoveOneStepFromRef(unit, 10, "WORLD"), 180)
            unit.order_manager.Add(MoveByStepOrder(unit, 10, 180))

        soufredouleur = general.GetRandomUnit()
        if soufredouleur is not None:
            soufredouleur.PushOrder(SacrificeOrder(soufredouleur), -1) 





# Mets tout les crossbowmen derrière le knight le plus proche d'eux, mets un avoid des range des autres crossbowmen
# Ils ont donc 2 ordres, un attackonsight, et un avoidorder
# faire une strtegie de coureur, il va devant les lignes enemis et cours de droite à gauche
# Les Pikeman doivent protéger les crossbowmen, faire en sorte

# stratégie de début possible, toutes les troupes reculent de 10 pas, 5 knight foncent à droite de la map pour dégager toutes
# les torupes de devant, le reste des knights foncent sur les crossbowmen en passant par la gauche
# les crossbowmen se decale à gauche. les Pikeman se mettent devant les crossbowmen
# les Crossbowmen doivent être le plus séparé possible
# ----------------------

# Le but de RandomIQ est d'activer une stratégie aléatoire pour chaque troupe
# Utile pour se rendre compte après plusieurs milliarsd d'essais, les stratégies qui fonctionnent
# RandomIQ
# ----------------------
# ----------------------

class StrategieCrossbowmanFallbackSomeIQ(StrategyTroup):
    """quand il reste aucun crossbowmen vivant """

    def __init__(self):
        super().__init__(None, "All", "None")

    def applyOrder(self, general, unit):

        if unit.type == UnitType.KNIGHT:
            # knight → rush les crossbowmen ennemis
            unit.order_manager.Add(AttackOnSightOrder(unit,UnitType.CROSSBOWMAN), 0)

        elif unit.type == UnitType.PIKEMAN:
            # Pikeman → focus les knights ennemis
            unit.order_manager.Add(AttackOnSightOrder(unit,UnitType.KNIGHT), 0)


class StrategieNoKnightFallbackSomeIQ(StrategyTroup):
    """Quand il ne reste aucun knight vivant."""

    def __init__(self):
        super().__init__(None, "All", "None")

    def applyOrder(self, general, unit):
        if unit.type == UnitType.CROSSBOWMAN:
            #les crossbowmen restent en arrière et focus ce qui s'avance
            unit.order_manager.Add(AttackOnSightOrder(unit,"All"), 0)

        elif unit.type == UnitType.PIKEMAN:
            # Les pikemen se mettent en garde du corps des crossbowmen et tapent tout
            crossbowmen = [u for u in general.MyUnits if u.type == UnitType.CROSSBOWMAN]
            for crossbowman in crossbowmen:
                unit.order_manager.Add(StayInFriendlySpaceOrder(unit, UnitType.CROSSBOWMAN), 0)
            unit.order_manager.Add(AttackOnSightOrder(unit, self.favoriteTroup), 1)


class StrategieNoPikemanFallback(StrategyTroup):
    """Quand il ne reste aucun pikeman vivant."""

    def __init__(self):
        super().__init__(None, "All", "None")

    def applyOrder(self, general, unit):

        if unit.type == UnitType.KNIGHT:
            unit.order_manager.Add(AttackOnSightOrder(), 0)

        elif unit.type == UnitType.CROSSBOWMAN:
            # Les crossbowmen restent à distance et focus surtout les unités de mêlée
            unit.order_manager.Add(AvoidOrder(unit, UnitType.KNIGHT), 0)
            unit.order_manager.Add(AttackOnSightOrder(unit, self.favoriteTroup), 1)



# DIVISER LES TROUPES EN EQUIPES

class StrategySquad(): #Stratégie pour un squad mixte 
    
    def __init__(self, nb_crossbowmen=0, nb_knights=0, nb_pikemen=0, squad_id=1):
        self.nb_crossbowmen = nb_crossbowmen
        self.nb_knights = nb_knights
        self.nb_pikemen = nb_pikemen
        self.squad_id = squad_id
        self.units = []

    def build_squad(self, general): #Choisit les unités dans le général, et leur donne squad_id.
        self.units = []

        if self.nb_knights > 0:
            self.units += general.get_squad(UnitType.KNIGHT, self.nb_knights, self.squad_id)

        if self.nb_crossbowmen > 0:
            self.units += general.get_squad(UnitType.CROSSBOWMAN, self.nb_crossbowmen, self.squad_id)

        if self.nb_pikemen > 0:
            self.units += general.get_squad(UnitType.PIKEMAN, self.nb_pikemen, self.squad_id)

        return self.units

    def apply_orders(self, general, order_cls, priority, *order_args):# order_cls : classe d'ordre (ex: AttackOnSightOrder) priority , order_args ,
        for u in self.units:
            order = order_cls(u, *order_args)   # on cree un ordre pour chaque unité
            u.om.Add(order, priority) 

    #exemple d'appel squad.apply_orders(general, MoveByStepOrder, 10, "forward")  # MoveByStepOrder(u, 10, "forward")


       


