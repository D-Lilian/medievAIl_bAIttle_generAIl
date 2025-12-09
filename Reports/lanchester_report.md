# Lanchester's Laws Analysis Report

## Background

**Lanchester's Laws** describe the relationship between army size and casualties:

- **Linear Law (Melee)**: In melee combat, casualties are proportional to the ratio of forces.
- **Square Law (Ranged)**: In ranged combat, effectiveness scales with the square of the number of units.

This experiment pits N units against 2N units to observe these relationships.

## Results Visualization

![Lanchester Plot](lanchester_report_plot.png)

## Summary by Unit Type

| Unit Type | N Range | Avg Casualties (min-max N) | Trend |
|-----------|---------|---------------------------|-------|
| Knight | 5-25 | 0.0 - 0.5 | Linear (Linear Law) |
| Crossbowman | 5-25 | 0.0 - 2.0 | Linear (Linear Law) |

## Analysis

### Knight

Expected behavior: **Linear Law** (melee combat)
- Casualties should scale approximately linearly with N
- The larger army's advantage is proportional to the size difference

### Crossbowman

Expected behavior: **Square Law** (ranged combat)
- Casualties should scale approximately with N²
- Concentration of fire amplifies the larger army's advantage


## Raw Data (Sample)

| Scenario | N | A Init | A Rem | B Init | B Rem | Winner | Ticks |
|----------|---|--------|-------|--------|-------|--------|-------|
| Lanchester(Knight, 5) | 5 | 5 | 0 | 10 | 10 | B | 66 |
| Lanchester(Knight, 5) | 5 | 5 | 0 | 10 | 10 | B | 66 |
| Lanchester(Knight, 10) | 10 | 10 | 0 | 20 | 20 | B | 65 |
| Lanchester(Knight, 10) | 10 | 10 | 0 | 20 | 20 | B | 66 |
| Lanchester(Knight, 15) | 15 | 15 | 0 | 30 | 29 | B | 71 |
| Lanchester(Knight, 15) | 15 | 15 | 0 | 30 | 30 | B | 71 |
| Lanchester(Knight, 20) | 20 | 20 | 0 | 40 | 39 | B | 72 |
| Lanchester(Knight, 20) | 20 | 20 | 0 | 40 | 40 | B | 70 |
| Lanchester(Knight, 25) | 25 | 25 | 0 | 50 | 50 | B | 74 |
| Lanchester(Knight, 25) | 25 | 25 | 0 | 50 | 49 | B | 74 |
| Lanchester(Crossbowman, 5) | 5 | 5 | 0 | 10 | 10 | B | 47 |
| Lanchester(Crossbowman, 5) | 5 | 5 | 0 | 10 | 10 | B | 47 |
| Lanchester(Crossbowman, 10) | 10 | 10 | 0 | 20 | 20 | B | 49 |
| Lanchester(Crossbowman, 10) | 10 | 10 | 0 | 20 | 20 | B | 48 |
| Lanchester(Crossbowman, 15) | 15 | 15 | 0 | 30 | 30 | B | 55 |
| Lanchester(Crossbowman, 15) | 15 | 15 | 0 | 30 | 29 | B | 52 |
| Lanchester(Crossbowman, 20) | 20 | 20 | 0 | 40 | 40 | B | 58 |
| Lanchester(Crossbowman, 20) | 20 | 20 | 0 | 40 | 40 | B | 57 |
| Lanchester(Crossbowman, 25) | 25 | 25 | 0 | 50 | 49 | B | 60 |
| Lanchester(Crossbowman, 25) | 25 | 25 | 0 | 50 | 47 | B | 62 |
