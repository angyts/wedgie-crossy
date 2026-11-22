"""Exact boundary-state diagnostics for a finite, joined-world search.

Every state contains player position, absolute tick and camera state.
No state is reduced to an aggregate boundary count. This remains an
experimental existential search, NOT a compositional fairness proof.
"""
from .joins import join_rows
from .patterns import GRASS, WIDTH
from .physics import SUBTILE
from .simulation_fp import step_fp, MOVES
from .camera import Camera

def _signature(position, tick, camera):
    return (position[0], position[1], tick, camera.best_row,
            camera.last_progress_tick, camera.boundary)

def trace_contracts(sections, entry_columns=(5,), entry_phase=0,
                    horizon=64, reaction_ticks=0, grace_ticks=100,
                    pressure_interval=20, initial_boundary=-3):
    """Report exact first-arrival boundary states and successful exits.

    The entire world shares one clock and one evolving camera per path.
    Boundaries are indexed by the final row of each supplied section.
    Successful final states are a subset of reachable final-boundary
    states, preserving exact tick and camera values for further analysis.
    """
    rows = join_rows(sections)
    if rows[0].kind != GRASS:
        raise ValueError("entry must be grass")
    if type(entry_phase) is not int or entry_phase < 0:
        raise ValueError("invalid phase")
    if type(horizon) is not int or horizon < 1:
        raise ValueError("invalid horizon")
    if type(reaction_ticks) is not int or not 0 <= reaction_ticks <= horizon:
        raise ValueError("invalid reaction delay")
    if not entry_columns or any(type(x) is not int or not 0 <= x < WIDTH
                                for x in entry_columns):
        raise ValueError("invalid entry columns")
    camera = Camera(grace_ticks, pressure_interval, initial_boundary)
    endpoints = []
    end = -1
    for section in sections:
        end += len(section)
        endpoints.append(end)
    boundary_states = [set() for _ in sections]
    frontier = {}
    for col in entry_columns:
        if not rows[0].trees & (1 << col):
            pos = (0, col * SUBTILE)
            frontier[_signature(pos, entry_phase, camera)] = (pos, camera.clone())
    for pos, cam in frontier.values():
        for i, endpoint in enumerate(endpoints):
            if pos[0] == endpoint:
                boundary_states[i].add(_signature(pos, entry_phase, cam))
    final = set()
    for elapsed in range(horizon):
        if not frontier:
            break
        tick = entry_phase + elapsed
        next_frontier = {}
        choices = ((0, 0),) if elapsed < reaction_ticks else MOVES
        for pos, cam in frontier.values():
            for move in choices:
                result = step_fp(rows, pos, tick, move)
                if result is None:
                    continue
                updated = cam.clone()
                if updated.update(result[0], elapsed + 1):
                    continue
                sig = _signature(result, tick + 1, updated)
                if result[0] == endpoints[-1]:
                    final.add(sig)
                for i, endpoint in enumerate(endpoints):
                    # Record all boundary arrivals, including later visits.
                    if result[0] == endpoint:
                        boundary_states[i].add(sig)
                next_frontier[sig] = (result, updated)
        frontier = next_frontier
    return {
        "reached": bool(final),
        "boundary_states": tuple(frozenset(states) for states in boundary_states),
        "successful_exits": frozenset(final),
        "entry_phase": entry_phase,
        "horizon": horizon,
        "deployable": False,
    }
