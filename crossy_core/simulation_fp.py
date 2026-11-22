"""Fixed-point tick transitions for grass, roads and moving logs.

Player moves are instantaneous at tick start. Hazards then advance for
one tick. This is a provisional simulation contract. Railways are
explicitly unsupported; no runtime or fairness certification exists.
"""
from .patterns import WIDTH, GRASS, ROAD, RIVER
from .physics import SUBTILE, BOARD_UNITS, swept_overlap, carry_on_log

MOVES = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))

def step_fp(rows, position, tick, direction):
    """Return (local row, fixed-point x), or None for death/blockage.

    A blocked tree move leaves the player on the source row and resolves
    its hazards for this tick. Other failed moves are fatal/out of bounds.
    """
    if direction not in MOVES:
        raise ValueError("invalid direction")
    if type(tick) is not int or tick < 0:
        raise ValueError("invalid tick")
    y, x = position
    if not (type(y) is int and type(x) is int
            and 0 <= y < len(rows) and 0 <= x <= BOARD_UNITS - SUBTILE):
        raise ValueError("invalid position")
    if any(row.kind not in (GRASS, ROAD, RIVER) for row in rows):
        raise NotImplementedError("railway physics not yet integrated")
    dy, dx = direction
    ny, nx = y + dy, x + dx * SUBTILE
    if not (0 <= ny < len(rows) and 0 <= nx <= BOARD_UNITS - SUBTILE):
        return None
    target = rows[ny]
    if target.kind == GRASS:
        first = nx // SUBTILE
        last = (nx + SUBTILE - 1) // SUBTILE
        if any(target.trees & (1 << c) for c in range(first, last + 1)):
            ny, nx = y, x
            target = rows[ny]
    if target.kind == GRASS:
        return (ny, nx)
    if target.kind == ROAD:
        start = (target.phase + target.direction * target.speed * tick) * SUBTILE
        velocity = target.direction * target.speed * SUBTILE
        collision = swept_overlap(nx, nx + SUBTILE, start,
                                  target.length * SUBTILE,
                                  target.spacing * SUBTILE, velocity)
        return None if collision else (ny, nx)
    carried = carry_on_log(
        nx, (target.phase + target.direction * target.speed * tick) * SUBTILE,
        target.length, target.spacing, target.direction * target.speed * SUBTILE)
    return None if carried is None else (ny, carried)
