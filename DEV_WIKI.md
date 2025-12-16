# Propritétés d'un ordre

- A une priorité (-1, 0, 1, 2, 3)
- Une méthode d'iniatlisation
- Une méthode Try qui renvoie False ou True
- Un ordre attaque ne peut pas etre effectué 2 fois par tour
- Un ordre mouvement ne peut pas etre effectué 2 fois par tour

# Priorités

Priorité de 0 > priorité de 1
Priorité de -1: seul ordre qui peut être effectué, aucun autre ordre n'est executé j'usqu'au tour suivant
Une troupe ne peut avoir 2 ordres de la même priorité

# Types d'ordres

## ComparePosition(self.unit, self.x, self.y)
>
> Compare la position de la troupe avec les coordonnées x,y (moyennant un rayon)

## MoveUnitClosestToXY(self.unit, self.x, self.y) # l'appel peut echouer ou pas, c pas grave on reessayera au prochain tick
>
> Déplace l'unité de sa capacité de déplacement maximale vers les coordonnées X et T

## DoFormation(typeFormation, self.units) # renvoi trrue ou false en fonction
>
> Déplace les unités ensemble, attire donc chaque unité l'une vers l'autre pour faire une formation ROND
> typeFormation est de type ROND toujours
>
## MoveOneStepFromTarget(self.unit, self.Target, self.direction)
>
> Se  déplace en se basant sur le réferentiel de self.Target, self.direction est un angle
> Donc MoveOneStepFromTarget(unitAlly, unitEnemy, 180) fait un pas dans la direction opposé de unitEnemy
> Donc MoveOneStepFromTarget(unitAlly, unitEnemy, 0) fait un pas dans la direction de unitEnemy
>
## MoveOneStepFromRef(self.unit, self.direction, self.ref)
>
> Déplace une unité avec un angle de direction en se basant sur un référentiel. Actullement self.ref vaut WORLD

## IsInFormation(self.units, typeFormation): # check un rayon par ex
>
> Check si une liste d'unités sont en formations. La formation ici est juste ROND, on check si la liste de troupes est dans un rayon"

## IsInReach(self.unit, self.target)
>
> Regarde si l'unité self.unit est dans la reach de l'unité self.target
>
## GetNearestTroupInSight(self.unit, typeTarget=self.typeTarget)
>
> Renvoie une unité de type typeTarget qui sont dans la sight de self.unit
>
## GetNearestTroupInReach(self.unit, typeTarget=self.typeTarget)
>
> Renvoie une unité de type typeTarget qui sont dans la reach de self.unit
>
## Kill(self.unit, target)
>
> Demande a la simulation de tuer target à l'aide de self.unit
