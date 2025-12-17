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
| Plotter | `PlotLanchester` |
| Scenario | `Lanchester` |
| types | `'[Knight,Crossbow]'` |
| range | `'range(10,50,10)'` |
| -N | Number of repetitions (default: 10) |

**Output:**

- `Reports/lanchester_data.csv` - Raw data
- `Reports/lanchester_analysis_*.png` - Plot
- `Reports/lanchester_report_*.html` - Full report (auto-opens)

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

```text
├── Controller/          # Orchestration (MVC Controller)
├── Model/               # Domain logic (Units, Generals, Simulation)
├── View/                # Visualization (Terminal, Pygame)
├── Plotting/            # Data science (plotnine, pandas)
├── Tournament/          # Tournament system
└── Utils/               # CLI, save/load, utilities
```

## Project Structure

```text
battle                   # Main entry point (bash script)
├── main.py              # Python entry
├── Utils/
│   ├── eval.py          # Command dispatcher
│   └── parse_cli.py     # CLI argument parsing
├── Controller/
│   ├── simulation_controller.py
│   ├── hybrid_controller.py   # View switching
│   ├── tournament_controller.py
│   └── plot_controller.py
├── Model/
│   ├── units.py
│   ├── generals.py
│   ├── general_factory.py
│   ├── strategies.py
│   └── simulation.py
├── Plotting/
│   ├── base.py          # Plotters (plotnine)
│   ├── data.py          # LanchesterData (pandas)
│   ├── collector.py     # Parallel simulation runner
│   └── report.py        # HTML report generator
└── Reports/             # Output directory
```
