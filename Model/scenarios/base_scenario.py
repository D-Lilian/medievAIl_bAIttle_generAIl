# -*- coding: utf-8 -*-
"""
@file base_scenario.py
@brief Base Scenario - Abstract class for programmable scenarios

@details
Defines the BaseScenario abstract class and BattleResult dataclass.
All programmable scenarios should inherit from BaseScenario.

"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Model.scenario import Scenario
from Model.simulation import Simulation
from Model.units import Unit


@dataclass
class BattleResult:
    """
    @brief Data class to store battle simulation results
    
    @details Holds all relevant statistics from a completed battle,
    including casualties, remaining units, and damage dealt.
    """
    # Configuration
    scenario_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Team A Results
    team_a_initial: int = 0
    team_a_remaining: int = 0
    team_a_casualties: int = 0
    team_a_total_hp_initial: int = 0
    team_a_total_hp_remaining: int = 0
    team_a_damage_dealt: int = 0
    
    # Team B Results
    team_b_initial: int = 0
    team_b_remaining: int = 0
    team_b_casualties: int = 0
    team_b_total_hp_initial: int = 0
    team_b_total_hp_remaining: int = 0
    team_b_damage_dealt: int = 0
    
    # Simulation metadata
    ticks: int = 0
    winner: str = ""  # "A", "B", or "draw"
    
    @property
    def team_a_casualty_rate(self) -> float:
        """Casualty rate for Team A (0.0 - 1.0)"""
        return self.team_a_casualties / self.team_a_initial if self.team_a_initial > 0 else 0.0
    
    @property
    def team_b_casualty_rate(self) -> float:
        """Casualty rate for Team B (0.0 - 1.0)"""
        return self.team_b_casualties / self.team_b_initial if self.team_b_initial > 0 else 0.0
    
    @property
    def team_a_hp_loss_rate(self) -> float:
        """HP loss rate for Team A (0.0 - 1.0)"""
        return 1 - (self.team_a_total_hp_remaining / self.team_a_total_hp_initial) if self.team_a_total_hp_initial > 0 else 0.0
    
    @property
    def team_b_hp_loss_rate(self) -> float:
        """HP loss rate for Team B (0.0 - 1.0)"""
        return 1 - (self.team_b_total_hp_remaining / self.team_b_total_hp_initial) if self.team_b_total_hp_initial > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization"""
        return {
            'scenario_name': self.scenario_name,
            'parameters': self.parameters,
            'team_a': {
                'initial': self.team_a_initial,
                'remaining': self.team_a_remaining,
                'casualties': self.team_a_casualties,
                'casualty_rate': self.team_a_casualty_rate,
                'hp_initial': self.team_a_total_hp_initial,
                'hp_remaining': self.team_a_total_hp_remaining,
                'hp_loss_rate': self.team_a_hp_loss_rate,
                'damage_dealt': self.team_a_damage_dealt,
            },
            'team_b': {
                'initial': self.team_b_initial,
                'remaining': self.team_b_remaining,
                'casualties': self.team_b_casualties,
                'casualty_rate': self.team_b_casualty_rate,
                'hp_initial': self.team_b_total_hp_initial,
                'hp_remaining': self.team_b_total_hp_remaining,
                'hp_loss_rate': self.team_b_hp_loss_rate,
                'damage_dealt': self.team_b_damage_dealt,
            },
            'ticks': self.ticks,
            'winner': self.winner,
        }


class BaseScenario(ABC):
    """
    @brief Abstract base class for programmable scenarios
    
    @details Defines the interface for all programmable scenarios.
    Subclasses must implement setup() to place units on the grid.
    """
    
    def __init__(self, size_x: int = 120, size_y: int = 120):
        """
        @brief Initialize the scenario
        
        @param size_x Map width
        @param size_y Map height
        """
        self.size_x = size_x
        self.size_y = size_y
        self.units: List[Unit] = []
        self.units_a: List[Unit] = []
        self.units_b: List[Unit] = []
        self.general_a = None
        self.general_b = None
        self._scenario: Scenario = None
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this scenario"""
        pass
    
    @abstractmethod
    def setup(self, **kwargs) -> 'BaseScenario':
        """
        @brief Set up the scenario with the given parameters
        
        @param kwargs Scenario-specific parameters
        @return self for method chaining
        """
        pass
    
    def build(self) -> Scenario:
        """
        @brief Build and return the Scenario object
        
        @return Scenario instance ready for simulation
        """
        self._scenario = Scenario(
            units=self.units,
            units_a=self.units_a,
            units_b=self.units_b,
            general_a=self.general_a,
            general_b=self.general_b,
            size_x=self.size_x,
            size_y=self.size_y
        )
        return self._scenario
    
    def run(self, tick_speed: int = 100, unlocked: bool = True) -> BattleResult:
        """
        @brief Run the scenario and return results
        
        @param tick_speed Simulation speed (ticks per second)
        @param unlocked If True, run as fast as possible
        @return BattleResult with simulation statistics
        """
        if self._scenario is None:
            self.build()
        
        # Store initial state
        initial_a = len(self.units_a)
        initial_b = len(self.units_b)
        initial_hp_a = sum(u.hp for u in self.units_a)
        initial_hp_b = sum(u.hp for u in self.units_b)
        
        # Run simulation
        sim = Simulation(
            self._scenario,
            tick_speed=tick_speed,
            paused=False,
            unlocked=unlocked
        )
        sim_result = sim.simulate()
        
        # Collect results
        remaining_a = sum(1 for u in self.units_a if u.hp > 0)
        remaining_b = sum(1 for u in self.units_b if u.hp > 0)
        remaining_hp_a = sum(max(0, u.hp) for u in self.units_a)
        remaining_hp_b = sum(max(0, u.hp) for u in self.units_b)
        damage_dealt_a = sum(getattr(u, 'damage_dealt', 0) for u in self.units_a)
        damage_dealt_b = sum(getattr(u, 'damage_dealt', 0) for u in self.units_b)
        
        # Determine winner
        if remaining_a == 0 and remaining_b == 0:
            winner = "draw"
        elif remaining_a == 0:
            winner = "B"
        elif remaining_b == 0:
            winner = "A"
        else:
            winner = "A" if remaining_a > remaining_b else "B"
        
        return BattleResult(
            scenario_name=self.name,
            parameters=self._get_parameters(),
            team_a_initial=initial_a,
            team_a_remaining=remaining_a,
            team_a_casualties=initial_a - remaining_a,
            team_a_total_hp_initial=initial_hp_a,
            team_a_total_hp_remaining=remaining_hp_a,
            team_a_damage_dealt=damage_dealt_a,
            team_b_initial=initial_b,
            team_b_remaining=remaining_b,
            team_b_casualties=initial_b - remaining_b,
            team_b_total_hp_initial=initial_hp_b,
            team_b_total_hp_remaining=remaining_hp_b,
            team_b_damage_dealt=damage_dealt_b,
            ticks=sim_result.get('ticks', 0),
            winner=winner
        )
    
    def _get_parameters(self) -> Dict[str, Any]:
        """
        @brief Get scenario parameters for result tracking
        
        @return Dictionary of parameters (override in subclasses)
        """
        return {}
    
    def reset(self) -> 'BaseScenario':
        """
        @brief Reset the scenario for another run
        
        @return self for method chaining
        """
        self.units = []
        self.units_a = []
        self.units_b = []
        self._scenario = None
        return self


class MockGeneral:
    """
    @brief Minimal general implementation for scenarios without AI
    
    @details A do-nothing general for testing pure combat mechanics
    without strategy interference.
    """
    def BeginStrategy(self):
        pass
    
    def CreateOrders(self):
        pass
    
    def notify(self, unit_type):
        pass
    
    def HandleUnitTypeDepleted(self, unit_type):
        pass
