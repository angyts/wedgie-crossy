"""Time-expanded crossing search for procedural Crossy terrain.

Host-only validation. Each tick advances hazards by one grid cell; the player
may wait or take one orthogonal step. This is a simplified model, not an
exact simulation of the device's wall-clock input and LCD timing.
"""
from collections import deque
import crossy_worldgen as w

def safe(seed, row, col, phase):
    if not 0 <= col < w.WIDTH or row < 0:
        return False
    kind = w.section(seed, row)[0]
    if kind == "grass":
        return not (w.tree_mask(seed, row) & (1 << col))
    if kind == "road":
        return not (w.road_mask(seed, row, phase) & (1 << col))
    if kind == "lilies":
        return bool(w.lily_mask(seed, row) & (1 << col))
    return bool(w.log_mask(seed, row, phase) & (1 << col))

def crossing_possible(seed, block, max_ticks=160):
    """Find a path across a single hazard block from its lower grass bank.

    Returns (possible, earliest_tick). The 24-phase cycle is exact for the
    current one-cell-per-step masks. This searches a finite horizon and does
    not certify real-time reaction feasibility on hardware.
    """
    first = 8 + block * w.BLOCK
    lower = first - 1
    upper = first + w.BLOCK - 1
    # Reach the first grass row after the actual hazard, not a fixed offset.
    _, _, width = w.section(seed, first)
    target = first + width
    start = (lower, w.CENTER, 0)
    q = deque([(start, 0)])
    visited = {start}
    while q:
        (row, col, phase), tick = q.popleft()
        if row >= target:
            return True, tick
        if tick >= max_ticks:
            continue
        # Road periods 1/2 repeat over 24 shared updates; logs over 12.
        next_phase = (phase + 1) % 24
        kind = w.section(seed, row)[0]
        carried = col
        if kind == "logs" and w.log_position(seed,row,next_phase) != w.log_position(seed,row,phase):
            carried += w.log_direction(seed,row)
            if not 0 <= carried < w.WIDTH:
                continue
        # The player's old position must remain safe until the next phase.
        if not safe(seed, row, carried, next_phase):
            continue
        for dr, dc in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = row + dr, carried + dc
            if nr < lower or nr > upper or not safe(seed, nr, nc, next_phase):
                continue
            state = (nr, nc, next_phase)
            if state not in visited:
                visited.add(state)
                q.append((state, tick + 1))
    return False, None

def scan(seed_count=1000, blocks=8):
    failures = []
    for seed in range(seed_count):
        for block in range(blocks):
            possible, _ = crossing_possible(seed, block)
            if not possible:
                failures.append((seed, block, w.section(seed,8+block*w.BLOCK)[0]))
    return failures
