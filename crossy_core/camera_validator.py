"""Experimental time-expanded validator using shared simulation and camera.

Tracks each candidate path's independent camera state. No universal
fairness certificate: phases/horizon are finite and gameplay movement
is still instantaneous at tick boundaries.
"""
from .patterns import GRASS, WIDTH
from .physics import SUBTILE
from .simulation_fp import step_fp, MOVES
from .camera import Camera

def validate_camera(rows, entry_columns=(5,), entry_phases=(0,),
                    horizon=64, reaction_ticks=0,
                    grace_ticks=100, pressure_interval=20,
                    initial_boundary=-3):
    if not rows or type(horizon) is not int or horizon < 1:
        raise ValueError("invalid rows/horizon")
    if any(row.index != rows[0].index + i for i, row in enumerate(rows)):
        raise ValueError("noncontiguous rows")
    if rows[0].kind != GRASS:
        raise ValueError("entry must be grass")
    if not entry_columns or any(type(c) is not int or not 0 <= c < WIDTH
                                for c in entry_columns):
        raise ValueError("invalid entry columns")
    if not entry_phases or any(type(p) is not int or p < 0
                               for p in entry_phases):
        raise ValueError("invalid phases")
    if type(reaction_ticks) is not int or not 0 <= reaction_ticks <= horizon:
        raise ValueError("invalid reaction")
    base = Camera(grace_ticks, pressure_interval, initial_boundary)
    for phase in entry_phases:
        # Each state is (position, camera); do not merge states with
        # different progress clocks or boundaries.
        states = [((0, c * SUBTILE), base.clone()) for c in entry_columns
                  if not rows[0].trees & (1 << c)]
        if not states:
            return False
        if len(rows) == 1:
            continue
        reached = False
        for elapsed in range(horizon):
            tick = phase + elapsed
            nxt = {}
            choices = ((0, 0),) if elapsed < reaction_ticks else MOVES
            for position, camera in states:
                for direction in choices:
                    result = step_fp(rows, position, tick, direction)
                    if result is None:
                        continue
                    updated = camera.clone()
                    # Camera uses elapsed time since the beginning of the
                    # crossing, independent of absolute hazard phase.
                    if updated.update(result[0], elapsed + 1):
                        continue
                    if result[0] == len(rows) - 1:
                        reached = True
                        break
                    key = (result, updated.best_row,
                           updated.last_progress_tick, updated.boundary)
                    nxt[key] = (result, updated)
                if reached:
                    break
            if reached:
                break
            states = list(nxt.values())
            if not states:
                break
        if not reached:
            return False
    return True
