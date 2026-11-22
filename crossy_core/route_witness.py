"""Offline deterministic route witnesses using the shared fixed-point physics.

Not a runtime module or fairness certificate. The search is bounded,
and each witness can be replayed without invoking the search engine.
"""
from .joins import join_rows
from .patterns import GRASS, WIDTH
from .physics import SUBTILE
from .simulation_fp import MOVES, step_fp
from .camera import Camera

def replay_witness(sections, moves, entry_column=5, entry_phase=0,
                   grace_ticks=100, pressure_interval=20,
                   initial_boundary=-3):
    rows = join_rows(sections)
    if type(entry_column) is not int or not 0 <= entry_column < WIDTH:
        raise ValueError("invalid entry column")
    if type(entry_phase) is not int or entry_phase < 0:
        raise ValueError("invalid entry phase")
    if rows[0].kind != GRASS or rows[0].trees & (1 << entry_column):
        raise ValueError("invalid starting tile")
    cam = Camera(grace_ticks, pressure_interval, initial_boundary)
    pos = (0, entry_column * SUBTILE)
    positions = [pos]
    for elapsed, move in enumerate(moves):
        pos = step_fp(rows, pos, entry_phase + elapsed, tuple(move))
        if pos is None or cam.update(pos[0], elapsed + 1):
            return {"survived": False, "finished": False,
                    "positions": tuple(positions)}
        positions.append(pos)
    return {"survived": True, "finished": pos[0] == len(rows)-1,
            "positions": tuple(positions)}

def find_witness(sections, entry_column=5, entry_phase=0, horizon=16,
                 max_states=50000, grace_ticks=100, pressure_interval=20,
                 initial_boundary=-3):
    if type(horizon) is not int or horizon < 1:
        raise ValueError("invalid horizon")
    if type(max_states) is not int or max_states < 1:
        raise ValueError("invalid state cap")
    rows = join_rows(sections)
    if type(entry_column) is not int or not 0 <= entry_column < WIDTH:
        raise ValueError("invalid entry column")
    if type(entry_phase) is not int or entry_phase < 0:
        raise ValueError("invalid entry phase")
    if rows[0].kind != GRASS or rows[0].trees & (1 << entry_column):
        raise ValueError("invalid starting tile")
    cam = Camera(grace_ticks, pressure_interval, initial_boundary)
    start = (0, entry_column * SUBTILE)
    if len(rows) == 1:
        return {"found": True, "moves": (), "positions": (start,),
                "ticks": 0, "deployable": False}
    frontier = [(start, cam, (), (start,))]
    for elapsed in range(horizon):
        nxt = {}
        for pos, camera, moves, positions in frontier:
            for move in MOVES:
                new_pos = step_fp(rows, pos, entry_phase + elapsed, move)
                if new_pos is None:
                    continue
                new_camera = camera.clone()
                if new_camera.update(new_pos[0], elapsed + 1):
                    continue
                route = moves + (move,)
                path = positions + (new_pos,)
                if new_pos[0] == len(rows)-1:
                    return {"found": True, "moves": route,
                            "positions": path, "ticks": len(route),
                            "deployable": False}
                key = (new_pos, new_camera.best_row,
                       new_camera.last_progress_tick, new_camera.boundary)
                if key not in nxt:
                    nxt[key] = (new_pos, new_camera, route, path)
                if len(nxt) > max_states:
                    raise ValueError("state cap exceeded")
        frontier = list(nxt.values())
        if not frontier:
            break
    return {"found": False, "moves": (), "positions": (),
            "ticks": None, "deployable": False}
