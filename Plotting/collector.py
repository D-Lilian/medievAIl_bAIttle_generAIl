# -*- coding: utf-8 -*-
"""
@file       collector.py
@brief      Data Collector for Lanchester analysis simulations.

@details    Runs simulations in parallel and collects data into pandas DataFrames.

@par Workflow:
@code
    for unit_type in [Knight, Crossbow]:
        for N in range(1, 100):
            data[unit_type, N] = Lanchester(unit_type, N).run()
    PlotLanchester(data)
@endcode

@see LanchesterData for the output data container.
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

from Model.simulation import Simulation
from Model.general_factory import create_general

from Plotting.data import (
    LanchesterData, 
    BattleDataCollector,
)
from Plotting.lanchester import Lanchester


## @defgroup WorkerFunctions Multiprocessing Worker Functions
## @{

def _run_single_simulation(args: Tuple[str, str, int, int, int]) -> Dict[str, Any]:
    """
    @brief  Run a single Lanchester simulation (multiprocessing worker).
    @param  args Tuple of (ai_name, unit_type, n, run_id, repetition).
    @return Dict with battle results for DataFrame insertion.
    
    @details Creates N vs 2N battle (Lanchester format).
    """
    ai_name, unit_type, n, run_id, repetition = args
    
    try:
        # Create fresh scenario: N units (Team A) vs 2N units (Team B)
        scenario = Lanchester(unit_type, n)
        
        # Assign generals using centralized factory
        scenario.general_a = create_general(ai_name, scenario.units_a, scenario.units_b)
        scenario.general_b = create_general(ai_name, scenario.units_b, scenario.units_a)
        
        # Run simulation (fast mode for data collection)
        simulation = Simulation(scenario, tick_speed=100, paused=False, unlocked=True)
        output = simulation.simulate()
        
        # Collect results using BattleDataCollector
        result = BattleDataCollector.collect_from_scenario(scenario, output)
        
        # Determine winner casualties
        if result.winner == 'A':
            winner_casualties = result.team_a.casualties
        elif result.winner == 'B':
            winner_casualties = result.team_b.casualties
        else:
            winner_casualties = 0
        
        # Return only essential columns for DataFrame (optimized)
        return {
            'run_id': run_id,
            'unit_type': unit_type,
            'n_value': n,
            'team_a_casualties': result.team_a.casualties,
            'team_b_casualties': result.team_b.casualties,
            'winner': result.winner,
            'winner_casualties': winner_casualties,
            'duration_ticks': result.ticks,
        }
    except Exception:
        # Return error result for this simulation (will be filtered out)
        # This handles cases where N is too small for some strategies
        return {
            'run_id': run_id,
            'unit_type': unit_type,
            'n_value': n,
            'team_a_casualties': 0,
            'team_b_casualties': 0,
            'winner': 'error',
            'winner_casualties': 0,
            'duration_ticks': 0,
        }


def _run_symmetric_simulation(args: Tuple[str, str, int, int, int, bool]) -> Dict[str, Any]:
    """
    @brief  Run a single symmetric simulation (N vs N).
    @param  args Tuple of (ai_name, unit_type, n, run_id, repetition, symmetric).
    @return Dict with battle results for DataFrame insertion.
    
    @details Creates N vs N battle (symmetric format).
    """
    ai_name, unit_type, n, run_id, repetition, _ = args
    
    try:
        # Create symmetric scenario: N units vs N units
        from Plotting.lanchester import LanchesterSymmetric
        scenario = LanchesterSymmetric(unit_type, n)
        
        # Assign generals
        scenario.general_a = create_general(ai_name, scenario.units_a, scenario.units_b)
        scenario.general_b = create_general(ai_name, scenario.units_b, scenario.units_a)
        
        # Run simulation
        simulation = Simulation(scenario, tick_speed=100, paused=False, unlocked=True)
        output = simulation.simulate()
        
        result = BattleDataCollector.collect_from_scenario(scenario, output)
        
        if result.winner == 'A':
            winner_casualties = result.team_a.casualties
        elif result.winner == 'B':
            winner_casualties = result.team_b.casualties
        else:
            winner_casualties = 0
        
        return {
            'run_id': run_id,
            'unit_type': unit_type,
            'n_value': n,
            'team_a_casualties': result.team_a.casualties,
            'team_b_casualties': result.team_b.casualties,
            'winner': result.winner,
            'winner_casualties': winner_casualties,
            'duration_ticks': result.ticks,
        }
    except Exception:
        return {
            'run_id': run_id,
            'unit_type': unit_type,
            'n_value': n,
            'team_a_casualties': 0,
            'team_b_casualties': 0,
            'winner': 'error',
            'winner_casualties': 0,
            'duration_ticks': 0,
        }


## @}

## @class DataCollector
#  @brief Collects simulation data by running Lanchester scenarios.

class DataCollector:
    """
    @brief  Collects simulation data by running Lanchester scenarios.
    
    @details Produces pandas DataFrames for data analysis.
    
    @par Example:
    @code
        collector = DataCollector(ai_name='DAFT', num_repetitions=10)
        data = collector.collect_lanchester(
            unit_types=['Knight', 'Crossbow'],
            n_range=range(5, 50, 5)
        )
    @endcode
    """
    
    ## @var AVAILABLE_AIS
    #  @brief List of available AI strategies.
    AVAILABLE_AIS = ['BRAINDEAD', 'DAFT', 'SOMEIQ', 'RPC', 'RANDOMIQ']
    
    def __init__(self, ai_name: str = 'DAFT', num_repetitions: int = 10):
        """
        @brief  Initialize the data collector.
        @param  ai_name AI strategy name for both teams.
        @param  num_repetitions Number of repetitions per configuration.
        """
        self.ai_name = ai_name.upper()
        self.num_repetitions = num_repetitions
    
    def collect_lanchester(self, unit_types: List[str], 
                           n_range: range) -> LanchesterData:
        """
        @brief  Collect Lanchester analysis data into DataFrame.
        @param  unit_types List of unit type names (e.g., ['Knight', 'Crossbow']).
        @param  n_range Range of N values to test.
        @return LanchesterData object containing all simulation results.
        
        @details Creates Lanchester scenarios: Team A (N units) vs Team B (2N units).
        """
        # Initialize data container
        data = LanchesterData(
            ai_name=self.ai_name,
            scenario_name='Lanchester',
            unit_types=list(unit_types),
            n_range=list(n_range),
            num_repetitions=self.num_repetitions,
            timestamp=datetime.now().isoformat()
        )
        
        # Calculate total simulations
        total_configs = len(unit_types) * len(n_range)
        total_simulations = total_configs * self.num_repetitions
        
        # Prepare all simulation arguments
        all_args = []
        run_id = 0
        for unit_type in unit_types:
            for n in n_range:
                for rep in range(self.num_repetitions):
                    all_args.append((self.ai_name, unit_type, n, run_id, rep))
                    run_id += 1
        
        # Run simulations with multiprocessing
        results = self._run_parallel(all_args, total_simulations)
        
        # Filter out error results (from simulations that failed)
        valid_results = [r for r in results if r.get('winner') != 'error']
        error_count = len(results) - len(valid_results)
        if error_count > 0:
            print(f"  Warning: {error_count} simulations failed (N too small for AI)")
        
        # Add all valid results to DataFrame
        data.add_results(valid_results)
        
        # Print compact results
        self._print_results(data)
        
        return data
    
    def _run_parallel(self, all_args: List[Tuple], total: int) -> List[Dict[str, Any]]:
        """
        @brief  Run simulations in parallel using ProcessPoolExecutor.
        @param  all_args List of argument tuples for each simulation.
        @param  total Total number of simulations for progress reporting.
        @return List of result dictionaries.
        """
        import sys
        
        results = []
        completed = 0
        
        # Determine number of workers
        max_workers = min(mp.cpu_count(), 8)  # Cap at 8 for efficiency
        
        # Progress bar settings
        bar_width = 40
        
        def print_progress(done: int, total: int):
            """Print a single-line progress bar with \r."""
            pct = done / total if total > 0 else 1
            filled = int(bar_width * pct)
            bar = '█' * filled + '░' * (bar_width - filled)
            sys.stdout.write(f'\r[{bar}] {pct*100:.0f}%')
            sys.stdout.flush()
        
        print(f"Running {total} simulations...", end=' ')
        sys.stdout.write('\n')
        
        if len(all_args) >= 4 and max_workers > 1:
            # Parallel execution
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(_run_single_simulation, args): args 
                          for args in all_args}
                
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    completed += 1
                    print_progress(completed, total)
        else:
            # Sequential for small batches
            for args in all_args:
                result = _run_single_simulation(args)
                results.append(result)
                completed += 1
                print_progress(completed, total)
        
        # Final newline after progress bar
        print()  # Move to next line
        
        return results
    
    def _print_results(self, data: LanchesterData):
        """@brief Print compact results."""
        summary = data.get_full_summary()
        if summary.empty:
            return
        
        parts = []
        for _, row in summary.iterrows():
            unit = row['unit_type']
            win_rate = row['overall_team_b_win_rate'] * 100
            parts.append(f"{unit}: {win_rate:.0f}%")
        
        print(f"Done. {' | '.join(parts)}")

    def collect_symmetric(self, unit_types: List[str], 
                          n_range: range) -> LanchesterData:
        """
        @brief  Collect symmetric battle data (N vs N).
        @param  unit_types List of unit type names.
        @param  n_range Range of N values to test.
        @return LanchesterData object (reused for simplicity).
        
        @details Creates symmetric scenarios: Team A (N units) vs Team B (N units).
        """
        data = LanchesterData(
            ai_name=self.ai_name,
            scenario_name='Symmetric',
            unit_types=list(unit_types),
            n_range=list(n_range),
            num_repetitions=self.num_repetitions,
            timestamp=datetime.now().isoformat()
        )
        
        total_simulations = len(unit_types) * len(n_range) * self.num_repetitions
        
        # Prepare all simulation arguments
        all_args = []
        run_id = 0
        for unit_type in unit_types:
            for n in n_range:
                for rep in range(self.num_repetitions):
                    # Use N vs N (symmetric) instead of N vs 2N
                    all_args.append((self.ai_name, unit_type, n, run_id, rep, True))  # True = symmetric
                    run_id += 1
        
        # Run simulations with multiprocessing
        results = self._run_parallel_symmetric(all_args, total_simulations)
        
        valid_results = [r for r in results if r.get('winner') != 'error']
        error_count = len(results) - len(valid_results)
        if error_count > 0:
            print(f"  Warning: {error_count} simulations failed")
        
        data.add_results(valid_results)
        self._print_results_symmetric(data)
        
        return data

    def _run_parallel_symmetric(self, all_args: List[Tuple], total: int) -> List[Dict[str, Any]]:
        """@brief Run symmetric simulations in parallel."""
        import sys
        
        results = []
        completed = 0
        max_workers = min(mp.cpu_count(), 8)
        bar_width = 40
        
        def print_progress(done: int, total: int):
            pct = done / total if total > 0 else 1
            filled = int(bar_width * pct)
            bar = '█' * filled + '░' * (bar_width - filled)
            sys.stdout.write(f'\r[{bar}] {pct*100:.0f}%')
            sys.stdout.flush()
        
        print(f"Running {total} simulations...", end=' ')
        sys.stdout.write('\n')
        
        if len(all_args) >= 4 and max_workers > 1:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(_run_symmetric_simulation, args): args 
                          for args in all_args}
                
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    completed += 1
                    print_progress(completed, total)
        else:
            for args in all_args:
                result = _run_symmetric_simulation(args)
                results.append(result)
                completed += 1
                print_progress(completed, total)
        
        print()
        return results

    def _print_results_symmetric(self, data: LanchesterData):
        """@brief Print compact results for symmetric battles."""
        summary = data.get_full_summary()
        if summary.empty:
            return
        
        parts = []
        for _, row in summary.iterrows():
            unit = row['unit_type']
            # For symmetric, both teams should win ~50% of the time
            parts.append(f"{unit}: ~50%")
        
        print(f"Done. {' | '.join(parts)}")


## @defgroup CLIUtilities CLI Parsing Utilities
## @{

def parse_types_arg(types_str: str) -> List[str]:
    """
    @brief  Parse unit types argument from CLI.
    @param  types_str String like '[Knight,Crossbow]' or 'Knight,Crossbow'.
    @return List of normalized unit type names.
    
    @par Example:
        '[Knight,Crossbow]' -> ['Knight', 'Crossbow']
    """
    # Remove brackets if present
    types_str = types_str.strip('[]')
    
    # Split by comma
    types = [t.strip() for t in types_str.split(',')]
    
    # Normalize names
    name_map = {
        'knight': 'Knight',
        'crossbow': 'Crossbowman',
        'crossbowman': 'Crossbowman',
        'pikeman': 'Pikeman',
        'pike': 'Pikeman',
        'melee': 'Knight',
        'ranged': 'Crossbowman',
        'archer': 'Crossbowman',
    }
    
    normalized = []
    for t in types:
        lower = t.lower()
        normalized.append(name_map.get(lower, t))
    
    return normalized


def parse_range_arg(range_str: str) -> range:
    """
    @brief  Parse range argument from CLI.
    @param  range_str String like 'range(1,100)' or '1-100' or '1:100:5'.
    @return Python range object.
    
    @par Example:
        'range(1,100,5)' -> range(1, 100, 5)
    """
    range_str = range_str.strip()
    
    # Handle range(min,max) or range(min,max,step)
    if range_str.startswith('range(') and range_str.endswith(')'):
        inner = range_str[6:-1]
        parts = [int(p.strip()) for p in inner.split(',')]
        if len(parts) == 2:
            return range(parts[0], parts[1])
        elif len(parts) == 3:
            return range(parts[0], parts[1], parts[2])
        elif len(parts) == 1:
            return range(1, parts[0])
    
    # Handle min-max format
    if '-' in range_str and not range_str.startswith('-'):
        parts = range_str.split('-')
        if len(parts) == 2:
            return range(int(parts[0]), int(parts[1]) + 1)
    
    # Handle min:max:step format
    if ':' in range_str:
        parts = range_str.split(':')
        if len(parts) == 2:
            return range(int(parts[0]), int(parts[1]))
        elif len(parts) == 3:
            return range(int(parts[0]), int(parts[1]), int(parts[2]))
    
    # Default fallback
    return range(5, 51, 5)

## @}