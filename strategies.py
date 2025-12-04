from errors import WrongArguments
from orders import AttackOnSightOrder, AvoidOrder, AttackOnReachOrder, StayInReachOrder, SacrificeOrder, MoveByStepOrder


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

    def applyOrder(self, general, unit):
        pass

## Deprecated
class StrategieArcherDAFT(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def applyOrder(self, general, unit):
        unit.PushOrder(AttackOnSightOrder(unit, None), 0)

class StrategieKnightDAFT(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def applyOrder(self, general, unit):
        unit.PushOrder(AttackOnSightOrder(unit, None), 0)

class StrategiePikemanDAFT(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def applyOrder(self, general, unit):
        unit.PushOrder(AttackOnSightOrder(unit, None), 0)

class StrategieStartDAFT(StrategyStart):
    def applyOrder(self, general, units):
        units.PushOrder(AttackOnSightOrder, 0) # On push/insere/add un ordre de priorité 0

# ----------------------


# BrainDead
# ----------------------
# Aucune hated troup
# Aucune favorite troup
class StrategieBrainDead(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def applyOrder(self, general, unit):
        pass


## DEPRECATED
class StrategieArcherBrainDead(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def applyOrder(self, general, unit):
        unit.PushOrder(AttackOnReachOrder(unit, None), 0)

class StrategieKnightBrainDead(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")

    def applyOrder(self, general, unit):
        unit.PushOrder(AttackOnReachOrder(unit, None), 0)

class StrategiePikemanBrainDead(StrategyTroup):
    def __init__(self, general):
        super().__init__(general, "All", "None")
    def applyOrder(self, general, unit):
        unit.PushOrder(AttackOnReachOrder(unit, None), 0)

class StrategieStartBrainDead(StrategyStart):
    def applyOrder(self, general, unit):
        unit.PushOrder(AttackOnReachOrder, 0) # On push/insere/add un ordre de priorité 0
# ----------------------

# Le but de SomeIQ est de battre Braindead et daft, pas de battre un autre SomeIQ
# SomeIQ
# ----------------------
class StrategieArcherSomeIQ(StrategyTroup): #focus Pikeman (faibles au tir), évitent les Knights, restent groupés
    def __init__(self):
        super().__init__(None, "PikeMan", "Knight")

    def applyOrder(self, general, unit):
        unit.PushOrder(AvoidOrder(unit,"knight"),0)  #éviter les knights

        if self.favoriteTroup is not None:
            unit.PushOrder(AttackOnSightOrder(unit,self.favoriteTroup), 1) # attaquer en priorité les Spikemen
        else:
            unit.PushOrder(AttackOnSightOrder(unit,"All"), 1)


class StrategieKnightSomeIQ(StrategyTroup):
    def __init__(self):
        super().__init__(None, "Archer", "PikeMan") 
    
    def applyOrder(self, general, unit):
        unit.PushOrder(AttackOnSightOrder(unit,"Archer"), 0) 
        unit.PushOrder(AttackOnSightOrder(unit,"ALL"), 1) 

class StrategiePikemanSomeIQ(StrategyTroup):
    def __init__(self):
        super().__init__(None, "Knight", "Archer")

    def applyOrder(self, general, unit):
        unit.PushOrder(StayInReachOrder(unit, "Archer"), 0)
        unit.PushOrder(AttackOnSightOrder(unit,"All"), 1) # On push/insere/add un ordre de priorité 0
       # stay in friendly zone a cote des archers et attaquer
    """for archer in [u for u in general.MyUnits if u.Type == "archer"]:
        unit.PushOrder(StayInFriendlySpaceOrder(unit, "Archer"), 0)
        # Attaque automatique des ennemis visibles"""


#rester collés des archers pour les défendre et attaquer


class StrategieStartSomeIQ(StrategyStart):
    def apply_order(self, general):
        for unit in general.MyUnits: 
            #unit.PushOrder(MoveOneStepFromRef(unit, 10, "WORLD"), 180)
            unit.PushOrder(MoveByStepOrder(unit, 10, 180))

        soufredouleur = general.GetRandomUnit()
        if soufredouleur is not None:
            soufredouleur.PushOrder(SacrificeOrder(soufredouleur), -1) 






# Mets tout les archers derrière le knight le plus proche d'eux, mets un avoid des range des autres archers
# Ils ont donc 2 ordres, un attackonsight, et un avoidorder
# faire une strtegie de coureur, il va devant les lignes enemis et cours de droite à gauche
# Les Pikeman doivent protéger les archers, faire en sorte

# stratégie de début possible, toutes les troupes reculent de 10 pas, 5 knight foncent à droite de la map pour dégager toutes
# les torupes de devant, le reste des knights foncent sur les archers en passant par la gauche
# les archers se decale à gauche. les Pikeman se mettent devant les archers
# les archers doivent être le plus séparé possible
# ----------------------

# Le but de RandomIQ est d'activer une stratégie aléatoire pour chaque troupe
# Utile pour se rendre compte après plusieurs milliarsd d'essais, les stratégies qui fonctionnent
# RandomIQ
# ----------------------
# ----------------------

class StrategieArcherFallbackSomeIQ(StrategyTroup):
    """quand il reste aucun archer vivant """

    def __init__(self):
        super().__init__(None, "All", "None")

    def applyOrder(self, general, unit):

        if unit.type == "knight":
            # knight → rush les archers ennemis
            unit.PushOrder(AttackOnSightOrder(unit,"archer"), 0)

        elif unit.type == "Pikeman":
            # Pikeman → focus les knights ennemis
            unit.PushOrder(AttackOnSightOrder(unit,"knight"), 0)


class StrategieNoKnightFallbackSomeIQ(StrategyTroup):
    """Quand il ne reste aucun knight vivant."""

    def __init__(self):
        super().__init__(None, "All", "None")

    def applyOrder(self, general, unit):
        if unit.type == "Archer":
            #les archers restent en arrière et focus ce qui s'avance
            unit.PushOrder(AttackOnSightOrder(unit,"All"), 0)

        elif unit.type == "Pikeman":
            # Les spikemen se mettent en garde du corps des archers et tapent tout
            archers = [u for u in general.MyUnits if u.type == "archer"]
            for archer in archers:
                unit.PushOrder(StayInFriendlySpaceOrder(unit, archer), 0)
            unit.PushOrder(AttackOnSightOrder(), 1)


class StrategieNoPikemanFallback(StrategyTroup):
    """Quand il ne reste aucun pikeman vivant."""

    def __init__(self):
        super().__init__(None, "All", "None")

    def applyOrder(self, general, unit):

        if unit.type == "Knight":
            #les knights jouent le rôle de frontline
            unit.PushOrder(AttackOnSightOrder(), 0)

        elif unit.type == "Archer":
            # Les archers restent à distance et focus surtout les unités de mêlée
            unit.PushOrder(AvoidOrder(unit, "knight"), 0)
            unit.PushOrder(AttackOnSightOrder(), 1)




# DIVISER LES TROUPES EN EQUIPES

# 0 archers adversaire 