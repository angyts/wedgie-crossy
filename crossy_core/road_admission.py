"""Offline road-family admission experiment, never runtime approval.

This intentionally requires both a complete-phase whole-join screen and
a phase-aware exact-state successor audit. It does not claim universal
fairness; the approved generator remains grass-only.
"""
from .patterns import GRASS, ROAD, Row
from .join_screen import screen_join
from .phase_successors import audit_successors

def road_fixture():
    """A small, reproducible grass-road-grass-road-grass candidate."""
    return (
        (Row(0, GRASS), Row(1, ROAD, direction=1, speed=2,
                           spacing=8, length=2)),
        (Row(2, GRASS), Row(3, ROAD, direction=-1, speed=2,
                           spacing=8, length=2), Row(4, GRASS)),
    )

def review_road_fixture(horizon=12, continuation_horizon=12,
                        max_period=64, max_states=4096):
    sections = road_fixture()
    whole = screen_join(sections, horizon=horizon,
                        max_period=max_period)
    successors = audit_successors(
        sections, boundary_index=0, horizon=horizon,
        continuation_horizon=continuation_horizon,
        max_period=max_period, max_states=max_states)
    return {
        "passed": whole["passed"] and successors["passed"],
        "whole_join": whole,
        "successors": successors,
        "deployable": False,
        "runtime_allowlisted": False,
    }
