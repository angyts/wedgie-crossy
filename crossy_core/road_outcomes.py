"""Offline classification of existential and all-state road continuation.

The classes describe finite search evidence, not real-world fairness.
"""
from .joins import join_rows
from .certification import phase_period
from .state_contracts import trace_contracts
from .successor_contracts import can_continue

def classify_boundary(sections, boundary_index=0, horizon=8,
                      max_period=64, max_states=4096, **settings):
    if not isinstance(sections, (tuple, list)) or len(sections) < 2:
        raise ValueError("two or more sections required")
    if type(boundary_index) is not int or not 0 <= boundary_index < len(sections)-1:
        raise ValueError("invalid boundary")
    if type(horizon) is not int or horizon < 1:
        raise ValueError("invalid horizon")
    if type(max_states) is not int or max_states < 1:
        raise ValueError("invalid state cap")
    rows = join_rows(sections)
    period = phase_period(rows, max_period=max_period)
    outcomes = []
    for phase in range(period):
        trace = trace_contracts(sections, entry_phase=phase,
                                horizon=horizon, **settings)
        states = trace["boundary_states"][boundary_index]
        if len(states) > max_states:
            outcomes.append({"phase": phase, "classification": "state-cap-exceeded",
                             "reachable": len(states), "continuable": None})
            continue
        camera_settings = {
            "grace_ticks": settings.get("grace_ticks", 100),
            "pressure_interval": settings.get("pressure_interval", 20),
            "initial_boundary": settings.get("initial_boundary", -3),
        }
        viable = sum(can_continue(
            rows, state, entry_phase=phase,
            horizon=max(0, horizon - (state[2] - phase)),
            **camera_settings) for state in states)
        classification = (
            "unreachable-boundary" if not states else
            "no-viable-continuation" if viable == 0 else
            "mixed-continuation" if viable < len(states) else
            "all-recorded-states-continue"
        )
        outcomes.append({"phase": phase, "classification": classification,
                         "reachable": len(states), "continuable": viable})
    return {"phases_checked": period, "outcomes": tuple(outcomes),
            "deployable": False}
