class StrategyStart:
    def __init__(self):
        pass

    def ApplyOrder(self, unit):
        # Ici donne a une troupe random par exemple le fait de se déplacer a l'autre bout de la map
        self.unit = unit
        raise NotImplemented#attaquer tout le monde par défaut pas sure

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
        units.PushOrder(AttackOnSightOrder, 0) # On push/insere/add un ordre de priorité 0

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
class StrategieArcherSomeIQ(StrategyTroup): #focus Spikeman (faibles au tir), évitent les Knights, restent groupés
    def __init__(self):
        super().__init__(None, "SpikeMan", "Knight")

    def applyOrder(self, general, unit):
        unit.PushOrder(AvoidOrder(unit,"knight"),0)  #éviter les knights

        if self.favorite_troup is not None:
            unit.PushOrder(AttackOnSightOrder(self.favorite_troup.lower()), 1)
        else:
            unit.PushOrder(AttackOnSightOrder(), 1)


class StrategieKnightSomeIQ(StrategyTroup):
    def __init__(self):
        super().__init__(None, "Archer", "SpikeMan") #PIIIKEEMAAANN
    def applyOrder(self, general, unit):
        unit.PushOrder(AttackOnSightOrder, 0) # On push/insere/add un ordre de priorité 0



class StrategieSpikemanSomeIQ(StrategyTroup):
    def __init__(self):
        super().__init__(None, "Knight", "Archer")
    def applyOrder(self, general, unit):
        unit.PushOrder(StayInReachOrder(unit, "Archer"), 0)
        unit.PushOrder(AttackOnSightOrder, 1) # On push/insere/add un ordre de priorité 0
       # stay in friendly zone a cote des archers et attaquer
    for archer in [u for u in general.MyUnits if u.Type == "archer"]:
        unit.PushOrder(StayInFriendlySpaceOrder(unit, archer), 0)
        # Attaque automatique des ennemis visibles
    unit.PushOrder(AttackOnSightOrder, 1)



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

class StrategieArcherFallbackSomeIQ(StrategyTroup):
    """quand il reste aucun archer vivant """

    def __init__(self):
        super().__init__(None, "All", "None")

    def applyOrder(self, general, unit):

        if unit.type == "knight":
            # knight → rush les archers ennemis
            unit.PushOrder(AttackOnSightOrder("archer"), 0)

        elif unit.type == "spikeman":
            # spikeman → focus les knights ennemis
            unit.PushOrder(AttackOnSightOrder("knight"), 0)


