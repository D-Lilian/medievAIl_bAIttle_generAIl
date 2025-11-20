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
