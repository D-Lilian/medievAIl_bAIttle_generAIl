# -*- coding: utf-8 -*-
"""
@file predefined_scenarios.py
@brief Predefined battle scenarios

@details
Collection of historically-inspired battle scenarios designed to test
different AI strategies and tactical approaches.

Each scenario varies in:
- Army size (100-200 units per team)
- Unit composition (Knights, Pikemen, Crossbowmen ratios)
- Initial formation (affects early battle dynamics)

All scenarios use symmetric armies (mirrored) for fair AI evaluation.
"""

from Model.scenario import Scenario
from Utils.map_generator import MapGenerator


class PredefinedScenarios:
    """
    Factory for predefined battle scenarios.
    
    Scenarios are designed to highlight different tactical challenges:
    - Balanced: Tests overall AI competence
    - Ranged-heavy: Tests positioning and focus-fire
    - Melee-heavy: Tests micro-management and flanking
    - Asymmetric compositions: Tests adaptation to enemy composition
    """

    # =========================================================================
    # BALANCED SCENARIOS (Mixed unit compositions)
    # =========================================================================

    @staticmethod
    def classic() -> Scenario:
        """
        100v100 - Classic Medieval Battle
        
        Balanced composition inspired by Agincourt:
        - 40% Pikemen (front line, hold the line)
        - 30% Knights (shock troops, flanking)
        - 30% Crossbowmen (ranged support)
        
        Tests: General tactical competence, formation holding
        """
        return MapGenerator.generate_battle_scenario(
            units_per_team=100,
            formation='classic',
            size_x=120,
            size_y=120
        )

    @staticmethod
    def large_battle() -> Scenario:
        """
        200v200 - Large Scale Engagement
        
        Same balanced composition but with more units.
        Tests AI scalability and performance under load.
        
        Tests: Scalability, group management, performance
        """
        return MapGenerator.generate_battle_scenario(
            units_per_team=200,
            formation='classic',
            size_x=120,
            size_y=120
        )

    # =========================================================================
    # DEFENSIVE SCENARIOS (Favor defensive play)
    # =========================================================================

    @staticmethod
    def shield_wall() -> Scenario:
        """
        120v120 - Shield Wall Defense
        
        Heavy infantry focus:
        - 50% Pikemen (dense front line)
        - 25% Knights (counter-charge reserve)
        - 25% Crossbowmen (harassment)
        
        Tests: Breaking through defensive formations, patience
        """
        return MapGenerator.generate_battle_scenario(
            units_per_team=120,
            formation='defensive',
            size_x=120,
            size_y=120
        )

    @staticmethod
    def fortress() -> Scenario:
        """
        150v150 - Hollow Square (Anti-Cavalry)
        
        Defensive box formation:
        - 50% Pikemen (outer perimeter)
        - 20% Knights (mobile reserve)
        - 30% Crossbowmen (protected in center)
        
        Tests: Surrounding tactics, focus fire coordination
        """
        return MapGenerator.generate_battle_scenario(
            units_per_team=150,
            formation='hollow_square',
            size_x=120,
            size_y=120
        )

    # =========================================================================
    # OFFENSIVE SCENARIOS (Favor aggressive play)
    # =========================================================================

    @staticmethod
    def cavalry_charge() -> Scenario:
        """
        100v100 - Heavy Cavalry Assault
        
        Cavalry-heavy composition:
        - 40% Knights (front line shock)
        - 30% Pikemen (follow-up)
        - 30% Crossbowmen (covering fire)
        
        Tests: Aggressive tactics, timing of charges
        """
        return MapGenerator.generate_battle_scenario(
            units_per_team=100,
            formation='offensive',
            size_x=120,
            size_y=120
        )

    @staticmethod
    def blitzkrieg() -> Scenario:
        """
        120v120 - Fast Assault
        
        Mobile army designed for quick engagements:
        - 50% Knights (maximum mobility)
        - 30% Crossbowmen (ranged pressure)
        - 20% Pikemen (minimal holding force)
        
        Tests: Speed, target prioritization, hit-and-run
        """
        return MapGenerator.generate_battle_scenario(
            units_per_team=120,
            formation='offensive',
            size_x=120,
            size_y=120
        )

    # =========================================================================
    # TACTICAL SCENARIOS (Complex formations)
    # =========================================================================

    @staticmethod
    def cannae() -> Scenario:
        """
        150v150 - Hammer and Anvil (Hannibal's Tactics)
        
        Envelopment formation:
        - Center (Anvil): 40% Pikemen to hold
        - Flanks (Hammer): 30% Knights to encircle
        - Rear: 30% Crossbowmen for ranged support
        
        Tests: Flanking maneuvers, pincer movements, coordination
        """
        return MapGenerator.generate_battle_scenario(
            units_per_team=150,
            formation='hammer_anvil',
            size_x=120,
            size_y=120
        )

    @staticmethod
    def testudo() -> Scenario:
        """
        100v100 - Testudo Formation (Roman Tactics)
        
        Ultra-compact defensive formation:
        - 60% Pikemen (dense shell)
        - 20% Knights (protected strike force)
        - 20% Crossbowmen (minimal ranged)
        
        Tests: Breaking tight formations, area damage
        """
        return MapGenerator.generate_battle_scenario(
            units_per_team=100,
            formation='testudo',
            size_x=120,
            size_y=120
        )

    # =========================================================================
    # SCENARIO REGISTRY (for CLI and tournament use)
    # =========================================================================

    @staticmethod
    def get_all_scenarios() -> dict:
        """Return a dictionary of all available scenarios."""
        return {
            'classic': PredefinedScenarios.classic,
            'large_battle': PredefinedScenarios.large_battle,
            'shield_wall': PredefinedScenarios.shield_wall,
            'fortress': PredefinedScenarios.fortress,
            'cavalry_charge': PredefinedScenarios.cavalry_charge,
            'blitzkrieg': PredefinedScenarios.blitzkrieg,
            'cannae': PredefinedScenarios.cannae,
            'testudo': PredefinedScenarios.testudo,
        }

    @staticmethod
    def get_scenario(name: str) -> Scenario:
        """
        Get a scenario by name.
        
        @param name: Scenario name (case-insensitive)
        @return: Scenario instance
        @raises ValueError: If scenario not found
        """
        scenarios = PredefinedScenarios.get_all_scenarios()
        name_lower = name.lower().replace('_', '').replace('-', '')
        
        for key, factory in scenarios.items():
            if key.lower().replace('_', '') == name_lower:
                return factory()
        
        available = list(scenarios.keys())
        raise ValueError(f"Unknown scenario '{name}'. Available: {available}")

    @staticmethod
    def list_scenarios() -> list:
        """Return list of available scenario names."""
        return list(PredefinedScenarios.get_all_scenarios().keys())

