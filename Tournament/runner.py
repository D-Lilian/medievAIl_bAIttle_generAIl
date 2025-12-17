# -*- coding: utf-8 -*-
"""
@file runner.py
@brief Parallel Tournament Runner

@details
Orchestrates running a complete tournament between AI generals in parallel
using multiprocessing to significantly speed up execution.
"""

import multiprocessing
from itertools import product
from typing import List, Tuple, Dict, Any

from Controller.simulation_controller import SimulationController
from Model.general_factory import create_general
from Model.units import UnitType
from Utils.predefined_scenarios import PredefinedScenarios

from Tournament.config import TournamentConfig
from Tournament.results import MatchResult, TournamentResults

# --- Worker Functions for Multiprocessing ---

# Available scenarios mapped to their factory functions
# Uses the centralized registry from PredefinedScenarios
SCENARIO_MAP = PredefinedScenarios.get_all_scenarios()


def _create_general_static(name: str, units_a: List, units_b: List):
    """
    Create a general with the specified AI strategy using centralized factory.
    
    @param name: General/AI name (BRAINDEAD, DAFT, SOMEIQ, RPC)
    @param units_a: Units for team A
    @param units_b: Units for team B
    @return: Configured General instance
    """
    return create_general(name, units_a, units_b)

def _run_match_worker(args: Tuple[str, str, str, bool]) -> MatchResult:
    """
    Worker function to run a single match. Designed to be run in a separate process.
    """
    general_a_name, general_b_name, scenario_name, swap_result = args
    
    # Create fresh instances for this process
    simulation_controller = SimulationController()
    scenario = SCENARIO_MAP[scenario_name]()
    
    # Create generals
    general_a = _create_general_static(general_a_name, scenario.units_a, scenario.units_b)
    general_b = _create_general_static(general_b_name, scenario.units_b, scenario.units_a)
    
    scenario.general_a = general_a
    scenario.general_b = general_b
    
    # Store initial counts
    initial_a = len(scenario.units_a)
    initial_b = len(scenario.units_b)
    
    # Run simulation
    simulation_controller.initialize_simulation(scenario, unlocked=True)
    output = simulation_controller.simulation.simulate()
    
    # Collect results
    ticks = output.get('ticks', 0)
    survivors_a = sum(1 for u in scenario.units_a if u.hp > 0)
    survivors_b = sum(1 for u in scenario.units_b if u.hp > 0)
    
    # Determine winner
    is_draw = False
    if survivors_a > 0 and survivors_b == 0:
        winner = 'A'
    elif survivors_b > 0 and survivors_a == 0:
        winner = 'B'
    else:
        winner = None
        is_draw = True
    
    # Handle position swap for alternation
    if swap_result:
        result_general_a, result_general_b = general_b_name, general_a_name
        winner = {'A': 'B', 'B': 'A'}.get(winner) # Swap winner perspective
    else:
        result_general_a, result_general_b = general_a_name, general_b_name
    
    return MatchResult(
        general_a=result_general_a,
        general_b=result_general_b,
        scenario_name=scenario_name,
        winner=winner,
        ticks=ticks,
        # Stats are from the perspective of the final result names
        team_a_survivors=survivors_a if not swap_result else survivors_b,
        team_b_survivors=survivors_b if not swap_result else survivors_a,
        team_a_casualties=initial_a - survivors_a if not swap_result else initial_b - survivors_b,
        team_b_casualties=initial_b - survivors_b if not swap_result else initial_a - survivors_a,
        is_draw=is_draw
    )

# --- Main Tournament Runner Class ---

class TournamentRunner:
    """
    Orchestrates running a complete tournament between AI generals in parallel.
    """
    
    AVAILABLE_GENERALS = ['BRAINDEAD', 'DAFT', 'SOMEIQ', 'RPC']
    SCENARIO_MAP = SCENARIO_MAP  # Expose module-level map as class attribute
    
    def __init__(self, config: TournamentConfig):
        """Initialize tournament runner."""
        self.config = config
        self.results = TournamentResults(config=config)
    
    def run(self) -> TournamentResults:
        """
        Run the complete tournament in parallel.
        """
        # --- 1. Prepare all match jobs ---
        jobs = self._prepare_jobs()
        total_matches = len(jobs)
        
        self._print_header(total_matches)
        
        # --- 2. Run jobs in parallel ---
        # Use a sensible number of processes, defaulting to os.cpu_count()
        num_processes = self.config.num_processes or multiprocessing.cpu_count()
        
        print(f"Running {total_matches} matches in parallel on {num_processes} processes...")
        
        all_results = []
        with multiprocessing.Pool(processes=num_processes) as pool:
            # Using imap_unordered to get results as they complete for progress tracking
            for i, result in enumerate(pool.imap_unordered(_run_match_worker, jobs), 1):
                all_results.append(result)
                print(f"\r  Progress: {i}/{total_matches} matches completed ({i/total_matches:.1%})", end='', flush=True)

        print("\n\nAll matches finished. Aggregating results...")
        
        # --- 3. Process results ---
        for result in all_results:
            self.results.add_match(result)
        
        self._print_footer(total_matches)
        
        return self.results
        
    def _prepare_jobs(self) -> List[Tuple[str, str, str, bool]]:
        """Create a list of all match arguments to be run."""
        jobs = []
        # Create all combinations of generals and scenarios
        matchup_product = product(
            self.config.scenarios,
            self.config.generals,
            self.config.generals
        )
        
        for scenario_name, general_a_name, general_b_name in matchup_product:
            if scenario_name not in SCENARIO_MAP:
                print(f"WARNING: Unknown scenario '{scenario_name}', skipping")
                continue
            
            for round_num in range(self.config.rounds_per_matchup):
                # Alternate positions every other round if configured
                swap = self.config.alternate_positions and round_num % 2 == 1
                if swap:
                    # Run B vs A, but the result will be swapped back
                    job = (general_b_name, general_a_name, scenario_name, True)
                else:
                    job = (general_a_name, general_b_name, scenario_name, False)
                jobs.append(job)
        return jobs

    def _print_header(self, total_matches: int):
        """Prints the tournament start banner."""
        print(f"\n{'='*60}")
        print("PARALLEL TOURNAMENT START")
        print(f"{'='*60}")
        print(f"Generals: {self.config.generals}")
        print(f"Scenarios: {self.config.scenarios}")
        print(f"Rounds per matchup: {self.config.rounds_per_matchup}")
        print(f"Alternate positions: {self.config.alternate_positions}")
        print(f"Total matches to run: {total_matches}")
        print(f"{'='*60}\n")
        
    def _print_footer(self, total_matches: int):
        """Prints the tournament end banner."""
        print(f"\n{'='*60}")
        print(f"TOURNAMENT COMPLETE - {total_matches} matches played")
        print(f"{'='*60}\n")
