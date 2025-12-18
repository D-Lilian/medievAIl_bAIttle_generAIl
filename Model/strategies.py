# -*- coding: utf-8 -*-
"""
@file strategies.py
@brief Strategy Definitions - AI behaviors

@details
Defines various strategies that Generals can assign to units.
Strategies determine how units behave in battle (e.g., attack, defend, flee).

"""
from Model.units import UnitType
from Model.orders import FormationOrder, DontMoveOrder
from Utils.errors import WrongArguments
from Model.orders import AttackOnSightOrder, AvoidOrder, StayInReachOrder, SacrificeOrder, \
    MoveByStepOrder, StayInFriendlySpaceOrder, AttackNearestTroupOmniscient
import random

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
        unit.order_manager.AddMaxPriority(AvoidOrder(unit, UnitType.KNIGHT))
        #tirer sur les pikeman
        unit.order_manager.AddMaxPriority(AttackNearestTroupOmniscient(unit, UnitType.PIKEMAN))
        #sinn tirer sur n'importe qui
        unit.order_manager.AddMaxPriority(AttackNearestTroupOmniscient(unit, UnitType.ALL))

class StrategieSimpleAttackBestAvoidWorst(StrategyTroup): #focus Pikeman (faibles au tir), évitent les Knights, restent groupés
    def __init__(self, favoriteTroup=UnitType.ALL, hatedTroup=UnitType.NONE):
        super().__init__(None, favoriteTroup, hatedTroup)

    def apply_order(self, general, unit):
        unit.order_manager.AddMaxPriority(AttackNearestTroupOmniscient(unit,self.favoriteTroup))
        unit.order_manager.AddMaxPriority(AttackNearestTroupOmniscient(unit,UnitType.ALL))
        if(self.hatedTroup != UnitType.NONE):
            unit.order_manager.AddMaxPriority(AvoidOrder(unit,self.hatedTroup))



class StrategieKnightSomeIQ(StrategyTroup):
    def __init__(self):
        #Cible favorite CROSSBOWMAN
        super().__init__(None, UnitType.CROSSBOWMAN, UnitType.PIKEMAN)
    
    def apply_order(self, general, unit):
        #pour foncer direct sur les archers adverses
        #contourne la ligne de front si possible
        unit.order_manager.AddMaxPriority(AttackNearestTroupOmniscient(unit, UnitType.CROSSBOWMAN))

        #si plus d'archers le reste
        unit.order_manager.AddMaxPriority(AttackNearestTroupOmniscient(unit, UnitType.ALL))


#protègent l'équipe en tuant les Chevaliers adverses
class StrategiePikemanSomeIQ(StrategyTroup):
    def __init__(self):
        #cible favorite KNIGHT
        super().__init__(None, UnitType.KNIGHT, UnitType.CROSSBOWMAN)

    def apply_order(self, general, unit):
        #priorité 1 Tuer les chevaux
        #on ne reste plus passif à attendre on va les chercher
        unit.order_manager.AddMaxPriority(AttackNearestTroupOmniscient(unit, UnitType.KNIGHT))

        #priorité 2 Tuer le reste
        unit.order_manager.AddMaxPriority(AttackNearestTroupOmniscient(unit, UnitType.ALL))


#############################################################################################################
# Strategie générique (Backups)
#############################################################################################################


# --- Fallbacks ---
class StrategieCrossbowmanFallbackSomeIQ(StrategyTroup):
    """quand il reste aucun crossbowmen vivant """

    def __init__(self):
        super().__init__(None, UnitType.ALL, UnitType.NONE)

    def apply_order(self, general, unit):
        # knight → rush les crossbowmen ennemis
        unit.order_manager.AddMaxPriority(AttackOnSightOrder(unit,UnitType.CROSSBOWMAN))

        # Pikeman → focus les knights ennemis
        unit.order_manager.AddMaxPriority(AttackOnSightOrder(unit,UnitType.KNIGHT))

        #if unit.type == UnitType.KNIGHT:
        #    # knight → rush les crossbowmen ennemis
        #    unit.order_manager.Add(AttackOnSightOrder(unit,UnitType.CROSSBOWMAN), 0)

        #elif unit.type == UnitType.PIKEMAN:
        #    # Pikeman → focus les knights ennemis
        #    unit.order_manager.Add(AttackOnSightOrder(unit,UnitType.KNIGHT), 0)


class StrategieNoKnightFallbackSomeIQ(StrategyTroup):
    """Quand il ne reste aucun knight vivant."""

    def __init__(self):
        super().__init__(None, UnitType.ALL, UnitType.NONE)

    def apply_order(self, general, unit):
        if unit.type == UnitType.CROSSBOWMAN:
            #les crossbowmen restent en arrière et focus ce qui s'avance
            unit.order_manager.Add(AttackOnSightOrder(unit,UnitType.ALL), 0)

        elif unit.type == UnitType.PIKEMAN:
            # Les pikemen se mettent en garde du corps des crossbowmen et tapent tout
            crossbowmen = [u for u in general.MyUnits if u.type == UnitType.CROSSBOWMAN]
            for crossbowman in crossbowmen:
                unit.order_manager.Add(StayInFriendlySpaceOrder(unit, UnitType.CROSSBOWMAN), 0)
            unit.order_manager.Add(AttackOnSightOrder(unit, self.favoriteTroup), 1)


class StrategieNoPikemanFallback(StrategyTroup):
    """Quand il ne reste aucun pikeman vivant."""

    def __init__(self):
        super().__init__(None, UnitType.ALL, UnitType.NONE)

    def apply_order(self, general, unit):
        unit.order_manager.Add(AttackNearestTroupOmniscient(unit, UnitType.ALL), 0)

        # Enlever les ordres qui target les spikeman


class StrategieNoTroupFallbackSomeIQ:
    """Quand il ne reste aucun troupe vivant. d'un type"""
    def __init__(self, unitType: UnitType):
        self.unitType = unitType

    def apply_order(self, general):
        pass
        #for unit in general.MyUnits:
        #    unit.order_manager.FlushOrders()


class StrategieRandomIQ(StrategyStart):
    def __init__(self):
        super().__init__()

    def apply_order(self, general):
        for unit in general.MyUnits:
            orders = [
                AttackNearestTroupOmniscient(
                    unit,
                    random.choice([UnitType.PIKEMAN,
                                   UnitType.CROSSBOWMAN,
                                   UnitType.NONE,
                                   UnitType.KNIGHT])
                ),
                StayInFriendlySpaceOrder(
                    unit,
                    random.choice([UnitType.PIKEMAN,
                                   UnitType.CROSSBOWMAN,
                                   UnitType.KNIGHT,
                                   UnitType.NONE,
                                   ])
                ),
                AvoidOrder(
                    unit,
                    random.choice([UnitType.PIKEMAN,
                                   UnitType.CROSSBOWMAN,
                                   UnitType.KNIGHT,
                                   UnitType.NONE])
                ),
            ]

            random.shuffle(orders)

            for order in orders:
                unit.order_manager.AddMaxPriority(order)

            unit.order_manager.AddMaxPriority(AttackNearestTroupOmniscient(unit, UnitType.ALL))



class StrategieStartSomeIQ(StrategyStart):
    """
    On envoi un mec se sacrifier, on recule toutes les troupes de 10 cases
    """
    def apply_order(self, general):
        # ON fait reculer tout le monde
        for unit in general.MyUnits:
            #unit.order_manager.Add(MoveOneStepFromRef(unit, 10, "WORLD"), 180)
            #unit.order_manager.Add(MoveByStepOrder(unit, 10, 180), 0)
            if(unit.unit_type == UnitType.KNIGHT):
                unit.order_manager.Add(DontMoveOrder(unit, 20-5), 0)
            elif(unit.unit_type == UnitType.CROSSBOWMAN):
                unit.order_manager.Add(DontMoveOrder(unit, 30-5), 0)
                unit.order_manager.Add(StayInFriendlySpaceOrder(unit, UnitType.PIKEMAN), 1)
            elif(unit.unit_type == UnitType.PIKEMAN):
                unit.order_manager.Add(DontMoveOrder(unit, 30-7), 0)

            #unit.order_manager.Add(DontMoveOrder(unit, 10), 0)

        # todo faire le truc global après les squad, et mettee les ordres globaux execeptés ceux au squad
        #StrategySquad(nb_crossbowmen=20).build_squad(general)
        #StrategySquad(nb_crossbowmen=20)
        #StrategySquad(nb_crossbowmen=20)

        # On fait une squad crossbow à gauche,
        squad1 = general.generate_squad({UnitType.CROSSBOWMAN:10, UnitType.PIKEMAN:5})
        if(len(squad1)!=0):
            for unit in squad1:
                #unit.order_manager.AddMaxPriority(MoveByStepOrder(unit, 50, 90), squad_id=squad1[0].squad_id)
                unit.order_manager.AddMaxPriority(FormationOrder(unit, squad1), squad_id=squad1[0].squad_id)

        # On fait une squad crossbow à droite,
        squad2 = general.generate_squad({UnitType.CROSSBOWMAN:10, UnitType.PIKEMAN:5})
        if(len(squad2)!=0):
            for unit in squad2:
                #unit.order_manager.AddMaxPriority(MoveByStepOrder(unit, 50, -90), squad_id=squad2[0].squad_id)
                #unit.order_manager.AddMaxPriority(DontMoveOrder(unit, 50), squad_id=squad2[0].squad_id)
                unit.order_manager.AddMaxPriority(FormationOrder(unit, squad2), squad_id=squad2[0].squad_id)

        squad3 = general.generate_squad({UnitType.KNIGHT:15})
        if(len(squad3)!=0):
            for unit in squad3:
                #unit.order_manager.AddMaxPriority(MoveByStepOrder(unit, 50, -90), squad_id=squad2[0].squad_id)
                #unit.order_manager.AddMaxPriority(DontMoveOrder(unit, 10), squad_id=squad2[0].squad_id)
                unit.order_manager.AddMaxPriority(FormationOrder(unit, squad3), squad_id=squad3[0].squad_id)


        soufredouleurs = general.generate_squad({UnitType.KNIGHT:3})
        for sf in soufredouleurs:
            sf.order_manager.RemoveOrderAtPriority(-1) # on lui enlève le déplacement en arrière

            #sf.order_manager.Add(SacrificeOrder(sf, 0, 50+soufredouleurs.index(sf)*10 ), -1)

            sf.order_manager.Add(SacrificeOrder(sf,  (sf.x-20) %general.size_x, (sf.y+50 )%general.size_y+soufredouleurs.index(sf)*10 ), -1)
            #sf.order_manager.Add(SacrificeOrder(sf,  (sf.x) %120, (sf.y +50)%120+soufredouleurs.index(sf)*10 ), -1)

            # faire systeme pourcentage

        soufredouleurs = general.generate_squad({UnitType.KNIGHT:3})
        for sf in soufredouleurs:
            sf.order_manager.RemoveOrderAtPriority(-1) # on lui enlève le déplacement en arrière

            #sf.order_manager.Add(SacrificeOrder(sf, 0, 50+soufredouleurs.index(sf)*10 ), -1)

            sf.order_manager.Add(SacrificeOrder(sf,  (sf.x+50) %general.size_x, (sf.y-20 )%general.size_y+soufredouleurs.index(sf)*10 ), -1)

        #soufredouleurs = general.generate_squad({UnitType.KNIGHT:3})
        #for sf in soufredouleurs:
        #    sf.order_manager.RemoveOrderAtPriority(-1) # on lui enlève le déplacement en arrière
        #    sf.order_manager.Add(SacrificeOrder(sf, 50, 50+soufredouleurs.index(sf)*10 ), -1)


        #soufredouleur1 = general.GetRandomUnit()
        #if soufredouleur1 is not None:
        #    soufredouleur1.order_manager.RemoveOrderAtPriority(-1) # on lui enlève le déplacement en arrière
        #    soufredouleur1.order_manager.Add(SacrificeOrder(soufredouleur1), -1)

        #soufredouleur2 = general.GetRandomUnit()
        #if soufredouleur2 is not None:
        #    soufredouleur2.order_manager.RemoveOrderAtPriority(-1) # on lui enlève le déplacement en arrière
        #    soufredouleur2.order_manager.Add(SacrificeOrder(soufredouleur2), -1)





class DummyStrategy(StrategyTroup):
    def __init__(self):
        super().__init__(None, UnitType.ALL, UnitType.NONE)
    def applyOrder(self):
        pass




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
