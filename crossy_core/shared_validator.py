"""Reachability search driven by the exact same step() as host gameplay.

Only grass/road sections supported. Entry-phase and time-horizon
assumptions are explicit; this is not a universal fairness certificate.
"""
from .simulation import step, DIRECTIONS
from .patterns import WIDTH, GRASS, ROAD

def validate_shared(rows, entry_columns=(5,), entry_phases=(0,),
                    horizon=64, reaction_ticks=0):
    if not rows or type(horizon) is not int or horizon < 1:
        raise ValueError("invalid rows/horizon")
    if any(row.index != rows[0].index + i for i, row in enumerate(rows)):
        raise ValueError("noncontiguous rows")
    if any(row.kind not in (GRASS, ROAD) for row in rows):
        raise NotImplementedError("river/rail not yet supported")
    if not entry_columns or any(type(x) is not int or not 0 <= x < WIDTH
                                for x in entry_columns):
        raise ValueError("invalid entry columns")
    if not entry_phases or any(type(t) is not int or t < 0
                               for t in entry_phases):
        raise ValueError("invalid entry phases")
    if type(reaction_ticks) is not int or not 0 <= reaction_ticks <= horizon:
        raise ValueError("invalid reaction delay")
    for phase in entry_phases:
        # Validate starting occupancy by applying the same simulation rule
        # at the tick before search; no hazard advance is assumed on entry.
        frontier = set()
        for x in entry_columns:
            row = rows[0]
            if row.kind == GRASS and not (row.trees & (1 << x)):
                frontier.add((0, x))
            elif row.kind == ROAD:
                # Do not accept starting on a road: entry requires safe grass.
                raise ValueError("entry row must be grass")
        if not frontier:
            return False
        if len(rows) == 1:
            continue
        reached = False
        for elapsed in range(horizon):
            directions = ((0, 0),) if elapsed < reaction_ticks else DIRECTIONS
            nxt = set()
            for position in frontier:
                for direction in directions:
                    result = step(rows, position, phase + elapsed, direction)
                    if result is not None:
                        nxt.add(result)
            frontier = nxt
            if any(y == len(rows) - 1 for y, _ in frontier):
                reached = True
                break
            if not frontier:
                break
        if not reached:
            return False
    return True
