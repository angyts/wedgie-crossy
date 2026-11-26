"""Offline, bounded time-expanded reachability for mixed terrain candidates.

This is an analysis tool, not a runtime dependency. A successful route is
evidence of feasibility under the modeled timing, NOT a human-fairness proof.
"""
import crossy_worldgen as w

MOVES = ((0, 0), (-1, 0), (1, 0), (0, 1), (0, -1))


def lane_kind(seed, row, mixed=True):
    live = w.section(seed, row)[0]
    if live == "rail":
        return live
    return w.mixed_section_candidate(seed, row) if mixed else live


def occupancy(seed, row, phase, kind):
    if kind == "rail":
        return w.train_mask(seed, row, phase)
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


def joined_route(seed, first_block, block_count=2, start_phase=0,
                 max_ticks=240, entry_columns=None, mixed=True):
    """Find a continuous route with compact predecessor links.

    Each search layer holds only reachable (row, col) states. Parents store
    (previous state, action) rather than copying full paths on every edge.
    Cached lane masks avoid repeating procedural calculations for every move.
    This is still a simplified one-input-per-tick feasibility model.
    """
    if block_count < 1 or max_ticks < 1:
        raise ValueError("block_count and max_ticks must be positive")
    first = 8 + first_block * w.BLOCK
    start = first - 1
    goal = first + block_count * w.BLOCK
    if entry_columns is None:
        entry_columns = (w.CENTER,)

    kinds = {}
    masks = {}

    def kind_at(row):
        if row not in kinds:
            kinds[row] = lane_kind(seed, row, mixed)
        return kinds[row]

    def mask_at(row, phase):
        key = (row, phase)
        if key not in masks:
            masks[key] = occupancy(seed, row, phase, kind_at(row))
        return masks[key]

    def safe_at(row, col, phase):
        if row < start or not 0 <= col < w.WIDTH:
            return False
        occupied = bool(mask_at(row, phase) & (1 << col))
        return occupied if kind_at(row) in ("logs", "lilies") else not occupied

    states = set()
    for col in entry_columns:
        if safe_at(start, col, start_phase):
            states.add((start, col))
    if not states:
        return None

    # Layer zero has no predecessors. Subsequent maps contain one parent
    # per reachable state, retaining the first deterministic BFS witness.
    parents = []
    for tick in range(max_ticks):
        phase = start_phase + tick
        next_states = set()
        links = {}
        for row, col in sorted(states):
            for move in MOVES:
                dc, dr = move
                nr, nc = row + dr, col + dc
                if not safe_at(nr, nc, phase):
                    continue
                kind = kind_at(nr)
                if kind == "logs" and mask_at(nr, phase) != mask_at(nr, phase + 1):
                    nc += w.log_direction(seed, nr)
                if not safe_at(nr, nc, phase + 1):
                    continue
                state = (nr, nc)
                if state in next_states:
                    continue
                next_states.add(state)
                links[state] = ((row, col), move)
                if nr >= goal:
                    path = [move]
                    previous = (row, col)
                    for earlier in reversed(parents):
                        previous, earlier_move = earlier[previous]
                        path.append(earlier_move)
                    path.reverse()
                    return tuple(path), phase + 1, nc
        parents.append(links)
        states = next_states
        if not states:
            break
    return None


def validate_joins(seed, first_block, block_count=2, phases=12,
                   max_ticks=240, entry_columns=None):
    """Count starting phases with a continuous multi-block witness.

    Reports an aggregate witness count, not a certified playable family.
    """
    if phases < 1:
        raise ValueError("phases must be positive")
    successes = 0
    for phase in range(phases):
        if joined_route(seed, first_block, block_count, phase,
                        max_ticks, entry_columns) is not None:
            successes += 1
    return successes, phases


def replay_joined_route(seed, first_block, moves, start_phase=0,
                        entry_col=w.CENTER, mixed=True):
    """Replay a witness from one entry state for deterministic verification."""
    row = 8 + first_block * w.BLOCK - 1
    col = entry_col
    if not safe(seed, row, col, start_phase, mixed):
        return None
    for tick, move in enumerate(moves):
        result = advance(seed, row, col, start_phase + tick, move, mixed)
        if result is None:
            return None
        row, col = result
    return row, col
