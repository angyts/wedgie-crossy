"""Offline, bounded time-expanded reachability for mixed terrain candidates.

This is an analysis tool, not a runtime dependency. A successful route is
evidence of feasibility under the modeled timing, NOT a human-fairness proof.
"""
import crossy_worldgen as w

MOVES = ((0, 0), (-1, 0), (1, 0), (0, 1), (0, -1))


def lane_kind(seed, row, mixed=True):
    return w.mixed_section_candidate(seed, row) if mixed else w.section(seed, row)[0]


def occupancy(seed, row, phase, kind):
    if kind == "road":
        shift = w.road_position(seed, row, phase)
        first, second = w.road_origins(seed, row)
        return (1 << ((first + shift) % w.WIDTH)) | (1 << ((second + shift) % w.WIDTH))
    if kind == "logs":
        # Use the same deterministic log parameter functions as the device,
        # even when a road lane is proposed as a mixed-section log lane.
        base = (w.log_section_value(seed, row) >> 8) % w.WIDTH
        stagger = (w.log_lane_value(seed, row) >> 10) % 2
        origin = (base + stagger) % w.WIDTH
        shift = w.log_position(seed, row, phase) % w.WIDTH
        length = w.log_length(seed, row)
        mask = 0
        for start in (origin, (origin + 4) % w.WIDTH, (origin + 8) % w.WIDTH):
            for cell in range(length):
                mask |= 1 << ((start + cell + shift) % w.WIDTH)
        return mask
    if kind == "lilies":
        return w.lily_mask(seed, row)
    return w.tree_mask(seed, row)


def safe(seed, row, col, phase, mixed=True):
    if not 0 <= col < w.WIDTH:
        return False
    kind = lane_kind(seed, row, mixed)
    occupied = bool(occupancy(seed, row, phase, kind) & (1 << col))
    return occupied if kind in ("logs", "lilies") else not occupied


def advance(seed, row, col, phase, move, mixed=True):
    """One input followed by one hazard tick; None means collision/death."""
    dc, dr = move
    nc, nr = col + dc, row + dr
    if nr < 0 or not safe(seed, nr, nc, phase, mixed):
        return None
    next_phase = phase + 1
    kind = lane_kind(seed, nr, mixed)
    if kind == "logs":
        before = occupancy(seed, nr, phase, kind)
        after = occupancy(seed, nr, next_phase, kind)
        if before != after:
            nc += w.log_direction(seed, nr)
            if not 0 <= nc < w.WIDTH:
                return None
    if not safe(seed, nr, nc, next_phase, mixed):
        return None
    return nr, nc


def route(seed, block, start_phase=0, max_ticks=120, mixed=True):
    """Return a witness path or None, using a bounded phase-aware BFS.

    Starts on the grass row preceding the section, in center column.
    Each transition consumes one traffic tick; moving and waiting are allowed.
    No diagonal moves. A route must reach the grass row after the section.
    """
    first = 8 + block * w.BLOCK
    goal = first + w.BLOCK
    start = first - 1
    if not safe(seed, start, w.CENTER, start_phase, mixed):
        return None
    states = {(start, w.CENTER): ()}
    for tick in range(max_ticks):
        phase = start_phase + tick
        next_states = {}
        for (row, col), path in states.items():
            for move in MOVES:
                result = advance(seed, row, col, phase, move, mixed)
                if result is None:
                    continue
                nr, nc = result
                if nr >= goal:
                    return path + (move,)
                if nr > goal or nr < start:
                    continue
                if (nr, nc) not in next_states:
                    next_states[(nr, nc)] = path + (move,)
        states = next_states
        if not states:
            break
    return None


def validate(seed, block, phases=12, max_ticks=120):
    """Report a phase-window witness count, not universal fairness."""
    successes = 0
    for phase in range(phases):
        if route(seed, block, phase, max_ticks) is not None:
            successes += 1
    return successes, phases
