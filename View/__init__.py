# -*- coding: utf-8 -*-
"""
@file __init__.py
@brief View module exports

@details
All view components are now in terminal_view.py following SOLID/KISS principles.
"""
from View.terminal_view import (
    TerminalView,
    ViewInterface,
    Team,
    UnitStatus,
    ColorPair,
    UnitRepr,
    Camera,
    ViewState,
    Stats,
    InputHandler,
    MapRenderer,
    UIRenderer,
    DebugRenderer,
    UnitCacheManager,
    resolve_letter,
    resolve_team,
    UNIT_LETTERS,
)

__all__ = [
    "TerminalView",
    "ViewInterface",
    "Team",
    "UnitStatus",
    "ColorPair",
    "UnitRepr",
    "Camera",
    "ViewState",
    "Stats",
    "InputHandler",
    "MapRenderer",
    "UIRenderer",
    "DebugRenderer",
    "UnitCacheManager",
    "resolve_letter",
    "resolve_team",
    "UNIT_LETTERS",
]
