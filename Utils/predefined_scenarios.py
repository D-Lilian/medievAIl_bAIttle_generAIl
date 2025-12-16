# -*- coding: utf-8 -*-
"""
@file predefined_scenarios.py
@brief create predefined scenarios

@details
Collection of scenarios

"""

from Model.scenario import Scenario
from Utils.map_generator import MapGenerator

class PredefinedScenarios:

    @staticmethod
    def classic_medieval_battle() -> Scenario:
        """100v100 - Classic Medieval Battle (Agincourt style)"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=100,
            formation='classic',
            size_x=120,
            size_y=120
        )

    @staticmethod
    def defensive_siege() -> Scenario:
        """120v120 - Defensive Formation (Shield Wall)"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=120,
            formation='defensive',
            size_x=120,
            size_y=130
        )

    @staticmethod
    def cavalry_charge() -> Scenario:
        """150v150 - Offensive Wedge (Heavy Cavalry)"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=150,
            formation='offensive',
            size_x=120,
            size_y=120
        )

    @staticmethod
    def cannae_envelopment() -> Scenario:
        """180v180 - Hammer and Anvil (Hannibal's Tactics)"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=180,
            formation='hammer_anvil',
            size_x=120,
            size_y=120
        )

    @staticmethod
    def roman_legion() -> Scenario:
        """100v100 - Testudo Formation (Roman Tactics)"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=100,
            formation='testudo',
            size_x=120,
            size_y=120
        )

    @staticmethod
    def british_square() -> Scenario:
        """120v120 - Hollow Square (Anti-Cavalry)"""
        return MapGenerator.generate_battle_scenario(
            units_per_team=120,
            formation='hollow_square',
            size_x=120,
            size_y=120
        )
