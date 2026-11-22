"""Offline adversarial phase sweep for complete joined sections.

This is diagnostic evidence, NOT certification. Uses the existing
boundary-state search, which has provisional physics and camera rules.
"""
from .joins import join_rows
from .certification import phase_period
from .boundary_states import trace_boundaries

def sweep_join(sections, max_period=256, **settings):
    """Test every discrete phase of the joined rows; fail closed on cap.

    Return both successful and failing phases. A positive result means
    that at least one route exists per phase from the specified entry
    columns, not that every player position can survive.
    """
    rows = join_rows(sections)
    period = phase_period(rows, max_period=max_period)
    failures = []
    boundary_min = [None] * len(sections)
    for phase in range(period):
        evidence = trace_boundaries(sections, entry_phase=phase, **settings)
        if not evidence["reached"]:
            failures.append(phase)
        for i, count in enumerate(evidence["boundary_counts"]):
            if boundary_min[i] is None or count < boundary_min[i]:
                boundary_min[i] = count
    return {
        "passed": not failures,
        "phases_checked": period,
        "failing_phases": tuple(failures),
        "minimum_boundary_counts": tuple(boundary_min),
        "model": "boundary-states-prototype-v1",
        "deployable": False,
    }
