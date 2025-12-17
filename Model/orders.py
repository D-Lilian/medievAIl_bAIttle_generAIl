# -*- coding: utf-8 -*-
"""
@file orders.py
@brief Order System - Commands for units

@details
Defines the Order class and its subclasses (Move, Attack, etc.).
Manages the execution and lifecycle of orders given to units.

"""
# from generals import GameEngineError,WrongArguments

#from Model import simulation


from Utils.logs import logger, setup_logger
from Model.units import Unit, UnitType
from Model.simulation import Simulation


# TODO FAIRE VIDEOS DES DIFFERENTS COMPORTEMENTS


class Order:
    def __init__(self, unit, squad_id=None):
        self.unit = unit
        self.squad_id = squad_id
        # On passe une fonction (lambda) à bind.
        # Elle sera appelée à chaque fois qu'un log est émis,
        # garantissant que les informations sont toujours à jour.

        log = logger.bind(order=str(self))
        self.log = log


    def Try(self, simu: Simulation):
        raise NotImplementedError

    def __lt__(self, other):
        return

    def __str__(self):
        return str(f"Order[{self.unit.__hash__()}/{self.__class__.__name__}]->[{self.unit.__class__.__name__}/{self.__hash__()} at ({self.unit.x}, {self.unit.y})]")

    #def __str__(self):
    #    return f"{self.__class__.__name__}(for {self.unit})"

class MoveOrder(Order):
    def __init__(self, unit, x, y):
        super().__init__(unit)
        self.x = x
        self.y = y

    def Try(self, simu):
        if simu.compare_position(self.unit, self.x, self.y):
            return True
        simu.move_unit_towards_coordinates(self.unit, self.x, self.y)
        return False


class SacrificeOrder(Order):
    def __init__(self, unit):
        super().__init__(unit)
        self.unit = unit

    def Try(self, simu:Simulation):
        self.log.debug("ЗА РОДИНУ !!!")
        simu.move_unit_towards_coordinates(self.unit, 0, 50)
        return False;
    # Fait la meme chose que avoid, + se déplace vers un coin opposé à la map



class MoveByStepOrder(Order):
    def __init__(self, unit, nbStep, direction):
        super().__init__(unit)
        self.unit = unit
        self.nbStep = nbStep
        self.direction = direction


    def Try(self, simu:Simulation):
        if simu.move_one_step_from_ref(self.unit, self.direction, "WORLD"):
            simu.nbStep -= 1
        if self.nbStep == 0:
            return True
        elif self.nbStep < 0:
            raise Exception
            #raise GameEngineError("While trying to step back, nbStep got negative")
        return False

class DontMoveOrder(Order):
    def __init__(self, unit, nb):
        super().__init__(unit)
        self.unit = unit
        self.nb = nb
        self._direction = -1


    def Try(self, simu:Simulation):
        simu.move_one_step_from_target_in_direction(self.unit, self.unit, -90*self._direction) # Fait croire a simu que l'unité a move
        self._direction *=-1
        if self.nb == 0:
            return True
        if self.nb < 0:
            raise Exception
            #raise GameEngineError("While trying to step back, nbStep got negative")
        self.nb -= 1
        return False

class AvoidOrder(Order):
    def __init__(self, unit, typeUnits):
        super().__init__(unit)
        self.unit = unit
        self.typeUnits = typeUnits

    def Try(self, simu):
        target = simu.get_nearest_enemy_in_sight(self.unit, type_target=self.typeUnits)
        if target is None:
            return False # Il ya aucune enemy nearby

        if simu.is_in_reach(target, self.unit):
            if simu.move_one_step_from_target_in_direction(self.unit, target, 180):
                return False
        else:
            return False

# Ici c'est un ordre qui vérifie systématiquement que l'unité n'est pas toute seule, cad que dans sa ligne of sight il ya au moins un allié, sinon, elle se dirige vers l'allié le plus proche
class StayInFriendlySpaceOrder(Order):
    def __init__(self, unit, typeUnit):
        super().__init__(unit)
        self.unit = unit
        self.typeUnit = typeUnit
        #self.type = "permanent"


    def Try(self, simu):
        friendly = simu.get_nearest_friendly_in_sight(self.unit, type_target=self.typeUnit)
        if friendly is None:
            return False # Il ya aucune enemy nearby

        if simu.is_in_reach(friendly, self.unit): # NOTE l'ordre des arguments ici est inversée
            if simu.move_unit_towards_unit(self.unit, friendly):
                return False
        else:
            return False


class MoveTowardEnemyWithSpecificAttribute(Order):
    def __init__(self, unit, attribute_name, attribute_value, fixed=False):
        super().__init__(unit)
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value
        self.fixed = fixed
        self.target = None

    def Try(self, simu):
        current_target = None

        if self.fixed and self.target:
            if self.target > 0:
                current_target = self.target
            else:
                self.target = None
                return False

        if current_target is None:
            current_target = simu.get_nearest_enemy_with_attributes( # TODO
                self.unit, self.attribute_name, self.attribute_value
            )

            if self.fixed and current_target:
                self.target = current_target

        if current_target:
            simu.move_unit_towards_unit(self.unit, current_target)

        return False

class AttackOrder(Order):
    "On assume ici que la target est forcément dans la list des troupes adverses"
    def __init__(self, unit, target):
        super().__init__(unit)
        self.target = target

    def Try(self, simu):
        if simu.is_in_reach(self.unit, self.target):
            killed = simu.attack_unit(self.unit, self.target)
            if not killed:
                return False
            return True
        return False

class StayInReachOrder(Order):
    def __init__(self, unit, target):
        super().__init__(unit)
        self.target = target

    def Try(self, simu):
        if simu.is_in_reach(self.unit, self.target):
            return False

        simu.move_unit_towards_unit(self.unit, self.target) # se deplace le plus lioin possible en fonction de la capacité de la troupe
        return False


class AttackOnReachOrder(Order):
    def __init__(self, unit, typeTarget):
        super().__init__(unit)
        self.typeTarget = typeTarget

    def Try(self, simu):
        target = simu.get_nearest_enemy_in_reach(self.unit, type_target=self.typeTarget)
        if target is None:
            return False
        simu.attack_unit(self.unit, target)
        return False

class AttackOnSightOrder(Order):
    # Au debut de la partie les unités se "voient" forcément
    # Le AttackOnSightOrder peut toujours etre accompli, cad il ne peut jamais se terminer, cad que l'appel à Try renvoi toujours False

    def __init__(self, unit, typeTarget):
        super().__init__(unit)
        self.typeTarget = typeTarget

    def Try(self, simu):
        target = simu.get_nearest_enemy_in_sight(self.unit, type_target=self.typeTarget)
        if target is None:
            return False

        if simu.is_in_reach(self.unit, target):
            simu.attack_unit(self.unit, target) # Renvoi faux si la troupe est morte, true sinon
            return False
        else:
            simu.move_unit_towards_unit(self.unit, target) # se deplace le plus lioin possible en fonction de la capacité de la troupe
            return False
            # Redondant mais besoin pour la clarté du code

class AttackNearestTroupOmniscient(Order):
    def __init__(self, unit, typeTarget):
        super().__init__(unit)
        self.typeTarget = typeTarget

    def Try(self, simu):
        target = simu.get_nearest_enemy_unit(self.unit, type_target=self.typeTarget)
        if target is None:
            self.log.debug(f"Aucune cible trouvée pour {self.unit}")
            return False

        if simu.is_in_reach(self.unit, target):
            simu.attack_unit(self.unit, target) # Renvoi faux si la troupe est morte, true sinon
            return False
        else:
            simu.move_unit_towards_unit(self.unit, target) # se deplace le plus lioin possible en fonction de la capacité de la troupe
            return False
            # Redondant mais besoin pour la clarté du code


class FormationOrder(Order):
    def __init__(self, unit, units):
        super().__init__(unit)
        self.units = units # Ici units comprend totu les autres alliés

    def Try(self, simu, type_formation='ROND'):
        # Qu'un seul type de formation (le groupe=
        if simu.is_in_formation(self.unit, self.units, type_formation): # check un rayon par ex
            return True
        simu.do_formation(self.unit, self.units, type_formation) # renvoi trrue ou false en fonction
        return False

class isInDangerOrder(Order):
    def __init__(self,unit,friendly,typeTarget):
        super().__init__(unit)
        self.friendly = friendly
        self.typeTarget = typeTarget


    def Try(self,simu):
        target = simu.get_nearest_enemy_in_sight(self.friendly, self.typeTarget)
        if target is None:
            return False

        simu.move_unit_towards_unit(self.unit, target)
        return False

class DumbOrder(Order):
    def __init__(self,unit,friendly,typeTarget):
        super().__init__(unit)
        self.friendly = friendly
        self.typeTarget = typeTarget

    def Try(self,simu, *args):
        self.log.debug("trying order")
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
        self.log =  logger.bind(order="order-manager")


    def AddMaxPriority(self, order, squad_id=None):
        node = _Node(order)
        keys = [p for p in self._by_priority if p >= 0]
        prio_max = max(keys) + 1 if keys else 0

        self._by_priority[prio_max] = node
        self._by_order[order] = prio_max

        if self._head is None:
            self.log.debug(f"Adding order at the beggining with prio {prio_max}")
            self._head = self._tail = node
            return

        self._tail.next = node
        node.prev = self._tail
        self._tail = node
        self.log.debug(f"Adding order with max priority of {prio_max}")


    def FlushOrders(self):
        self._head = None
        self._tail = None
        self._by_priority = {}
        self._by_order = {}

    def removeSquadOrders(self):
        orders_to_remove = [order for order in self._by_order if order.squad_id is not None]
        for order in orders_to_remove:
            self.Remove(order)



    #def Add(self, order, priority, squad_id=None):
    #    if priority in self._by_priority:
    #        raise ValueError(f"Priority already used {priority} by order {self._by_priority[priority].order}")
    #    node = _Node(order)
    #    self._by_priority[priority] = node
    #    self._by_order[order] = priority

    #    if self._head is None:
    #        self._head = self._tail = node
    #        return

    #    keys = [p for p in self._by_priority if p < priority]
    #    if not keys:
    #        node.next = self._head
    #        self._head.prev = node
    #        self._head = node
    #        return

    #    insert_after = max(keys) # on prend la priorité maximale
    #    ref = self._by_priority[insert_after]
    #    node.next = ref.next
    #    node.prev = ref
    #    ref.next = node
    #    if node.next:
    #        node.next.prev = node
    #    else:
    #        self._tail = node


    def Add(self, order, priority, squad_id=None):
        self.log.debug(f"Add called with priority={priority}")


        if priority in self._by_priority:
            raise ValueError(f"Priority already used {priority} by order {self._by_priority[priority].order}")

        node = _Node(order)
        self._by_priority[priority] = node
        self._by_order[order] = priority

        if self._head is None:
            self._head = self._tail = node
            return

        if priority == -1:
            node.next = self._head
            self._head.prev = node
            self._head = node
            return

        keys = [p for p in self._by_priority if 0 <= p < priority]
        if not keys:
            node.next = self._head
            self._head.prev = node
            self._head = node
            return

        insert_after = max(keys)
        ref = self._by_priority[insert_after]
        node.next = ref.next
        node.prev = ref
        ref.next = node
        if node.next:
            node.next.prev = node
        else:
            self._tail = node



    def TryOrder(self, simu, order):
        enforcing = self._by_priority.get(-1)
        if enforcing is not None:
            if enforcing.order is order:
                return order.Try(simu)
            return False
        return order.Try(simu)



    #def TryOrder(self, simu, order):
    #    if -1 in self._by_priority:
    #        if self._by_order[order] == -1:
    #            return order.Try(simu)
    #        else:
    #            return False # Tout les autres ordres ne sont pas effectué
#
#        return order.Try(simu)

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

    def __str__(self):
        cur = self._head
        s = []
        while cur:
            p = self._by_order[cur.order]
            s.append(f"{cur.order.__class__.__name__}(p={p})")
            cur = cur.next
        if not s:
            return "OrderManager(empty)"
        return f"OrderManager([{', '.join(s)}])"

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

    # quand on exécute ce fichier directement.
    import sys
    from pathlib import Path
    # On ajoute la racine du projet ('medievAIl_bAIttle_generAIl') au chemin de recherche
    project_root = Path(__file__).resolve().parent.parent
    sys.path.append(str(project_root))

    # Maintenant que le chemin est correct, on peut faire les imports pour le test
    from Model.units import Crossbowman
    from Utils.logs import setup_logger, logger

    u1 = Crossbowman('A', 0, 0)
    setup_logger(level="DEBUG", modules=["orders"])
    om = OrderManager()

    #om.Add(DumbOrder(u1, 10, 0), 0);
    #om.Add(DumbOrder(u1, 2, 0), 1);
    #om.Add(DumbOrder(u1, 3, 0), 2);
    #om.Add(DumbOrder(u1, 4, 0), 3);

    om.AddMaxPriority(DumbOrder(u1, 10, 0),);
    om.AddMaxPriority(DumbOrder(u1, 2, 0),);
    om.AddMaxPriority(DumbOrder(u1, 3, 0),);
    om.AddMaxPriority(DumbOrder(u1, 4, 0),);


    logger.debug(om)
    for order in om:
        om.TryOrder("", order)
        om.Remove(order)

    for order in om:
        #om.TryOrder("", order)
        om.Remove(order)
