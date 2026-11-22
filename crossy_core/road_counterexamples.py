"""Offline road counterexample reports; never grants runtime approval."""
from .long_road_audit import road_sections
from .join_screen import screen_join
from .all_boundary_audit import audit_all_boundaries

def inspect_roads(count=2, speed=2, spacing=8, length=2,
                  horizon=8, max_period=64, max_states=4096):
    sections = road_sections(count=count, speed=speed,
                             spacing=spacing, length=length)
    rows = tuple(row for section in sections for row in section)
    whole = screen_join(sections, horizon=horizon, max_period=max_period)
    boundaries = audit_all_boundaries(
        sections, horizon=horizon, continuation_horizon=horizon,
        total_horizon=horizon, max_period=max_period,
        max_states=max_states)
    failures = tuple(
        (result["boundary_index"], phase, reason)
        for result in boundaries["results"]
        for phase, reason in result["failures"]
    )
    return {
        "configuration": (count, speed, spacing, length, horizon),
        "row_signatures": tuple(row.signature() for row in rows),
        "whole_join_passed": whole["passed"],
        "boundary_failures": failures,
        "passed": whole["passed"] and boundaries["passed"],
        "deployable": False,
    }

def inspect_matrix(configurations, horizon=8, max_period=64):
    """Review a caller-supplied bounded matrix; invalid cases fail closed."""
    if not isinstance(configurations, (tuple, list)) or not 1 <= len(configurations) <= 16:
        raise ValueError("configuration count must be 1..16")
    reports = []
    for config in configurations:
        if not isinstance(config, (tuple, list)) or len(config) != 4:
            raise ValueError("configuration must be count,speed,spacing,length")
        reports.append(inspect_roads(*config, horizon=horizon,
                                     max_period=max_period))
    return tuple(reports)
