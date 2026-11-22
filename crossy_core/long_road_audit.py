"""Offline stress fixtures for longer road sequences.

A passing result is diagnostic under the provisional model only.
No road candidate is approved for the runtime generator.
"""
from .patterns import Row, GRASS, ROAD
from .join_screen import screen_join
from .all_boundary_audit import audit_all_boundaries

def road_sections(count=3, speed=2, spacing=8, length=2):
    if type(count) is not int or not 1 <= count <= 4:
        raise ValueError("count must be 1..4")
    if type(speed) is not int or speed < 1:
        raise ValueError("invalid speed")
    sections = []
    for i in range(count):
        y = 2 * i
        sections.append((
            Row(y, GRASS),
            Row(y + 1, ROAD, direction=1 if i % 2 == 0 else -1,
                speed=speed, spacing=spacing, length=length, phase=i),
        ))
    sections.append((Row(2 * count, GRASS),))
    return tuple(sections)

def audit_roads(count=3, horizon=16, max_period=64,
                max_states=4096, **settings):
    sections = road_sections(count=count)
    whole = screen_join(sections, horizon=horizon,
                        max_period=max_period, **settings)
    boundaries = audit_all_boundaries(
        sections, horizon=horizon, continuation_horizon=horizon,
        total_horizon=horizon, max_period=max_period,
        max_states=max_states, **settings)
    return {
        "passed": whole["passed"] and boundaries["passed"],
        "whole_join": whole, "boundaries": boundaries,
        "deployable": False, "runtime_allowlisted": False,
    }
