"""Experimental multi-terrain time-expanded crossing search.

One move is instantaneous at the start of a tick, then hazards advance
for that tick. Player horizontal coordinates are fixed-point. Rail trains
are whole-row pulses; warnings prohibit entering a rail row. This is a
conservative abstraction, not an accurate moving-train rendering model.
No certified pattern families are produced by this module.
"""
from .patterns import WIDTH, GRASS, ROAD, RIVER, RAIL
from .physics import SUBTILE, BOARD_UNITS, swept_overlap, carry_on_log

MOVES = ((0, 0), (1, 0), (-1, 0), (0, SUBTILE), (0, -SUBTILE))

def train_active(row, tick):
    return (tick + row.phase) % row.period < row.length

def train_warning(row, tick):
    phase = (tick + row.phase) % row.period
    return row.period - row.warning <= phase < row.period

def _road_safe(row, x, tick):
    return not swept_overlap(
        x, x + SUBTILE,
        (row.phase + row.direction * row.speed * tick) * SUBTILE,
        row.length * SUBTILE, row.spacing * SUBTILE,
        row.direction * row.speed * SUBTILE)

def _river_next(row, x, tick):
    return carry_on_log(
        x, (row.phase + row.direction * row.speed * tick) * SUBTILE,
        row.length, row.spacing, row.direction * row.speed * SUBTILE)

def _transition(row, x, tick, entering):
    if x < 0 or x + SUBTILE > BOARD_UNITS:
        return None
    if row.kind == GRASS:
        # For sub-tile positions, any touched tree column blocks.
        left, right = x // SUBTILE, (x + SUBTILE - 1) // SUBTILE
        if any(row.trees & (1 << c) for c in range(left, right + 1)):
            return None
        return x
    if row.kind == ROAD:
        return x if _road_safe(row, x, tick) else None
    if row.kind == RIVER:
        return _river_next(row, x, tick)
    if row.kind == RAIL:
        if train_active(row, tick) or train_active(row, tick + 1):
            return None
        if entering and train_warning(row, tick):
            return None
        return x
    raise ValueError("unknown terrain")

def validate_multiterrain(rows, entry_columns=(5,), entry_phases=(0,),
                          horizon=64, reaction_ticks=0, max_wait_ticks=None):
    """Return True only if all sampled entry phases reach the last row.

    max_wait_ticks limits consecutive stationary decisions (a camera
    pressure proxy). This is NOT a real rising camera-boundary model.
    States are (row, sub-tile x, consecutive waits).
    """
    if not rows or type(horizon) is not int or horizon < 1:
        raise ValueError("invalid rows or horizon")
    if any(row.index != rows[0].index + i for i, row in enumerate(rows)):
        raise ValueError("noncontiguous rows")
    if not entry_columns or any(type(x) is not int or not 0 <= x < WIDTH
                                for x in entry_columns):
        raise ValueError("invalid entry columns")
    if not entry_phases or any(type(t) is not int or t < 0
                               for t in entry_phases):
        raise ValueError("invalid entry phases")
    if type(reaction_ticks) is not int or not 0 <= reaction_ticks <= horizon:
        raise ValueError("invalid reaction delay")
    if max_wait_ticks is not None and (
            type(max_wait_ticks) is not int or max_wait_ticks < 0):
        raise ValueError("invalid wait bound")
    for phase in entry_phases:
        frontier = {(0, x * SUBTILE, 0) for x in entry_columns
                    if _transition(rows[0], x * SUBTILE, phase, False) is not None}
        if not frontier:
            return False
        if len(rows) == 1:
            continue
        reached = False
        for step in range(horizon):
            tick = phase + step
            nxt = set()
            for y, x, waits in frontier:
                choices = ((0, 0),) if step < reaction_ticks else MOVES
                for dy, dx in choices:
                    ny, nx = y + dy, x + dx
                    if not (0 <= ny < len(rows)):
                        continue
                    new_waits = waits + 1 if dy == 0 and dx == 0 else 0
                    if max_wait_ticks is not None and new_waits > max_wait_ticks:
                        continue
                    result = _transition(rows[ny], nx, tick, ny != y)
                    if result is not None:
                        nxt.add((ny, result, new_waits))
            frontier = nxt
            if any(y == len(rows) - 1 for y, _, _ in frontier):
                reached = True
                break
            if not frontier:
                break
        if not reached:
            return False
    return True
