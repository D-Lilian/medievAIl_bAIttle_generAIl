# -*- coding: utf-8 -*-
"""
@file __init__.py
@brief View package initialization.

@details
Exports the main TerminalView class and key data types.
"""

from View.terminal_view import TerminalView
from View.data_types import Team, UnitStatus, UnitRepr

__all__ = ['TerminalView', 'Team', 'UnitStatus', 'UnitRepr']
