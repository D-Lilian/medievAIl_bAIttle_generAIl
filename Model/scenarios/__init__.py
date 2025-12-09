# -*- coding: utf-8 -*-
"""
@file __init__.py
@brief Scenarios module - Programmable battle scenarios

@details
Contains base scenario classes and specific scenario implementations
for testing combat mechanics and Lanchester's Laws.
"""
from Model.scenarios.base_scenario import BaseScenario, BattleResult
from Model.scenarios.lanchester_scenario import LanchesterScenario
