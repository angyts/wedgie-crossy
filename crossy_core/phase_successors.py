"""Offline phase-aware exact-state continuation audit.

For each discrete hazard phase, record states at a specified section
boundary and demand that every recorded state can reach the final row.
All checks are under the provisional tick/camera model. This is NOT
production certification and does not modify the approved generator.
"""
from .joins import join_rows
from .certification import phase_period
from .state_contracts import trace_contracts
from .successor_contracts import check_successors

def audit_successors(sections, boundary_index=0, horizon=8,
                     continuation_horizon=8, max_period=64,
                     max_states=4096, **settings):
    if not isinstance(sections, (tuple, list)) or len(sections) < 2:
        raise ValueError("at least two sections required")
    if type(boundary_index) is not int or not 0 <= boundary_index < len(sections) - 1:
        raise ValueError("invalid boundary index")
    if (type(horizon) is not int or horizon < 1
            or type(continuation_horizon) is not int or continuation_horizon < 0
            or type(max_states) is not int or max_states < 1):
        raise ValueError("invalid search bounds")
    rows = join_rows(sections)
    period = phase_period(rows, max_period=max_period)
    failures = []
    checked = 0
    for phase in range(period):
        evidence = trace_contracts(sections, entry_phase=phase,
                                   horizon=horizon, **settings)
        states = evidence["boundary_states"][boundary_index]
        if not states:
            failures.append((phase, "unreachable-boundary"))
            continue
        if len(states) > max_states:
            failures.append((phase, "state-cap-exceeded"))
            continue
        checked += len(states)
        result = check_successors(
            sections, states, entry_phase=phase,
            horizon=continuation_horizon,
            grace_ticks=settings.get("grace_ticks", 100),
            pressure_interval=settings.get("pressure_interval", 20),
            initial_boundary=settings.get("initial_boundary", -3))
        if not result["passed"]:
            failures.append((phase, "no-continuation-for-some-states"))
    return {"passed": not failures, "phases_checked": period,
            "states_checked": checked, "failures": tuple(failures),
            "boundary_index": boundary_index, "deployable": False}
