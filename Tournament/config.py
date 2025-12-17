# -*- coding: utf-8 -*-
"""
@file config.py
@brief Tournament Configuration

@details
Defines configuration dataclass for tournament settings.
Follows Single Responsibility Principle - only handles configuration.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TournamentConfig:
    """Configuration for a tournament."""
    generals: List[str]
    scenarios: List[str]
    rounds_per_matchup: int = 10
    alternate_positions: bool = True
    max_ticks: int = 1000
    num_processes: Optional[int] = None # Number of processes for parallel execution, None for cpu_count()
