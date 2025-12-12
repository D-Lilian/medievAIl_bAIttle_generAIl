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

#### Features

- **Zoom Control**: Zoom in/out with 'M' key (3 levels: 1x, 2x, 3x)
- **Camera Movement**: Move camera with ZQSD/WASD keys, fast movement with Shift+ZQSD
- **Auto Camera**: Toggle automatic camera following units with 'A' key
- **Simulation Control**: Pause/resume with 'P', adjust speed with +/- keys
- **Panel Management**: Toggle UI panels with F1-F4 keys
- **Save/Load**: Quick save with F11, quick load with F12 (placeholders)
- **Report Generation**: Generate HTML battle reports with Tab key
- **Debug Mode**: Toggle debug overlay with Ctrl+D
- **Exit**: Quit with ESC or Q

#### Controls Summary

| Key | Action |
|-----|--------|
| **P** | Pause/Resume simulation |
| **M** | Cycle zoom levels (1x → 2x → 3x) |
| **A** | Toggle auto-follow camera |
| **ZQSD/WASD** | Move camera |
| **Shift+ZQSD** | Fast camera movement |
| **+/-** | Increase/Decrease simulation speed |
| **F1** | Toggle unit counts panel |
| **F2** | Toggle unit types panel |
| **F3** | Toggle simulation info panel |
| **F4** | Toggle all UI panels |
| **F11** | Quick save (placeholder) |
| **F12** | Quick load (placeholder) |
| **Tab** | Generate HTML battle report |
| **Ctrl+D** | Toggle debug overlay |
| **ESC/Q** | Exit terminal view |

#### UI Panels

- **Unit Counts**: Shows current number of units per team
- **Unit Types**: Displays breakdown by unit type (Knight, Pikeman, etc.)
- **Simulation Info**: Displays tick count, FPS, and simulation status
- **Debug Overlay**: Shows detailed unit information for development

#### Auto Camera Mode

When enabled, the camera automatically centers on the barycenter (center of mass) of all alive units, providing a dynamic view that follows the action. Disable for manual camera control.

#### Performance

- Smooth 60 FPS rendering with double buffering
- Optimized unit rendering with caching
- Real-time FPS display in simulation info panel

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
