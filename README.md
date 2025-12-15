# MedievAIl_bAIttle_generAIl

## Description

TODO

### Available Generals

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

The Terminal View is an interactive, real-time visualization of medieval battles using a curses-based terminal interface. It provides complete control over simulation playback, camera positioning, and detailed battle analysis through both terminal UI and generated HTML reports.

#### Architecture

Built following SOLID principles with a clean MVC separation of concerns:

**View Layer** (`View/terminal_view.py`):

- **TerminalView**: Main view class coordinating all rendering components and report generation
- **InputHandler**: Processes keyboard input with configurable callbacks for actions
- **MapRenderer**: Renders the battlefield grid with units positioned using team-based coloring
- **UIRenderer**: Displays informational panels (statistics, controls, simulation state) and pause overlay
- **DebugRenderer**: Shows detailed unit debugging information overlay
- **UnitCacheManager**: Manages unit data extraction, caching, and conversion to view representations with wall-clock time tracking
- **ViewState**: Centralized state management for pause, zoom, panels, and tick speed
- **Camera**: Handles viewport positioning, zoom levels, and auto-follow mode

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

- **Quick Save (F11)**: Saves scenario state to timestamped `.pkl` files in `save/` directory
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
| **F11** | Quick Save | Save current game state to timestamped file |
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
- Function key support (F1-F12) for panel toggles and actions

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

Executes a series of matches between multiple AIs and scenarios.

| Argument | Description |
| :--- | :--- |
| `-G / --ais` | **List** of participating AI names (required). |
| `-S / --scenarios` | **List** of scenarios to play (required). |
| `-N` | Number of rounds for each confrontation (Default: 10). |
| `-na / --no-alternate` | Disables alternation of player positions (AI1 vs AI2) for each round. |

### 4\. `plot`: Simulate and plot results

Generates a graph by varying a specific parameter of a scenario.

| Argument | Description |
| :--- | :--- |
| `<ai>` | Name of the AI to use for simulation. |
| `<plotter>` | Name of the plotting function to execute. |
| `<scenario_params>` | **Two arguments**: `ScenarioName` and the `Parameter` to vary (ex: `Lanchester N`). |
| `<range_params>` | **List of values** for the parameter range (ex: `1 100 1` for `range(1, 100)`). |
| `-N` | Number of repetitions for each parameter value (Default: 10). |
