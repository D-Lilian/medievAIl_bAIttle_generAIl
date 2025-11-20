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
