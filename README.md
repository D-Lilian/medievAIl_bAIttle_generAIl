# MedievAIl_bAIttle_generAIl
## Description
TODO

### Généraux disponibles
#### Braindead
TODO description

#### Daft
TODO description

#### SomeIQ
TODO description

#### RandomIQ
TODO description


## Screenshots
TODO

### Terminal View
#### Fonctionalités
- Zoom In/ Zoom Out
- Stop
- Increase/Decrease tick
- Save/Load

TODO

### 2.5D View

#### Fonctionalités
- Stop
- Increase/Decrease tick

## Installation

Il faut d'abord installer créer un venv

```bash
python3 -m venv .venv
````

Puis l'activer

```bash
source .venv/bin/activate
```
Puis installer les dépendances

```bash
pip install -r requirements.txt
```

## Utilisation

TODO spécifier l'entrypoint

Le programme s'exécute via la ligne de commande et supporte plusieurs commandes principales : `run`, `load`, `tourney`, et `plot`.

## Commandes disponibles

### 1\. `run` : Lancer une bataille simple
Exécute une seule confrontation entre deux intelligences artificielles sur un scénario donné.

| Argument | Description |
| :--- | :--- |
| `scenario` | Nom du scénario à exécuter. |
| `ai1` | Nom de l'IA pour l'équipe 1. |
| `ai2` | Nom de l'IA pour l'équipe 2. |
| `-t` | (Optionnel) Affiche la vue terminale. |
| `-d / --datafile` | (Optionnel) Fichier où écrire les données de la bataille. |

### 2\. `load` : Charger une bataille

Reprend une bataille à partir d'un fichier de sauvegarde.

| Argument | Description |
| :--- | :--- |
| `savefile` | Chemin d'accès au fichier de sauvegarde (`.sav`). |


### 3\. `tourney` : Organiser un tournoi

Exécute une série de matchs entre plusieurs IA et scénarios.

| Argument | Description |
| :--- | :--- |
| `-G / --ais` | **Liste** des noms d'IA participantes (requis). |
| `-S / --scenarios` | **Liste** des scénarios à jouer (requis). |
| `-N` | Nombre de manches pour chaque confrontation (Défaut: 10). |
| `-na / --no-alternate` | Désactive l'alternance des positions des joueurs (AI1 vs AI2) pour chaque manche. |

### 4\. `plot` : Simuler et tracer des résultats

Génère un graphique en faisant varier un paramètre spécifique d'un scénario.

| Argument | Description |
| :--- | :--- |
| `<ai>` | Nom de l'IA à utiliser pour la simulation. |
| `<plotter>` | Nom de la fonction de traçage (plotting) à exécuter. |
| `<scenario_params>` | **Deux arguments** : `NomScenario` et le `Paramètre` à faire varier (ex: `Lanchester N`). |
| `<range_params>` | **Liste des valeurs** pour la plage du paramètre (ex: `1 100 1` pour `range(1, 100)`). |
| `-N` | Nombre de répétitions pour chaque valeur de paramètre (Défaut: 10). |