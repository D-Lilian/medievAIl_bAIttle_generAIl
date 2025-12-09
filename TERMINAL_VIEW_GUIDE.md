# Terminal View Guide

## Overview
The Terminal View provides an interactive curses-based interface to visualize medieval battle simulations in real-time.

## Quick Start

### Using TerminalViewController (Recommended)

The easiest way to use the terminal view is through the `TerminalViewController`:

```python
from Controller.TerminalViewController import TerminalViewController
from Model.Scenario import Scenario
from Model.Units import Knight, Pikeman, Team
from Model.generals import General
from Model.strategies import StrategyStart, StrategieDAFT

# Create units
units = []
units_a = []
units_b = []

# Team A
for i in range(5):
    u = Knight(Team.A, 20, 20 + i*5)
    units.append(u)
    units_a.append(u)

# Team B
for i in range(5):
    u = Pikeman(Team.B, 100, 20 + i*5)
    units.append(u)
    units_b.append(u)

# Create generals
gen_a = General(units_a, units_b, StrategyStart(), StrategieDAFT(None))
gen_b = General(units_b, units_a, StrategyStart(), StrategieDAFT(None))

# Create scenario
scenario = Scenario(
    units=units,
    units_a=units_a,
    units_b=units_b,
    general_a=gen_a,
    general_b=gen_b,
    size_x=120,
    size_y=120
)

# Run interactive view
controller = TerminalViewController(scenario, board_width=120, board_height=120, tick_speed=10)
controller.run_interactive()
```

### Convenience Function

For even simpler usage:

```python
from Controller.TerminalViewController import run_battle_with_terminal_view

# ... create scenario as above ...

run_battle_with_terminal_view(scenario, 120, 120, tick_speed=10)
```

### Headless Mode

To run a simulation without the interactive view:

```python
controller = TerminalViewController(scenario, 120, 120)
final_state = controller.run_headless(max_ticks=1000)
```

## Controls

- **Arrow Keys**: Move camera
- **+/-**: Zoom in/out
- **Space**: Pause/Resume
- **TAB**: Pause simulation
- **s**: Search for units
- **r**: Generate HTML report
- **q**: Quit

## Features

- Real-time battlefield visualization
- Camera movement and zoom
- Unit search
- Interactive HTML reports with:
  - Battle statistics
  - Timeline visualization
  - Interactive unit movement maps
  - Collapsible sections
- 90-degree rotated view for better readability

## Command Line Usage

Run simulations from the command line:

```bash
python Controller/main_controller.py run scenario1 daft braindead -t 10
```

Options:
- `scenario1`: Scenario name (currently uses default)
- `daft`, `braindead`, `someiq`: AI strategies for teams A and B
- `-t 10`: Tick speed (frames per second)

## Architecture

- **TerminalViewController**: High-level interface for running simulations
- **TerminalView**: Low-level curses UI implementation
- **Scenario**: Encapsulates units, generals, and battlefield configuration
- **Simulation**: Core simulation engine

## Testing

Run tests:
```bash
python -m unittest Tests.terminal_view_tests -v
python -m unittest Tests.controller_tests -v
```
