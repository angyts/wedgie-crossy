"""Shared one-tick movement contract for host simulation and validation.

Movement is instantaneous at tick start; road hazards sweep during tick.
This is an explicitly provisional gameplay rule, not yet a complete
physical movement model. River/rail require additional implementations.
"""
from .patterns import WIDTH, GRASS, ROAD
from .physics import SUBTILE, swept_overlap

DIRECTIONS = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))

def step(rows, position, tick, direction):
    """Return next (row_index, column), or None on collision/invalid move.

    Coordinates are local row indices; caller controls absolute time.
    """
    if direction not in DIRECTIONS:
        raise ValueError("invalid direction")
    y, x = position
    if not (0 <= y < len(rows) and 0 <= x < WIDTH):
        raise ValueError("invalid position")
    if any(row.kind not in (GRASS, ROAD) for row in rows):
        raise NotImplementedError("river and rail simulation pending")
    dy, dx = direction
    ny, nx = y + dy, x + dx
    if not (0 <= ny < len(rows) and 0 <= nx < WIDTH):
        return None
    row = rows[ny]
    if row.kind == GRASS:
        return None if row.trees & (1 << nx) else (ny, nx)
    start = (row.phase + row.direction * row.speed * tick) * SUBTILE
    if swept_overlap(nx * SUBTILE, (nx + 1) * SUBTILE, start,
                     row.length * SUBTILE, row.spacing * SUBTILE,
                     row.direction * row.speed * SUBTILE):
        return None
    return ny, nx
