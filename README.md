# MedievAIl_bAIttle_generAIl

## Description

A medieval battle simulation engine with AI generals, comprehensive data analysis, and visualization tools. Features tournament systems, Lanchester's Laws analysis, and multiple scenario types.

### Architecture

The project follows **MVC** architecture with **SOLID** principles:

```
├── Controller/          # Orchestration layer
│   ├── simulation_controller.py
│   ├── terminal_controller.py
│   ├── tournament_controller.py
│   └── plot_controller.py
├── Model/               # Domain logic
│   ├── simulation.py
│   ├── scenario.py
│   ├── units.py
│   ├── generals.py
│   ├── strategies.py
│   └── orders.py
├── View/                # Visualization
│   ├── terminal_view.py
│   └── renderers/
├── Plotting/            # Data visualization
│   ├── base.py          # Generic plotters
│   ├── scenario_plotters.py  # Scenario-specific plotters
│   ├── collector.py     # Data collection
│   └── lanchester.py    # Lanchester scenario
├── Tournament/          # Tournament system
│   ├── runner.py
│   └── report.py
├── Analysis/            # Statistical analysis
│   ├── statistics.py
│   └── visualizers.py
└── Utils/               # Utilities
    ├── eval.py          # CLI dispatcher
    └── parse_cli.py     # Argument parsing
```

### Available Generals

| General | Description |
|---------|-------------|
| `BRAINDEAD` | Basic AI with no tactical awareness - units attack nearest enemy |
| `DAFT` | Default AI with simple tactics and formation awareness |
| `SOMEIQ` | Smarter AI with unit-specific strategies (crossbow kiting, knight charging, etc.) |

### Available Unit Types

| Unit | Type | Description |
|------|------|-------------|
| `Knight` | Melee | Heavy cavalry, high damage and HP |
| `Pikeman` | Melee | Infantry with reach, effective vs cavalry |
| `Crossbowman` | Ranged | Ranged unit, focus fire capable |
| `LongSwordsman` | Melee | Balanced infantry |
| `EliteSkirmisher` | Ranged | Fast ranged unit |
| `CavalryArcher` | Ranged | Mobile ranged cavalry |
| `LightCavalry` | Melee | Fast cavalry |
| `Onager` | Siege | Area damage siege weapon |
| `Scorpion` | Siege | Anti-personnel siege weapon |
| `Trebuchet` | Siege | Long-range siege weapon |

## Screenshots

TODO

### Terminal View

The Terminal View is an interactive, real-time visualization of medieval battles using a curses-based terminal interface. It provides complete control over simulation playback, camera positioning, and detailed battle analysis through both terminal UI and generated HTML reports.

#### Architecture

Built following SOLID principles with a clean MVC separation of concerns:

**View Layer** (Refactored into `View/` module):

- **TerminalView** (`View/terminal_view.py`): Main facade class coordinating all components
- **InputHandler** (`View/input_handler.py`): Processes keyboard input with configurable callbacks
- **Renderers** (`View/renderers/`):
  - **MapRenderer**: Renders the battlefield grid
  - **UIRenderer**: Displays informational panels and overlays
  - **DebugRenderer**: Shows debug info
- **UnitCacheManager** (`View/unit_cache.py`): Manages unit data extraction and caching
- **ReportGenerator** (`View/report_generator.py`): Handles HTML report generation
- **State** (`View/state.py`): `ViewState` and `Camera` classes
- **Stats** (`View/stats.py`): Statistics tracking
- **Data Types** (`View/data_types.py`): Enums and data classes (`UnitRepr`, `Team`, etc.)

**Controller Layer** (`Controller/terminal_controller.py`):

- **TerminalController**: Orchestrates interaction between SimulationController and TerminalView, syncing state bidirectionally

**Model Layer** (read-only from View):

- View accesses simulation state without modifying it, maintaining clean MVC separation

#### Features

**Visualization**:

- **Real-time Rendering**: Smooth 60 FPS display with double-buffered rendering to prevent flicker
- **Zoom Control**: 3 zoom levels (1x, 2x, 3x) toggled with 'M' key for tactical overview or detailed unit view
- **Team Coloring**: Cyan for Team A, Red for Team B, with bold rendering for alive units
- **Unit Letters**: Each unit type displays with a distinctive letter (K=Knight, P=Pikeman, C=Crossbowman, etc.)
- **Dynamic Updates**: Unit positions, HP, and status update in real-time as simulation progresses

**Camera & Navigation**:

- **Manual Control**: Navigate with ZQSD/Arrow keys (5 units/tick normal, 15 units/tick with Shift)
- **Auto-follow Mode**: Automatic tracking of units' center of mass with 'A' key toggle
- **Viewport Clamping**: Camera bounds automatically constrain to battlefield edges
- **Zoom-aware Movement**: Movement speed scales with zoom level for consistent feel

**Simulation Control**:

- **Pause/Resume**: 'P' key freezes simulation while keeping view interactive
- **Variable Speed**: Adjust from 1-240 ticks/second with +/- keys (default: 5 tps)
- **Bidirectional Sync**: View and simulation controller maintain synchronized pause and speed state
- **End Detection**: Simulation auto-pauses when one team is eliminated
- **Headless Mode**: Exiting the view (ESC) switches simulation to headless mode (unpaused, max speed) to finish in background

**UI & Information**:

- **F1 - Unit Counts**: Team-wise alive/dead counts and total units
- **F2 - Unit Types**: Breakdown by type (Knight, Pikeman, Crossbowman, etc.) per team
- **F3 - Simulation Info**: Wall-clock time, pause status, zoom level, camera position, auto-follow state, tick speed
- **F4 - Toggle All**: Show/hide all panels simultaneously
- **Pause Overlay**: Visual indicator when simulation is paused
- **Help Bar**: Always-visible control reminder at bottom of screen
- **Smart Target Inference**: View automatically deduces unit targets from orders (even implicit ones like AttackOnSight)

**Persistence & Reports**:

- **Quick Save (E)**: Saves scenario state to timestamped `.pkl` files in `save/` directory
- **HTML Reports (Tab)**: Generates comprehensive battle reports with:
  - Interactive unit cards with detailed stats (HP, damage, position, target, speed, range, etc.)
  - Visual battlefield map with clickable unit positions
  - Unit breakdown by type with progress bars
  - Enhanced target display: Shows target name and ID (e.g., "Pikeman #3")
  - Automatic browser launch with timestamp-based filenames
  - Modern CSS styling with team colors, gradients, and hover effects

**Development Tools**:

- **Debug Mode (Ctrl+D)**: Overlay showing detailed unit info for first 6 units
- **Clean Exit (ESC)**: Proper curses cleanup and simulation shutdown

#### Controls Summary

Complete keyboard mapping for terminal view interaction:

| Key | Action | Description |
|-----|--------|-------------|
| **P** | Pause/Resume | Toggle simulation execution without closing the view |
| **M** | Cycle Zoom | Switch between 1x, 2x, and 3x zoom levels |
| **A** | Auto-follow | Enable/disable automatic camera tracking of units |
| **Z/↑** | Move Up | Scroll camera upward (normal speed) |
| **S/↓** | Move Down | Scroll camera downward (normal speed) |
| **Q/←** | Move Left | Scroll camera left (normal speed) |
| **D/→** | Move Right | Scroll camera right (normal speed) |
| **Shift+ZQSD** | Fast Move | Move camera at 3x speed in any direction |
| **+/=** | Speed Up | Increase simulation speed by 5 ticks/second |
| **-/_** | Speed Down | Decrease simulation speed by 5 ticks/second (minimum 1) |
| **F1** | Toggle Unit Counts | Show/hide team unit statistics panel |
| **F2** | Toggle Unit Types | Show/hide unit type breakdown panel |
| **F3** | Toggle Sim Info | Show/hide simulation status and performance panel |
| **F4** | Toggle All Panels | Show/hide all UI panels at once |
| **E** | Quick Save | Save current game state to timestamped file |
| **Tab** | Generate Report | Create detailed HTML battle report and open in browser |
| **Ctrl+D** | Debug Mode | Toggle detailed debug information overlay |
| **ESC** | Exit | Close terminal view and end simulation |

#### Implementation Details

**Target Resolution**:
Unit targets displayed in reports are resolved from orders using this priority:

1. `order.current_target` (dynamically updated target from order execution)
2. `order.target` (initial target specified in order)
3. If no target found, displayed as "None"

This ensures the view reflects actual tactical decisions made by AI strategies.

**Time Tracking**:

- **Displayed Time**: Wall-clock elapsed time (pause-aware)
- **Simulation Time**: Tick-based progression in background thread
- View maintains separate time tracking to provide stable, user-friendly display

**Performance Optimizations**:

- Double-buffered rendering (`noutrefresh()` + `doupdate()`) prevents screen flicker
- Unit caching reduces redundant data extraction from simulation
- Frame-time budgeting maintains consistent FPS regardless of tick speed
- Efficient curses attribute management with pre-defined color pairs

**Auto Camera Mode**:
When enabled (A key), camera automatically centers on barycenter of all alive units:

```python
center_x = sum(u.x for u in alive_units) / len(alive_units)
center_y = sum(u.y for u in alive_units) / len(alive_units)
```

Provides dynamic view that follows the action. Manual movement disables auto-follow.

**HTML Report Features**:

- **Interactive Selection**: Click any unit card or map dot to select it
- **Target Highlighting**: When a unit is selected, its target is automatically highlighted
- **Responsive Layout**: Cards and map adapt to screen size
- **Color Coding**: Team A (cyan), Team B (red), Dead units (gray)
- **Status Indicators**: HP bars with color-coded critical/low health states
- **Comprehensive Stats**: Position, damage dealt, target, speed, range, armor, attack, accuracy

**Keyboard Handling**:

- ESC delay minimized with `ESCDELAY=25` environment variable
- Non-blocking input with `nodelay(True)` curses mode
- Shift key detection for fast camera movement
- Function key support (F1-F4) for panel toggles and actions

### 2.5D View

#### Functionalities

- Stop
- Increase/Decrease tick

## Installation

First, create a virtual environment

```bash
python3 -m venv .venv
```

Then activate it

```bash
source .venv/bin/activate
```

Then install the dependencies

```bash
pip install -r requirements.txt
```

## Usage

TODO specify entrypoint

The program runs via command line and supports several main commands: `run`, `load`, `tourney`, and `plot`.

## Available Commands

### 1\. `run`: Run a simple battle

Executes a single confrontation between two artificial intelligences on a given scenario.

| Argument | Description |
| :--- | :--- |
| `scenario` | Name of the scenario to execute. |
| `ai1` | Name of the AI for team 1. |
| `ai2` | Name of the AI for team 2. |
| `-t` | (Optional) Displays the terminal view. |
| `-d / --datafile` | (Optional) File where battle data will be written. |

### 2\. `load`: Load a battle

Resumes a battle from a save file.

| Argument | Description |
| :--- | :--- |
| `savefile` | Path to the save file (`.sav`). |

### 3\. `tourney`: Organize a tournament

Runs a fully automated tournament between AI generals, generating comprehensive HTML reports with score matrices.

| Argument | Description |
| :--- | :--- |
| `-G / --ais` | **List** of participating AI names. Default: all available (BRAINDEAD, DAFT, SOMEIQ). |
| `-S / --scenarios` | **List** of scenarios to play. Default: all available. |
| `-N` | Number of rounds for each matchup (Default: 10). |
| `-na / --no-alternate` | Disables alternation of player positions for fairness testing. |

#### Tournament Features

- **All pairwise matchups** including reflexive (X vs X) to detect position bias
- **Position alternation** (by default) ensures fairness - each general plays both sides
- **Comprehensive HTML report** with:
  - Overall standings with win percentages
  - General vs General matrix (across all scenarios)
  - Per-scenario matrices
  - General vs Scenario performance
  - Reflexive matchup analysis (should be ~50% to confirm no position bias)

#### Example Usage

```bash
# Run tournament with all generals and scenarios (10 rounds each)
python battle.py tourney -G DAFT BRAINDEAD SOMEIQ -N 10

# Run tournament with specific scenarios
python battle.py tourney -G DAFT BRAINDEAD -S classical_medieval_battle cavalry_charge -N 5

# Run without position alternation (to test for position bias)
python battle.py tourney -G DAFT BRAINDEAD -N 20 -na
```

#### Available Generals

| General | Description |
| :--- | :--- |
| `BRAINDEAD` | Basic AI with no tactical awareness |
| `DAFT` | Default AI with simple tactics |
| `SOMEIQ` | Smarter AI with unit-specific strategies |

#### Available Scenarios

| Scenario | Description |
| :--- | :--- |
| `classical_medieval_battle` | 100v100 - Classic Medieval Battle |
| `defensive_siege` | 120v120 - Defensive Formation |
| `cavalry_charge` | 150v150 - Offensive Wedge |
| `cannae_envelopment` | 180v180 - Hammer and Anvil |
| `british_square` | 120v120 - Hollow Square |

### 4\. `plot`: Simulate and plot results

Generates graphs by running scenarios with varying parameters and produces both PNG plots and Markdown reports.

#### Syntax

```bash
battle plot <AI> <Plotter> <Scenario> [types] range(min,max[,step]) [-N reps] [--stats]
```

| Argument | Description |
| :--- | :--- |
| `AI` | Name of the AI to use (DAFT, BRAINDEAD, SOMEIQ). |
| `Plotter` | Name of the plotting function (PlotLanchester, PlotCasualties, etc.). |
| `Scenario` | Scenario name (currently: Lanchester). |
| `[types]` | Unit types as `[Type1,Type2]` (e.g., `[Knight,Crossbow]`). |
| `range(...)` | Range expression: `range(min,max)` or `range(min,max,step)`. |
| `-N` | Number of repetitions per configuration (Default: 10). |
| `--stats` | Enable full statistical analysis with hypothesis tests and advanced visualizations. |

#### How It Works

The command does roughly this (pseudo code):

```python
for type in [Knight, Crossbow]:
    for N in range(1, 100):
        data[type, N] = Lanchester(type, N).run()  # repeat N times
PlotLanchester(data)
```

Where:

- `Lanchester(type, N)` creates a scenario with N units vs 2N units of the same type
- `data[type, N]` contains: casualties, survivors, total HP damage on each side
- `PlotLanchester(data)` produces pertinent graphs to visualize that data

#### Available Plotters

Three categories of plotters are available:

**Scenario-Specific Plotters (recommended):**

Each predefined scenario has a dedicated plotter with relevant visualizations:

| Plotter | Scenario | Description |
|---------|----------|-------------|
| `PlotLanchester` / `Lanchester` | Lanchester | N vs 2N analysis - tests Linear vs Square Law |
| `PlotClassicMedieval` / `ClassicMedieval` | classic_medieval_battle | 100v100 Agincourt-style battle analysis |
| `PlotCavalryCharge` / `CavalryCharge` | cavalry_charge | 150v150 charge impact and K/D ratio |
| `PlotDefensiveSiege` / `DefensiveSiege` | defensive_siege | 120v120 shield wall effectiveness |
| `PlotCannaeEnvelopment` / `CannaeEnvelopment` | cannae_envelopment | 180v180 flanking maneuver analysis |
| `PlotRomanLegion` / `RomanLegion` | roman_legion | 100v100 testudo formation analysis |
| `PlotBritishSquare` / `BritishSquare` | british_square | 120v120 anti-cavalry square analysis |

**Generic Plotters (matplotlib-based):**

| Plotter | Description |
|---------|-------------|
| `PlotCasualties` | Simple casualties comparison between teams |
| `PlotSurvivors` | Shows surviving units for both teams |
| `PlotWinRate` | Visualizes win rate analysis |

**ggplot2-style (plotnine - publication quality):**

Uses plotnine, the Python equivalent of R's ggplot2, for publication-quality visualizations.

| Plotter | Description |
| :--- | :--- |
| `GGPlotLanchester` | Beautiful multi-panel Lanchester analysis with individual plots saved separately. |
| `GGPlotCasualties` | Elegant faceted casualties comparison with team colors. |
| `GGPlotSurvivors` | Survival rate visualization with area ribbons. |
| `GGPlotWinRate` | Win rate with reference lines and color fills. |
| `GGPlotLanchesterComparison` | Direct comparison of casualty scaling between unit types. |

#### Statistical Analysis Mode (`--stats`)

When using the `--stats` flag, the system performs comprehensive statistical analysis:

**Lanchester Law Testing:**
- Fits Linear, Quadratic, and Square Root models
- Calculates R² for each model to determine best fit
- Validates whether data matches theoretical expectations (Linear Law for melee, Square Law for ranged)

**Hypothesis Testing:**
- Independent t-tests comparing unit types
- Mann-Whitney U tests (non-parametric alternative)
- ANOVA for 3+ unit types
- Chi-square tests for proportions

**Effect Size Calculations:**
- Cohen's d with interpretation (small/medium/large)
- Eta-squared for ANOVA
- 95% Confidence intervals

**Advanced Visualizations Generated:**
- `correlation_heatmap.png` - Cross-correlation matrix of all metrics
- `boxplot.png` - Casualty distributions by unit type
- `grouped_barplot.png` - Mean casualties comparison with error bars
- `mean_comparison.png` - Mean with 95% CI
- `histogram.png` - Battle duration distribution
- `metric_heatmap.png` - N × casualties heatmap

#### Available Scenarios for Plotting

| Scenario | Signature | Description |
|----------|-----------|-------------|
| `Lanchester` | N vs 2N | Tests Lanchester's Laws - use N ≥ 20 for visible differences |
| `classic_medieval_battle` | 100v100 | Classic Medieval Battle (Agincourt style) |
| `cavalry_charge` | 150v150 | Offensive Wedge (Heavy Cavalry) |
| `defensive_siege` | 120v120 | Defensive Formation (Shield Wall) |
| `cannae_envelopment` | 180v180 | Hammer and Anvil (Hannibal's Tactics) |
| `roman_legion` | 100v100 | Testudo Formation (Roman Tactics) |
| `british_square` | 120v120 | Hollow Square (Anti-Cavalry) |

#### Example Usage

```bash
# Lanchester analysis with 3 unit types (use N >= 20 for visible results)
python battle.py plot DAFT Lanchester Lanchester "[Knight,Pikeman,Crossbowman]" "range(20,100,20)" -N 5

# Using ggplot2-style visualization
python battle.py plot DAFT GGPlotLanchester Lanchester "[Knight,Crossbowman]" "range(20,80,20)"

# Cavalry charge analysis
python battle.py plot DAFT CavalryCharge cavalry_charge "[Knight]" "range(50,200,50)" -N 5

# Full statistical analysis with hypothesis tests
python battle.py plot DAFT Lanchester Lanchester "[Knight,Crossbowman]" "range(20,100,20)" -N 10 --stats
```

#### Output

The command generates:

1. **PNG Plot** in `Reports/lanchester_analysis_YYYYMMDD_HHMMSS.png`
2. **Markdown Report** in `Reports/Lanchester_report_YYYYMMDD_HHMMSS.md`

For ggplot-style plotters, additional individual plots are saved:

- `Reports/lanchester_winner_casualties_*.png`
- `Reports/lanchester_win_rate_*.png`
- `Reports/lanchester_duration_*.png`
- `Reports/lanchester_casualties_comparison_*.png`

**With `--stats` flag, additional outputs:**

3. **Statistical Report** in `Reports/stats_report_YYYYMMDD_HHMMSS.md` containing:
   - Lanchester Law Analysis (R² values, best fit, theory validation)
   - Unit Type Comparisons (p-values, effect sizes, significance)
   - ANOVA results (if 3+ unit types)
   - Summary statistics DataFrame

4. **Advanced Visualizations:**
   - `Reports/correlation_heatmap_*.png`
   - `Reports/boxplot_*.png`
   - `Reports/grouped_barplot_*.png`
   - `Reports/mean_comparison_*.png`
   - `Reports/histogram_*.png`
   - `Reports/metric_heatmap_*.png`

#### Lanchester's Laws

- **Linear Law (Melee)**: In melee combat, casualties are proportional to N. The side with numerical advantage loses fewer soldiers proportionally.
- **Square Law (Ranged)**: In ranged combat, fighting effectiveness scales with N². A 2:1 numerical advantage results in ~4:1 combat effectiveness.

The Lanchester scenario pits N units against 2N units of the same type. The larger side (2N) should win every time, and what's interesting is to have a graph with two curves corresponding to unit types, with x=N and y=casualties sustained by winning side.
