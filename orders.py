#from generals import GameEngineError,WrongArguments
class Order:
    def __init__(self, unit):
        self.unit = unit

    def Try(self, simu):
        """
        Returns:
            bool: True si l'ordre est accompli et peut être supprimé
                  False si l'ordre doit être réessayé
        """
        raise NotImplementedError # On ne peut pas instancier la classe Ordre direct

    def __lt__(self, other):
        return

class MoveOrder(Order):
    def __init__(self, unit, x, y):
        super().__init__(unit)
        self.x = x
        self.y = y

    def Try(self, simu):
        if simu.ComparePosition(self.unit, self.x, self.y):
            return True # L'ordre a bien été réussi
        simu.MoveUnitClosestToXY(self.unit, self.x, self.y) # l'appel peut echouer ou pas, c pas grave on reessayera au prochain tick
        return False


class SacrificeOrder(Order):
    def __init__(self, unit):
        super().__init__(unit)
        self.unit = unit

    def Try(self, simu):
        # TODO
        raise NotImplemented
    # Fait la meme chose que avoid, + se déplace vers un coin opposé à la map



class MoveByStepOrder(Order):
    def __init__(self, unit, nbStep, direction):
        super().__init__(unit)
        self.unit = unit
        self.nbStep = nbStep
        self.direction = direction


    def Try(self, simu):
        if simu.MoveOneStepTowardsDir(self.unit, self.direction): # TODO angle
            simu.nbStep -= 1

        if self.nbStep == 0:
            return True
        elif self.nbStep < 0:
            raise Exception
            #raise GameEngineError("While trying to step back, nbStep got negative")
        return False

class AvoidOrder(Order):
    def __init__(self, unit, typeUnits):
        super().__init__(unit)
        self.unit = unit
        self.typeUnits = typeUnits

    def Try(self, simu):
        target = simu.GetNearestTroupInSight(self.unit, typeUnits=self.typeUnits)
        if target is None:
            return False # Il ya aucune enemy nearby

        if simu.IsInRange(target, self.Unit): # NOTE l'ordre des arguments ici est inversée
            if simu.MoveOneStepTowardsDir(self.unit,self.target, 180): # TODO angle
                return False
        else:
            return False

# Ici c'est un ordre qui vérifie systématiquement que l'unité n'est pas toute seule, cad que dans sa ligne of sight il ya au moins un allié, sinon, elle se dirige vers l'allié le plus proche
class StayInFriendlySpaceOrder(Order):
    def __init__(self, unit):
        super().__init__(unit)
        self.unit = unit

        #self.type = "permanent"


    def Try(self, simu):
        raise NotImplemented #il faut que le knight se rend cpte s'il sera trop loin des archers et revenir

class GetBehindOrder(Order):
    def __init__(self, unit, target):
        super().__init__(unit)
        self.unit = unit
        self.target = target

    def Try(self, simu):
        #TODO
        # Obsolète, meme chose que stayinfriendlyspace
        raise NotImplemented

class MoveTowardEnemyWithSpecificAttribute(Order):
    def __init__(self, unit, attribute_name, attribute_value, fixed=False):
        super().__init__(unit)
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value

    def Try(self, simu):
        #TODO
        raise NotImplemented


class AttackOrder(Order):
    "On assume ici que la target est forcément dans la list des troupes adverses"
    def __init__(self, unit, target):
        super().__init__(unit)
        self.target = target

    def Try(self, simu):
        # todo enlever le isinrgange
        if simu.IsInRange(self.unit, self.target):
            killed = simu.Kill(self.unit, self.target)
            if not killed:
                return False
            return True
        return False

class StayInReachOrder(Order):
    def __init__(self, unit, target):
        super().__init__(unit)
        self.target = target

    def Try(self, simu):
        if simu.IsInReach(self.unit, self.target):
            return False

        simu.MoveUnitClosestTo(self.unit, self.target) # se deplace le plus lioin possible en fonction de la capacité de la troupe
        return False


class AttackOnReachOrder(Order):
    def __init__(self, unit, typeTarget):
        super().__init__(unit)
        self.typeTarget = typeTarget

    def Try(self, simu):
        target = simu.GetNearestTroupInReach(self.unit, typeTarget=self.typeTarget)
        if target is None:
            return False
        simu.Kill(self.unit, target)
        return False

class AttackOnSightOrder(Order):
    # Au debut de la partie les unités se "voient" forcément
    # Le AttackOnSightOrder peut toujours etre accompli, cad il ne peut jamais se terminer, cad que l'appel à Try renvoi toujours False

    def __init__(self, unit, typeTargets):
        super().__init__(unit)
        self.typeTarget = typeTargets

    def Try(self, simu):
        target = simu.GetNearestTroupInSight(self.unit, typeTargets=self.typeTargets)
        if target is None:
            return False

        if simu.IsInRange(self.unit, target):
            simu.Kill(self.unit, target) # Renvoi faux si la troupe est morte, true sinon
            return
        else:
            #self.unit.PushOrder(MoveOrder(
            simu.MoveUnitClosestTo(self.unit, target) # se deplace le plus lioin possible en fonction de la capacité de la troupe
            return False
            # Redondant mais besoin pour la clarté du code
        return False

class FormationOrder(Order):
    def __init__(self, unit, units):
        super().__init__(unit)
        self.units = units # Ici units comprend totu les autres alliés

    def Try(self, simu, typeFormation="GROUPE"):
        # Qu'un seul type de formation (le groupe=
        if simu.IsInFormation(self.units, typeFormation): # check un rayon par ex
            return True
        simu.DoFormation(typeFormation, self.units) # renvoi trrue ou false en fonction
        return False

class isInDangerOrder(Order):
    def __init__(self,unit,friendly,typeTarget):
        super().__init__(unit)
        self.friendly = friendly
        self.typeTarget = typeTarget


    def Try(self,simu):
        target = simu.GetNearestTroupInSight(self.friendly, self.typeTarget)
        if target is None:
            return False

        simu.MoveUnitClosestTo(self.unit, target)
        return False



class _Node:
    def __init__(self, order):
        self.order = order
        self.prev = None
        self.next = None


class OrderManager:
    def __init__(self):
        self._head = None
        self._tail = None
        self._by_priority = {}
        self._by_order = {}

    def Add(self, order, priority):
        if priority in self._by_priority:
            raise ValueError("Priority already used")
        node = _Node(order)
        self._by_priority[priority] = node
        self._by_order[order] = priority

        if self._head is None:
            self._head = self._tail = node
            return

        keys = [p for p in self._by_priority if p < priority]
        if not keys:
            node.next = self._head
            self._head.prev = node
            self._head = node
            return

        insert_after = max(keys) # on prend la priorité maximale
        ref = self._by_priority[insert_after]
        node.next = ref.next
        node.prev = ref
        ref.next = node
        if node.next:
            node.next.prev = node
        else:
            self._tail = node

    def TryOrder(self, simu, order):
        if -1 in self._by_priority:
            if self._by_order[order] == -1:
                return order.Try(simu)
            else:
                return False # Tout les autres ordres ne sont pas effectué

        return order.Try(simu)
        #print("Trying order")
        #order.Try(simu)

    def Get(self, priority):
        n = self._by_priority.get(priority)
        return n.order if n else None

    def Remove(self, order):
        if order not in self._by_order:
            return False
        priority = self._by_order.pop(order)
        node = self._by_priority.pop(priority)

        if node.prev:
            node.prev.next = node.next
        else:
            self._head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self._tail = node.prev
        return True

    def RemoveOrderAtPriority(self, priority):
        n = self._by_priority.get(priority)
        if not n:
            return False
        return self.Remove(n.order)

    def __iter__(self):
        cur = self._head
        while cur:
            yield cur.order
            cur = cur.next

    def __len__(self):
        return len(self._by_priority)

    def __repr__(self):
        cur = self._head
        s = []
        while cur:
            p = self._by_order[cur.order]
            s.append(f"{cur.order.__class__.__name__}(p={p})")
            cur = cur.next
        if not s:
            return "OrderManager(empty)"
        return f"OrderManager([{', '.join(s)}])"

    # TODO implémenter l'addition d'un ordre qui prend le dessus sur tout les ordres, (le ordre enforcing)



if __name__ == "__main__":
    u1 = "Archer"
    u1 = Unit()
    om = OrderManager()
    u1.om = om

    u1.om.Add(MoveByStepOrder(u1, 10, 0), 0);
    u1.om.Add(MoveByStepOrder(u1, 2, 0), 1);
    u1.om.Add(MoveByStepOrder(u1, 3, 0), 2);
    u1.om.Add(MoveByStepOrder(u1, 4, 0), 3);

    for order in om:
        om.TryOrder("", order)
        om.Remove(order)


