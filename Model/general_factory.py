# -*- coding: utf-8 -*-
"""
@file general_factory.py
@brief Factory for creating AI Generals

@details
Centralizes general creation logic to avoid duplication across modules.
Supports all AI strategies: BRAINDEAD, DAFT, SOMEIQ, RPC.

Used by:
- Utils.eval (CLI entry point)
- Plotting.collector (for Lanchester analysis)
- Tournament.runner (for tournament matches)

Follows Factory Pattern and Single Responsibility Principle.
"""

from typing import List

from Model.generals import General
from Model.units import UnitType
from Model.strategies import (
    StrategieBrainDead,
    StrategieDAFT,
    StrategieCrossbowmanSomeIQ,
    StrategieKnightSomeIQ,
    StrategiePikemanSomeIQ,
    StrategieStartSomeIQ,
    StrategieSimpleAttackBestAvoidWorst,
    StrategieRandomIQ,
)


# =============================================================================
# AVAILABLE AI STRATEGIES
# =============================================================================

AVAILABLE_AIS = ['BRAINDEAD', 'DAFT', 'SOMEIQ', 'RPC', 'RANDOMIQ']


def get_available_ais() -> List[str]:
    """
    Get list of available AI names.
    
    @return: List of AI strategy names
    """
    return AVAILABLE_AIS.copy()


def create_general(name: str, unitsA, unitsB) -> General:
    """
    Create a general with the specified AI strategy.
    
    @param name: AI name (BRAINDEAD, DAFT, SOMEIQ, RPC)
    @param unitsA: Units controlled by this general (allied units)
    @param unitsB: Enemy units
    @return: Configured General instance
    @raises ValueError: If AI name is unknown
    
    Example:
        general_a = create_general("SOMEIQ", scenario.units_a, scenario.units_b)
        general_b = create_general("DAFT", scenario.units_b, scenario.units_a)
    """
    name_up = name.upper()
    
    if name_up == "BRAINDEAD":
        sT = {
            UnitType.CROSSBOWMAN: StrategieBrainDead(None),
            UnitType.KNIGHT: StrategieBrainDead(None),
            UnitType.PIKEMAN: StrategieBrainDead(None),
        }
        return General(unitsA=unitsA, unitsB=unitsB, sS=None, sT=sT, name=name_up)
    
    elif name_up == "DAFT":
        sT = {
            UnitType.CROSSBOWMAN: StrategieDAFT(None),
            UnitType.KNIGHT: StrategieDAFT(None),
            UnitType.PIKEMAN: StrategieDAFT(None),
        }
        return General(unitsA=unitsA, unitsB=unitsB, sS=None, sT=sT, name=name_up)
    
    elif name_up == "SOMEIQ":
        sT = {
            UnitType.CROSSBOWMAN: StrategieCrossbowmanSomeIQ(),
            UnitType.KNIGHT: StrategieKnightSomeIQ(),
            UnitType.PIKEMAN: StrategiePikemanSomeIQ(),
        }
        sS = StrategieStartSomeIQ()
        return General(unitsA=unitsA, unitsB=unitsB, sS=sS, sT=sT, name=name_up)
    
    elif name_up == "RPC":
        # Rock-Paper-Counter: each unit type targets its counter
        sT = {
            UnitType.CROSSBOWMAN: StrategieSimpleAttackBestAvoidWorst(
                favoriteTroup=UnitType.PIKEMAN, 
                hatedTroup=UnitType.KNIGHT
            ),
            UnitType.KNIGHT: StrategieSimpleAttackBestAvoidWorst(
                favoriteTroup=UnitType.CROSSBOWMAN, 
                hatedTroup=UnitType.PIKEMAN
            ),
            UnitType.PIKEMAN: StrategieSimpleAttackBestAvoidWorst(
                favoriteTroup=UnitType.KNIGHT, 
                hatedTroup=UnitType.CROSSBOWMAN
            ),
        }
        return General(unitsA=unitsA, unitsB=unitsB, sS=None, sT=sT, name=name_up)
    
    elif name_up == "RANDOMIQ":
        # Random strategy - applies random orders
        sS = StrategieRandomIQ()
        return General(unitsA=unitsA, unitsB=unitsB, sS=sS, sT=None, name=name_up)
    
    else:
        available = ', '.join(AVAILABLE_AIS)
        raise ValueError(f"Unknown AI: '{name}'. Available: {available}")
