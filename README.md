# MedievAIl bAIttle generAIl

Medieval battle simulator with AI generals, data analysis, and Lanchester's Laws verification.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Quick Start

```bash
# Run a battle (2.5D view)
./battle run classic DAFT BRAINDEAD

# Run in terminal mode
./battle run classic DAFT BRAINDEAD -t

# Run Lanchester analysis
./battle plot DAFT PlotLanchester Lanchester '[Knight,Crossbow]' 'range(10,50,10)' -N 5

# Run a tournament
./battle tourney -G DAFT BRAINDEAD SOMEIQ -N 10
```

## Commands

| Command | Description |
|---------|-------------|
| `run <scenario> <ai1> <ai2>` | Run a battle between two AIs |
| `load <savefile>` | Load a saved game |
| `tourney` | Run a tournament |
| `plot` | Run Lanchester analysis |

### run

```bash
./battle run <scenario> <ai1> <ai2> [-t]
```

| Option | Description |
|--------|-------------|
| `-t` | Terminal view (default: 2.5D Pygame view) |

Press **F9** to switch from Terminal to 2.5D view during battle.

### load

```bash
./battle load <savefile>
```

Loads a `.pkl` save file from `save/` directory.

### tourney

```bash
./battle tourney [-G AI1 AI2 ...] [-S SCENARIO1 ...] [-N rounds] [-na]
```

| Option | Description |
|--------|-------------|
| `-G` | List of AIs (default: all) |
| `-S` | List of scenarios (default: all) |
| `-N` | Rounds per matchup (default: 10) |
| `-na` | Disable position alternation |

### plot

```bash
./battle plot <AI> <Plotter> <Scenario> '[types]' 'range(min,max,step)' [-N reps]
```

| Argument | Example |
|----------|---------|
| AI | `DAFT`, `BRAINDEAD`, `SOMEIQ`, `RPC` |
| Plotter | `PlotLanchester`, `PlotCasualties`, `PlotUnitComparison`, etc. |
| Scenario | `Lanchester` (for PlotLanchester only), `classic`, `shield_wall` |
| types | `'[Knight,Crossbowman]'` |
| range | `'range(10,50,10)'` |
| -N | Number of repetitions (default: 10) |

**Available Plotters:**

| Plotter | Description | Scenario |
|---------|-------------|----------|
| `PlotLanchester` | Lanchester's Laws analysis (N vs 2N) | `Lanchester` only |
| `PlotCasualties` | Casualties by unit type | Any |
| `PlotWinRate` | Win rate analysis | Any |
| `PlotDuration` | Battle duration analysis | Any |
| `PlotUnitComparison` | Unit type effectiveness | Any |
| `PlotDamageMatrix` | Damage dealt between unit types | Any |
| `PlotKillEfficiency` | Kill efficiency per unit type | Any |

**Note:** `PlotLanchester` requires `Lanchester` scenario and vice versa.

**Output:**

- `Reports/lanchester_data.csv` - Raw data
- `Reports/<plotter>_*.png` - Plot
- `Reports/lanchester_report_*.html` - Full report (PlotLanchester only)

## AI Generals

| General | Description |
|---------|-------------|
| `BRAINDEAD` | Attack nearest visible enemy |
| `DAFT` | Attack globally nearest enemy |
| `SOMEIQ` | Unit-specific tactics with formations |
| `RPC` | Rock-Paper-Counter targeting |

### General Architecture

Each general has:

- **sT** (Strategy per Type): Behavior per unit type
- **sS** (Start Strategy): Initial formations/positioning

```python
from Model.general_factory import create_general

general_a = create_general("SOMEIQ", scenario.units_a, scenario.units_b)
general_b = create_general("DAFT", scenario.units_b, scenario.units_a)
```

## Unit Types

| Unit | Type | Notes |
|------|------|-------|
| Knight | Melee | Heavy cavalry |
| Pikeman | Melee | Anti-cavalry |
| Crossbowman | Ranged | Focus fire |

## Scenarios

| Scenario | Size | Description |
|----------|------|-------------|
| `classic` | 100v100 | Agincourt style |
| `large_battle` | 200v200 | Large scale |
| `cavalry_charge` | 100v100 | Heavy cavalry |
| `shield_wall` | 120v120 | Defensive |
| `cannae` | 150v150 | Hammer and anvil |
| `Lanchester` | N vs 2N | For analysis |

## Lanchester's Laws

The `Lanchester` scenario tests combat theory:

- **Linear Law** (Melee): Casualties ∝ N
- **Square Law** (Ranged): Casualties ∝ √N

Team A (N units) vs Team B (2N units). Analyze winner casualties to verify the laws.

## Terminal Controls

| Key | Action |
|-----|--------|
| P | Pause/Resume |
| M | Cycle zoom (1x/2x/3x) |
| A | Auto-follow camera |
| ZQSD/Arrows | Move camera |
| +/- | Speed up/down |
| F1-F4 | Toggle info panels |
| E | Quick save |
| Tab | Generate HTML report |
| F9 | Switch to 2.5D view |
| ESC | Exit |

## Architecture

The project follows the **MVC** (Model-View-Controller) pattern with specialized modules.

``` txt
medievAIl_bAIttle_generAIl/
│
├── battle                 # Entry point (bash script)
├── main.py                # Python entry point
│
├── Model/                 # MODEL - Business logic
│   ├── units.py           # Unit classes (Knight, Pikeman, Crossbowman)
│   ├── generals.py        # General AI logic
│   ├── general_factory.py # Factory pattern for general creation
│   ├── strategies.py      # General strategies (BRAINDEAD, DAFT, SOMEIQ, RPC)
│   ├── orders.py          # Order system (Move, Attack, Formation)
│   ├── scenario.py        # Battle configuration
│   └── simulation.py      # Simulation engine
│
├── View/                  # VIEW - Display
│   ├── pygame_view.py     # 2.5D isometric view (Pygame)
│   ├── terminal_view.py   # Terminal view (curses)
│   ├── renderers/         # Rendering components (map, UI, debug)
│   ├── report_generator.py # HTML report generation
│   ├── state.py           # View state
│   ├── stats.py           # Real-time statistics
│   └── data_types.py      # Shared data types
│
├── Controller/            # CONTROLLER - Orchestration
│   ├── simulation_controller.py  # Simulation control
│   ├── pygame_controller.py      # 2.5D view control
│   ├── terminal_controller.py    # Terminal view control
│   ├── hybrid_controller.py      # View switching (F9)
│   ├── plot_controller.py        # Lanchester analysis
│   └── tournament_controller.py  # Tournaments
│
├── Plotting/              # DATA SCIENCE - Analysis
│   ├── base.py            # Abstract plotters (plotnine/ggplot2)
│   ├── lanchester.py      # PlotLanchester analysis
│   ├── data.py            # LanchesterData (pandas DataFrame)
│   ├── collector.py       # Parallel collection (multiprocessing)
│   └── report.py          # HTML report generation with graphs
│
├── Tournament/            # TOURNAMENTS
│   ├── config.py          # Tournament configuration
│   ├── runner.py          # Match execution
│   ├── results.py         # Results and rankings
│   └── report.py          # Tournament HTML reports
│
├── Utils/                 # UTILITIES
│   ├── eval.py            # CLI dispatcher (run, load, plot, tourney)
│   ├── parse_cli.py       # Argument parsing
│   ├── predefined_scenarios.py  # Predefined scenarios
│   ├── save_load.py       # Save/load (.pkl)
│   ├── statistical.py     # Statistical analysis
│   ├── logs.py            # Logging (loguru)
│   └── errors.py          # Custom exceptions
│
├── Tests/                 # UNIT TESTS
│   ├── orders_test.py
│   ├── plotting_tests.py
│   ├── tournament_tests.py
│   └── general_factory_tests.py
│
├── Reports/               # OUTPUT - Generated reports
└── assets/                # ASSETS - Sprites and images
```
