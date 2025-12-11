from Model.Units import UnitType
from Model.orders import FormationOrder
from Utils.errors import WrongArguments
from Model.orders import AttackOnSightOrder, AvoidOrder, StayInReachOrder, SacrificeOrder, \
    MoveByStepOrder, StayInFriendlySpaceOrder, AttackNearestTroupOmniscient

#############################################################################################################
# CLasse abstraites
#############################################################################################################
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

    def ApplyOrder(self, unit):
        self.unit = unit
        raise NotImplemented

#############################################################################################################
# DAFT
#############################################################################################################
# Aucune hated troup
# Aucune favorite troup
class StrategieDAFT(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, UnitType.ALL, UnitType.NONE)

    def apply_order(self, general, unit):
        print("Applying order")
        unit.order_manager.Add(AttackNearestTroupOmniscient(unit, self.favoriteTroup), 0)

## Deprecated

class StrategieStartDAFT(StrategyStart):
    def apply_order(self, general, units):
        pass

#############################################################################################################
# BrainDead
#############################################################################################################
# Aucune hated troup
# Aucune favorite troup
class StrategieBrainDead(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, UnitType.ALL, UnitType.NONE)

    def apply_order(self, general, unit):
        #unit.order_manager.Add(AttackOnReachOrder(unit, self.favoriteTroup), 0)
        unit.order_manager.Add(AttackOnSightOrder(unit, self.favoriteTroup), 0)


class StrategieStartBrainDead(StrategyStart):
    def apply_order(self, general, unit):
        pass
        #unit.order_manager.Add(AttackOnReachOrder, 0) # On push/insere/add un ordre de priorité 0

#############################################################################################################
# SomeIQ 
#############################################################################################################

# 1. ARBALÉTRIERS : Ils visent les Piquiers (lents) et fuient les Chevaliers
class StrategieCrossbowmanSomeIQ(StrategyTroup): 
    def __init__(self):
        # Cible favorite PIKEMAN car ils n'ont pas d'armure de tir
        # Ennemi détesté KNIGHT car ils chargent vite
        super().__init__(None, UnitType.PIKEMAN, UnitType.KNIGHT)

    def apply_order(self, general, unit):
        #priorité 0 fuir si un Chevalier est trop près
        unit.order_manager.Add(AvoidOrder(unit, UnitType.KNIGHT), 0)
        #tirer sur les pikeman
        unit.order_manager.Add(AttackNearestTroupOmniscient(unit, UnitType.PIKEMAN), 1)
        #sinn tirer sur n'importe qui
        unit.order_manager.Add(AttackNearestTroupOmniscient(unit, UnitType.ALL), 2)



class StrategieKnightSomeIQ(StrategyTroup):
    def __init__(self):
        #Cible favorite CROSSBOWMAN 
        super().__init__(None, UnitType.CROSSBOWMAN, UnitType.PIKEMAN)
    
    def apply_order(self, general, unit):
        #pour foncer direct sur les archers adverses
        #contourne la ligne de front si possible
        unit.order_manager.Add(AttackNearestTroupOmniscient(unit, UnitType.CROSSBOWMAN), 0)
        
        #si plus d'archers le reste
        unit.order_manager.Add(AttackNearestTroupOmniscient(unit, UnitType.ALL), 1)


#protègent l'équipe en tuant les Chevaliers adverses
class StrategiePikemanSomeIQ(StrategyTroup):
    def __init__(self):
        #cible favorite KNIGHT 
        super().__init__(None, UnitType.KNIGHT, UnitType.CROSSBOWMAN)

    def apply_order(self, general, unit):
        #priorité 1 Tuer les chevaux 
        #on ne reste plus passif à attendre on va les chercher
        unit.order_manager.Add(AttackNearestTroupOmniscient(unit, UnitType.KNIGHT), 0)
        
        #priorité 2 Tuer le reste
        unit.order_manager.Add(AttackNearestTroupOmniscient(unit, UnitType.ALL), 1)


#############################################################################################################
# Strategie générique (Backups)
#############################################################################################################

class StrategieSimpleAttackBestAvoidWorst(StrategyTroup): 
    def __init__(self, favoriteTroup=UnitType.ALL, hatedTroup=UnitType.NONE):
        super().__init__(None, favoriteTroup, hatedTroup)

    def apply_order(self, general, unit):
        unit.order_manager.Add(AttackNearestTroupOmniscient(unit,self.favoriteTroup), 0)
        unit.order_manager.Add(AvoidOrder(unit,self.hatedTroup),1)
        unit.order_manager.Add(AttackNearestTroupOmniscient(unit,UnitType.ALL), 2)

# --- Fallbacks ---
class StrategieCrossbowmanFallbackSomeIQ(StrategyTroup):
    def __init__(self): super().__init__(None, UnitType.ALL, UnitType.NONE)
    def apply_order(self, general, unit):
        unit.order_manager.AddMaxPriority(AttackNearestTroupOmniscient(unit, UnitType.CROSSBOWMAN))

class StrategieNoKnightFallbackSomeIQ(StrategyTroup):
    def __init__(self): super().__init__(None, UnitType.ALL, UnitType.NONE)
    def apply_order(self, general, unit):
        unit.order_manager.Add(AttackNearestTroupOmniscient(unit, UnitType.ALL), 0)

class StrategieNoPikemanFallback(StrategyTroup):
    def __init__(self): super().__init__(None, UnitType.ALL, UnitType.NONE)
    def apply_order(self, general, unit):
        unit.order_manager.Add(AttackNearestTroupOmniscient(unit, UnitType.ALL), 0)



class StrategieNoTroupFallbackSomeIQ:
    """Quand il ne reste aucun troupe vivant. d'un type"""
    def __init__(self, unitType: UnitType):
        self.unitType = unitType

    def apply_order(self, general):
        pass
        #for unit in general.MyUnits:
        #    unit.order_manager.FlushOrders()







# DIVISER LES TROUPES EN EQUIPES

class StrategySquad(): #Stratégie pour un squad mixte 
    
    def __init__(self, general, nb_crossbowmen=0, nb_knights=0, nb_pikemen=0, squad_id=0):
        self.nb_crossbowmen = nb_crossbowmen
        self.nb_knights = nb_knights
        self.nb_pikemen = nb_pikemen
        self.squad_id = general.squad_id
        self.units = []


    def build_squad(self, general): #Choisit les unités dans le général, et leur donne squad_id.
        if(self.units != []):
            # strategie already called
            general.log.warn("Strategye called twice")
            return self.units

        squad = general.generate_squad(
            {UnitType.CROSSBOWMAN: self.nb_crossbowmen,
             UnitType.KNIGHT: self.nb_knights,
             UnitType.PIKEMAN: self.nb_pikemen}
        )
        self.units = squad

        return squad

    def apply_orders(self, general, order_cls, priority, *order_args):# order_cls : classe d'ordre (ex: AttackOnSightOrder) priority , order_args ,
        for u in self.units:
            order = order_cls(u, *order_args)   # on cree un ordre pour chaque unité
            u.om.Add(order, priority) 

    #exemple d'appel squad.apply_orders(general, MoveByStepOrder, 10, "forward")  # MoveByStepOrder(u, 10, "forward")


       