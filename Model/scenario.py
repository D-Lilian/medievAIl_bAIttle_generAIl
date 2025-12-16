# -*- coding: utf-8 -*-
"""
@file scenario.py
@brief Scenario Definition - Setup for a battle

@details
Contains the Scenario class which holds the initial state of a battle,
including units, generals, and map size.

"""
class Scenario:

    def __init__(self, units, units_a, units_b, general_a, general_b, size_x=120, size_y=120):
        self.units = units

        self.units_a = units_a
        self.units_b = units_b

        self.general_a = general_a
        self.general_b = general_b

        self.size_x = max(size_x, 120)
        self.size_y = max(size_y, 120)

