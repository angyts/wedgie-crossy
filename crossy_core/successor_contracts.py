"""Experimental continuation checks from exact recorded boundary states.

Checks each supplied state independently, preserving hazard time and
camera state. A successful continuation is existential under a finite
horizon, NOT a universal fairness certificate.
"""
from .joins import join_rows
from .physics import BOARD_UNITS, SUBTILE
from .camera import Camera
from .simulation_fp import step_fp, MOVES

def can_continue(rows, state, entry_phase=0, horizon=32,
                 grace_ticks=100, pressure_interval=20,
                 initial_boundary=-3):
    """Can this exact (row,x,tick,best,last_progress,boundary) reach end?"""
    if len(state) != 6 or type(horizon) is not int or horizon < 0:
        raise ValueError("invalid state or horizon")
    y, x, tick, best, last, boundary = state
    if (any(type(v) is not int for v in state)
            or not 0 <= y < len(rows)
            or not 0 <= x <= BOARD_UNITS - SUBTILE
            or tick < entry_phase or last < 0
            or last > tick - entry_phase or best < y
            or boundary < initial_boundary):
        raise ValueError("invalid state fields")
    camera = Camera(grace_ticks, pressure_interval, initial_boundary)
    camera.best_row, camera.last_progress_tick, camera.boundary = best, last, boundary
    frontier = {(y, x, best, last, boundary): ((y, x), camera)}
    if y == len(rows) - 1:
        return True
    for offset in range(horizon):
        nxt = {}
        for pos, cam in frontier.values():
            for direction in MOVES:
                result = step_fp(rows, pos, tick + offset, direction)
                if result is None:
                    continue
                updated = cam.clone()
                if updated.update(result[0], tick + offset - entry_phase + 1):
                    continue
                if result[0] == len(rows) - 1:
                    return True
                key = (result[0], result[1], updated.best_row,
                       updated.last_progress_tick, updated.boundary)
                nxt[key] = (result, updated)
        frontier = nxt
        if not frontier:
            break
    return False

def check_successors(sections, boundary_states, entry_phase=0,
                     horizon=32, **settings):
    """Require every provided exact boundary state to have a continuation.

    States must be from the penultimate section boundary or earlier.
    Empty sets fail closed; this does not infer which states are
    representative or safe under arbitrary future sections.
    """
    rows = join_rows(sections)
    states = tuple(boundary_states)
    if not states:
        return {"passed": False, "checked": 0, "failed": (),
                "deployable": False}
    failures = tuple(s for s in states if not can_continue(
        rows, s, entry_phase=entry_phase, horizon=horizon, **settings))
    return {"passed": not failures, "checked": len(states),
            "failed": failures, "deployable": False}
