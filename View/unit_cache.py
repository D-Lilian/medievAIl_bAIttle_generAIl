# -*- coding: utf-8 -*-
"""
@file unit_cache.py
@brief Unit cache management for the terminal view.

@details
Manages unit data extraction from the simulation and caching.
Handles conversion from Model units to View UnitRepr.
Follows Single Responsibility Principle.
"""

import time
from typing import List, Dict, Optional

from Model.units import UnitType
from View.data_types import Team, UnitStatus, UnitRepr, resolve_letter, resolve_team
from View.stats import Stats


class UnitCacheManager:
    """
    @brief Manages unit data extraction and caching.
    """

    def __init__(self):
        """
        @brief Initialize cache manager.
        """
        self.units: List[UnitRepr] = []
        self._all_units: Dict[int, UnitRepr] = {}
        self._hp_memory: Dict[int, int] = {}
        self._target_memory: Dict[int, str] = {}
        # Wall-clock tracking for displayed simulation time
        self._wall_start: Optional[float] = None
        self._wall_accum: float = 0.0
        self._last_wall: Optional[float] = None
        self._last_paused: bool = False

    def update(self, simulation, stats: Stats) -> None:
        """
        @brief Update cache from simulation.
        @param simulation Simulation object
        @param stats Statistics to update
        """
        stats.reset()

        raw_units = self._get_units(simulation)
        current_ids = set()

        for unit in raw_units:
            if not hasattr(unit, 'hp'):
                continue

            uid = id(unit)
            current_ids.add(uid)
            repr_unit = self._create_repr(unit, uid, simulation)
            self._all_units[uid] = repr_unit

        # Mark missing as dead
        for uid, repr_unit in self._all_units.items():
            if uid not in current_ids:
                repr_unit.status = UnitStatus.DEAD
                repr_unit.hp = 0

        # Rebuild cache and stats
        self.units = list(self._all_units.values())
        for unit in self.units:
            stats.add_unit(unit)

        # Update time (wall-clock, pause-aware) to display stable elapsed time
        stats.simulation_time = self._get_time(simulation)

    def _get_units(self, simulation) -> list:
        """
        @brief Extract units from simulation.
        @param simulation Simulation object
        @return List of units
        """
        if hasattr(simulation, 'scenario') and hasattr(simulation.scenario, 'units'):
            return simulation.scenario.units
        if hasattr(simulation, 'units'):
            return simulation.units
        return []

    def _get_time(self, simulation) -> float:
        """
        @brief Get simulation time.
        @param simulation Simulation object
        @return Time in seconds
        """
        now = time.perf_counter()

        # Initialize clocks
        if self._wall_start is None:
            self._wall_start = now
            self._last_wall = now
            self._last_paused = getattr(simulation, 'paused', False)
            return 0.0

        paused = getattr(simulation, 'paused', False)

        # Accumulate wall-clock only when not paused
        if not paused:
            if self._last_wall is not None:
                self._wall_accum += max(0.0, now - self._last_wall)

        # Update last wall time regardless (so resume starts from here)
        self._last_wall = now
        self._last_paused = paused

        return self._wall_accum

    def _create_repr(self, unit, uid: int, simulation) -> UnitRepr:
        """
        @brief Create UnitRepr from model unit.
        @param unit Model unit object
        @param uid Unit ID
        @param simulation Simulation object for target inference
        @return Unit representation
        """
        hp = getattr(unit, 'hp', 0)
        hp_max = self._get_hp_max(unit, uid, hp)
        team = resolve_team(getattr(unit, 'team', getattr(unit, 'equipe', 1)))
        unit_type = getattr(unit, 'name', type(unit).__name__)

        # Resolve target strictly from orders: prefer order.current_target, then order.target
        target = None
        order_manager = getattr(unit, 'order_manager', None)

        if order_manager:
            for order in order_manager:
                if hasattr(order, 'current_target'):
                    candidate = getattr(order, 'current_target')
                    if candidate is not None:
                        target = candidate
                        break
            if target is None:
                for order in order_manager:
                    candidate = getattr(order, 'target', None)
                    if candidate is not None:
                        target = candidate
                        break
            
            # Fallback: infer target from order type if still None
            if target is None:
                for order in order_manager:
                    order_type = type(order).__name__
                    
                    # AttackOnSightOrder / AttackNearestTroupOmniscient
                    if order_type in ('AttackOnSightOrder', 'AttackNearestTroupOmniscient'):
                        type_target = getattr(order, 'typeTarget', UnitType.ALL)
                        if order_type == 'AttackOnSightOrder':
                            target = simulation.get_nearest_enemy_in_sight(unit, type_target=type_target)
                        else:
                            target = simulation.get_nearest_enemy_unit(unit, type_target=type_target)
                        if target:
                            break
                    
                    # AttackOnReachOrder
                    elif order_type == 'AttackOnReachOrder':
                        type_target = getattr(order, 'typeTarget', UnitType.ALL)
                        target = simulation.get_nearest_enemy_in_reach(unit, type_target=type_target)
                        if target:
                            break
                    
                    # AvoidOrder / StayInFriendlySpaceOrder (target is reference point)
                    elif order_type == 'AvoidOrder':
                        type_units = getattr(order, 'typeUnits', UnitType.ALL)
                        target = simulation.get_nearest_enemy_in_sight(unit, type_target=type_units)
                        if target:
                            break
                    elif order_type == 'StayInFriendlySpaceOrder':
                        type_units = getattr(order, 'typeUnits', UnitType.ALL)
                        target = simulation.get_nearest_friendly_in_sight(unit, type_target=type_units)
                        if target:
                            break
                    
                    # MoveTowardEnemyWithSpecificAttribute
                    elif order_type == 'MoveTowardEnemyWithSpecificAttribute':
                        attr_name = getattr(order, 'attribute_name', None)
                        if attr_name:
                            target = simulation.get_nearest_enemy_with_attributes(unit, attr_name)
                            if target:
                                break

        target_name = None
        target_uid = None
        if target is not None:
            t_name = getattr(target, 'name', type(target).__name__)
            t_team = resolve_team(getattr(target, 'team', getattr(target, 'equipe', None)))
            target_name = f"{t_name} (Team {'A' if t_team == Team.A else 'B'})"
            target_uid = id(target)

        return UnitRepr(
            type=unit_type,
            team=team,
            uid=uid,
            letter=resolve_letter(unit_type),
            x=getattr(unit, 'x', 0.0),
            y=getattr(unit, 'y', 0.0),
            hp=max(0, hp),
            hp_max=hp_max,
            status=UnitStatus.ALIVE if hp > 0 else UnitStatus.DEAD,
            damage_dealt=getattr(unit, 'damage_dealt', 0),
            target_name=target_name,
            target_uid=target_uid,
            armor=getattr(unit, 'armor', None),
            attack=getattr(unit, 'attack', None),
            range=getattr(unit, 'range', None),
            reload_time=getattr(unit, 'reload_time', None),
            reload_val=getattr(unit, 'reload', None),
            speed=getattr(unit, 'speed', None),
            accuracy=getattr(unit, 'accuracy', None)
        )

    def _get_hp_max(self, unit, uid: int, current_hp: int) -> int:
        """
        @brief Get or estimate hp_max.
        @param unit Unit object
        @param uid Unit ID
        @param current_hp Current HP value
        @return Maximum HP value
        """
        if hasattr(unit, 'hp_max'):
            return getattr(unit, 'hp_max')
        if uid not in self._hp_memory and current_hp > 0:
            self._hp_memory[uid] = current_hp
        return self._hp_memory.get(uid, current_hp)
