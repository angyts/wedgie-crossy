"""Offline discrete time-expanded feasibility checker, version 0.

A conservative *prototype*, not a production fairness certificate.
Each tick is one move opportunity. Hazards occupy whole columns. River
platform drift, swept collisions, train warnings, camera pressure and
human reaction budgets are NOT modeled here; those require later work.
"""
from .patterns import WIDTH, GRASS, ROAD, RIVER, RAIL

MOVES = ((0, 0), (0, -1), (0, 1), (1, 0), (-1, 0))

def occupied(row, column, tick):
    """Return whether a column is covered at this integer time."""
    if row.kind == GRASS:
        return bool(row.trees & (1 << column))
    if row.kind == RAIL:
        # A periodic train occupies the entire row for length ticks.
        return (tick + row.phase) % row.period < row.length
    # Periodic vehicles or logs with modular wrapping.
    phase = (column - row.direction * row.speed * tick - row.phase) % row.spacing
    present = phase < row.length
    return present if row.kind == ROAD else not present

def validate(rows, entry_columns=(5,), horizon=128, entry_phases=(0,),
             require_all_phases=True):
    """Check time-feasible reachability across ordered rows.

    Returns True if each tested entry phase has a route from row 0 to
    the final row. Waiting and one-cell moves each cost one tick.
    This checks sampled entry phases, NOT all possible starting states.
    """
    if not rows or not isinstance(horizon, int) or horizon < 1:
        raise ValueError("rows and positive horizon required")
    if len(rows) > horizon + 1:
        return False
    if any(rows[i].index != rows[0].index + i for i in range(len(rows))):
        raise ValueError("rows must have contiguous indices")
    if not entry_columns or not entry_phases:
        raise ValueError("entry columns and phases required")
    if any(not isinstance(c, int) or not 0 <= c < WIDTH for c in entry_columns):
        raise ValueError("invalid entry column")
    if any(not isinstance(p, int) or p < 0 for p in entry_phases):
        raise ValueError("invalid entry phase")
    results = []
    for phase in entry_phases:
        frontier = {(0, c) for c in entry_columns if not occupied(rows[0], c, phase)}
        reached = any(y == len(rows) - 1 for y, _ in frontier)
        for step in range(1, horizon + 1):
            if reached or not frontier:
                break
            tick = phase + step
            next_frontier = set()
            for y, x in frontier:
                # Must survive on the source tile through the tick.
                if occupied(rows[y], x, tick):
                    continue
                for dy, dx in MOVES:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < len(rows) and 0 <= nx < WIDTH:
                        if not occupied(rows[ny], nx, tick):
                            next_frontier.add((ny, nx))
            frontier = next_frontier
            reached = any(y == len(rows) - 1 for y, _ in frontier)
        results.append(reached)
    return all(results) if require_all_phases else any(results)
