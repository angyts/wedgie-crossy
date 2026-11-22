"""Experimental swept-road path search, not a fairness certificate.

Discrete decisions occur once per tick. Each player move is treated as
instantaneous at the START of a tick, followed by continuous hazard motion.
This is a defined simplified model, not actual game movement interpolation.
River and railway rows are rejected until their dynamics are integrated.
"""
from .patterns import WIDTH, GRASS, ROAD
from .physics import SUBTILE, swept_overlap

MOVES = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))

def _road_safe(row, x, tick):
    spacing = row.spacing * SUBTILE
    length = row.length * SUBTILE
    start = row.phase * SUBTILE + row.direction * row.speed * SUBTILE * tick
    delta = row.direction * row.speed * SUBTILE
    return not swept_overlap(x * SUBTILE, (x + 1) * SUBTILE,
                             start, length, spacing, delta)

def _safe(row, x, tick):
    if row.kind == GRASS:
        return not (row.trees & (1 << x))
    return _road_safe(row, x, tick)

def validate_swept_roads(rows, entry_columns=(5,), horizon=128,
                         entry_phases=(0,), reaction_ticks=0):
    """Require a route for EVERY supplied entry phase.

    A player must wait reaction_ticks on the starting tile before moving.
    Source tiles must be safe during each tick, including after moving.
    This is conservative for moves made at tick boundaries, but not a
    general proof for arbitrary player motion or entry conditions.
    """
    if not rows or not isinstance(horizon, int) or horizon < 1:
        raise ValueError("invalid horizon/rows")
    if any(row.kind not in (GRASS, ROAD) for row in rows):
        raise NotImplementedError("river and rail dynamics not integrated")
    if any(row.index != rows[0].index + i for i, row in enumerate(rows)):
        raise ValueError("noncontiguous rows")
    if not entry_columns or any(type(x) is not int or not 0 <= x < WIDTH
                                for x in entry_columns):
        raise ValueError("invalid entry columns")
    if not entry_phases or any(type(t) is not int or t < 0 for t in entry_phases):
        raise ValueError("invalid phases")
    if type(reaction_ticks) is not int or not 0 <= reaction_ticks <= horizon:
        raise ValueError("invalid reaction delay")
    for phase in entry_phases:
        frontier = {(0, x) for x in entry_columns
                    if _safe(rows[0], x, phase)}
        if not frontier:
            return False
        if len(rows) == 1:
            continue
        reached = False
        for step in range(horizon):
            tick = phase + step
            next_frontier = set()
            for y, x in frontier:
                # Hazard moves during this tick, even if player waits.
                if step < reaction_ticks:
                    moves = ((0, 0),)
                else:
                    moves = MOVES
                for dy, dx in moves:
                    ny, nx = y + dy, x + dx
                    if not (0 <= ny < len(rows) and 0 <= nx < WIDTH):
                        continue
                    if not _safe(rows[ny], nx, tick):
                        continue
                    next_frontier.add((ny, nx))
            frontier = next_frontier
            if any(y == len(rows) - 1 for y, _ in frontier):
                reached = True
                break
            if not frontier:
                break
        if not reached:
            return False
    return True
