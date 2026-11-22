"""Experimental explicit section-boundary state propagation.

Every search state retains player position, absolute hazard tick and
camera progress. Sections are traversed on one shared timeline; this
does NOT yet certify arbitrary section-family composition.
"""
from .joins import join_rows
from .patterns import GRASS, WIDTH
from .physics import SUBTILE
from .simulation_fp import MOVES, step_fp
from .camera import Camera

def trace_boundaries(sections, entry_columns=(5,), entry_phase=0,
                     horizon=64, reaction_ticks=0, grace_ticks=100,
                     pressure_interval=20, initial_boundary=-3):
    """Return per-boundary reachable state counts and final reachability.

    A checkpoint is reached only by entering its final row from an
    earlier row. The same camera and tick are carried onward. This
    checks one specified entry phase, not every possible phase.
    """
    rows = join_rows(sections)
    if rows[0].kind != GRASS:
        raise ValueError("entry must be grass")
    if type(entry_phase) is not int or entry_phase < 0:
        raise ValueError("invalid entry phase")
    if type(horizon) is not int or horizon < 1:
        raise ValueError("invalid horizon")
    if type(reaction_ticks) is not int or not 0 <= reaction_ticks <= horizon:
        raise ValueError("invalid reaction delay")
    if not entry_columns or any(type(x) is not int or not 0 <= x < WIDTH
                                for x in entry_columns):
        raise ValueError("invalid entry columns")
    base = Camera(grace_ticks, pressure_interval, initial_boundary)
    endpoints = []
    n = 0
    for section in sections:
        n += len(section)
        endpoints.append(n - 1)
    counts = [0] * len(sections)
    frontier = {}
    for x in entry_columns:
        if not rows[0].trees & (1 << x):
            pos = (0, x * SUBTILE)
            frontier[(pos, 0, 0, base.boundary)] = (pos, base.clone())
    if not frontier:
        return {"reached": False, "boundary_counts": tuple(counts),
                "phases_checked": 1, "horizon": horizon}
    if endpoints[0] == 0:
        counts[0] = len(frontier)
    for elapsed in range(horizon):
        choices = ((0, 0),) if elapsed < reaction_ticks else MOVES
        nxt = {}
        for pos, cam in frontier.values():
            for direction in choices:
                result = step_fp(rows, pos, entry_phase + elapsed, direction)
                if result is None:
                    continue
                updated = cam.clone()
                if updated.update(result[0], elapsed + 1):
                    continue
                key = (result, updated.best_row,
                       updated.last_progress_tick, updated.boundary)
                nxt[key] = (result, updated)
        frontier = nxt
        for i, end in enumerate(endpoints):
            at_boundary = sum(1 for pos, _ in frontier.values()
                              if pos[0] == end)
            if at_boundary > counts[i]:
                counts[i] = at_boundary
        if not frontier:
            break
    return {"reached": counts[-1] > 0,
            "boundary_counts": tuple(counts),
            "phases_checked": 1, "horizon": horizon}
