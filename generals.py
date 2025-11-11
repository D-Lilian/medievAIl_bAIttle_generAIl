class WrongArguments(Exception):
    pass

class General:
    def __init__(self, unitsA, unitsB, sA , sK, sP, sS):
        # Set UNits
        if(len(unitsB) != len(unitsA) != 200):
            raise WrongArguments("Not enough arguments")
        self.MyUnits = unitsA
        self.HistUnits = unitsB

        # Set Orders
        for unit in self.MyUnits:
            unit.Orders = []

        # Set strategie
        self.sA = sA
        self.sK = sK
        self.sP = sP
        self.sS = sS
        return

    def BeginStrategy(self):
        for unit in self.MyUnits:
            self.sS.ApplyOrder(self, unit)

    def CreateOrders(self):
        for unit in self.MyUnits:
            match unit:
                case "Archer":
                    self.sA.ApplyOrder(unit)
                case "Knight":
                    self.K.ApplyOrder(unit)
                case "Spikeman":
                    self.P.ApplyOrder(unit)



class StrategyArcher:
    def __init__(self, favoriteTroup, hatedTroup):
        pass
    def ApplyOrder(self, general, unit):
        # Check dans les unités adverse si il ya un troupe de favorite troup et créé un ordre target
        # Check dans le sunités adverse si il ya une troupe de hated troup, et s'éloigne d'elle
        pass

class StrategyKnight:
    def __init__(self, favoriteTroup, hatedTroup):
        pass
    def ApplyOrder(self, unit):
        pass

class StrategyStart:
    def __init__(self, favoriteTroup, hatedTroup):
        pass
    def ApplyOrder(self, unit):
        # Ici donne a une troupe random par exemple le fait de se déplacer a l'autre bout de la map
        pass

class StrategySpikeman:
    def __init__(self, general, favoriteTroup, hatedTroup):
        if self.favoriteTroup == self.hatedTroup:
            raise WrongArguments("Favorite and hated troups cannot be the same")

        self.favoriteTroup = favoriteTroup
        self.hatedTroup = hatedTroup

        if not self.favoriteTroup in general.HistUnits:
            self.favoriteTroup = None
        pass

    def ApplyOrder(self, unit):
        pass

class MoveOrder:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class AttackOrder:
    "On assume ici que la target est forcément dans la list des troupes adverses"
    def __init__(self, target):
        self.target = target

class AttackInReachOrder:
    def __init__(self):
        pass

class AttackOnSightOrder:
    # Au debut de la partie les unités se "voient" forcément
    def __init__(self):
        pass


# DAFT
# ----------------------

class StrategieArcherDAFT(StrategyArcher):
    def __init__(self):
        super().__init__("Knight", "SpikeMan")
    def applyOrder(self, general, unit):
        pass

class StrategieKnightDAFT(StrategyKnight):
    def applyOrder(self, general, unit):
        pass

class StrategieSpikemanDAFT(StrategySpikeman):
    def applyOrder(self, general, unit):
        pass

class StrategieStart(StrategyStart):
    def applyOrder(self, general, unit):
        unit.PushOrder(AttackOnSightOrder, 0) # On push/insere/add un ordre de priorité 0
        pass

# ----------------------


# BrainDead
# ----------------------
# ----------------------


if __name__ == '__main__':
    unitsA = ["archer" for i in range(200)]
    unitsB = ["archer" for i in range(200)]

    DAFT1 = General(unitsA, unitsB)
    DAFT2 = General(unitsB, unitsA)

    pass


