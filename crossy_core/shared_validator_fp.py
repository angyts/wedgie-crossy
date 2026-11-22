"""Experimental reachability using the same fixed-point tick transition as gameplay.

Supports grass, roads and rivers; railway support is deliberately rejected.
All starting positions are on grass. Results depend on sampled phases,
finite horizon and instantaneous player movement; NOT fairness certification.
"""
from .patterns import GRASS, ROAD, RIVER, WIDTH
from .physics import SUBTILE
from .simulation_fp import step_fp, MOVES

def validate_fp(rows, entry_columns=(5,), entry_phases=(0,),
                horizon=64, reaction_ticks=0):
    if not rows or type(horizon) is not int or horizon < 1:
        raise ValueError("invalid rows/horizon")
    if any(row.index != rows[0].index + i for i, row in enumerate(rows)):
        raise ValueError("noncontiguous rows")
    if any(row.kind not in (GRASS, ROAD, RIVER) for row in rows):
        raise NotImplementedError("railway simulation pending")
    if rows[0].kind != GRASS:
        raise ValueError("entry row must be grass")
    if not entry_columns or any(type(c) is not int or not 0 <= c < WIDTH
                                for c in entry_columns):
        raise ValueError("invalid entry columns")
    if not entry_phases or any(type(p) is not int or p < 0
                               for p in entry_phases):
        raise ValueError("invalid entry phases")
    if type(reaction_ticks) is not int or not 0 <= reaction_ticks <= horizon:
        raise ValueError("invalid reaction delay")
    for phase in entry_phases:
        frontier = {(0, c * SUBTILE) for c in entry_columns
                    if not (rows[0].trees & (1 << c))}
        if not frontier:
            return False
        if len(rows) == 1:
            continue
        reached = False
        for elapsed in range(horizon):
            directions = ((0, 0),) if elapsed < reaction_ticks else MOVES
            nxt = set()
            for position in frontier:
                for direction in directions:
                    result = step_fp(rows, position, phase + elapsed, direction)
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
