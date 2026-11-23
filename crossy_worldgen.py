"""Pure, allocation-light procedural terrain planning for Wedgie Crossy.

Prototype only: not yet wired into the device gameplay loop.
All terrain decisions are reproducible from a 32-bit seed and absolute row.
"""
WIDTH = 12
CENTER = 5
BLOCK = 12
MASK = (1 << WIDTH) - 1

def count_bits(value):
    """Count set bits without CPython-only int.bit_count()."""
    count = 0
    while value:
        value &= value - 1
        count += 1
    return count

def mix32(value):
    value &= 0xffffffff
    value ^= value >> 16
    value = (value * 0x7feb352d) & 0xffffffff
    value ^= value >> 15
    value = (value * 0x846ca68b) & 0xffffffff
    return (value ^ (value >> 16)) & 0xffffffff

def _base_section(seed, row):
    """Return (kind, local_lane, width), or grass.

    Blocks contain a hazard section followed by a grass buffer. A single
    section is never more than 8 rows, leaving room to preview terrain.
    """
    if row < 8:
        return ("grass", 0, 0)
    index = (row - 8) // BLOCK
    offset = (row - 8) % BLOCK
    value = mix32(seed ^ (index * 0x9e3779b9))
    start = 8 + index * BLOCK
    if start < 30:
        low, high = 1, 2
    elif start < 70:
        low, high = 2, 5
    elif start < 120:
        low, high = 5, 7
    else:
        low, high = 6, 8
    width = low + (value >> 8) % (high - low + 1)
    if offset >= width:
        return ("grass", 0, 0)
    # Favor roads without eliminating log and lily sections.
    kind = ("road", "road", "road", "road", "road", "logs", "lilies")[value % 7]
    return (kind, offset, width)

def lily_route_col(seed, row):
    kind, lane, width = section(seed, row)
    if kind != "lilies":
        return None
    block = (row - 8) // BLOCK
    value = mix32(seed ^ (block * 0x6d2b79f5))
    col = 2 + value % (WIDTH - 4)
    for i in range(lane):
        turn = mix32(value ^ (i * 0x9e3779b9)) % 3 - 1
        col = max(1, min(WIDTH - 2, col + turn))
    return col

def lily_bank_route(seed, row):
    if section(seed, row)[0] != "grass":
        return 0
    target = None
    if section(seed, row + 1)[0] == "lilies":
        target = lily_route_col(seed, row + 1)
    elif row > 0 and section(seed, row - 1)[0] == "lilies":
        target = lily_route_col(seed, row - 1)
    if target is None:
        return 0
    mask = 0
    for col in range(min(CENTER, target), max(CENTER, target) + 1):
        mask |= 1 << col
    return mask

def tree_mask(seed, row):
    kind, _, _ = section(seed, row)
    if kind != "grass" or row < 2:
        return 0
    value = mix32(seed ^ (row * 0x85ebca6b))
    mask = 0
    for col in range(WIDTH):
        value = mix32(value + col + 1)
        if col != CENTER and value % 6 == 0:
            mask |= 1 << col
    return mask & ~lily_bank_route(seed, row)

def lily_mask(seed, row):
    kind, lane, width = section(seed, row)
    if kind != "lilies":
        return 0
    # Each row contains a landing pad at the previous row's route column,
    # so a sideways change never requires an impossible diagonal jump.
    value = mix32(seed ^ (row * 0x27d4eb2d))
    route = lily_route_col(seed, row)
    mask = 1 << route
    if lane > 0:
        previous = lily_route_col(seed, row - 1)
        mask |= 1 << previous
    target = max(count_bits(mask), 3 + value % 3)
    for step in range(WIDTH):
        col = (value + step * 5) % WIDTH
        mask |= 1 << col
        if count_bits(mask) >= target:
            break
    return mask

def log_section_value(seed, row):
    """Stable parameters for one river, independent of camera position."""
    block = (row - 8) // BLOCK
    return mix32(seed ^ (block * 0x7f4a7c15))

def log_lane_value(seed, row):
    return mix32(log_section_value(seed, row) ^ (row * 0x9e3779b9))

def log_direction(seed, row):
    # Neighboring lanes need not alternate, or move together.
    return -1 if log_lane_value(seed, row) & 1 else 1

def log_period(seed, row):
    return 1 + ((log_lane_value(seed, row) >> 3) & 1)

def log_position(seed, row, phase):
    return (phase // log_period(seed, row)) * log_direction(seed, row)

def log_length(seed, row):
    """Deterministic 2-3 tile logs, varying by lane."""
    return 2 + ((log_lane_value(seed, row) >> 16) % 2)

def log_mask(seed, row, phase):
    kind, lane, width = section(seed, row)
    if kind != "logs":
        return 0
    # Two variable-length trunks, with staggered lane origins.
    # At phase zero, adjacent lanes differ by at most one cell, so
    # the player can enter a river without a permanent offset barrier.
    base = (log_section_value(seed, row) >> 8) % WIDTH
    # Small deterministic offsets vary each lane without a fixed staircase.
    stagger = (log_lane_value(seed, row) >> 10) % 2
    origin = (base + stagger) % WIDTH
    offset = log_position(seed, row, phase) % WIDTH
    mask = 0
    # Three shorter trunks provide more transfer opportunities without
    # making each individual log excessively long.
    for start in (origin, (origin + 4) % WIDTH, (origin + 8) % WIDTH):
        for cell in range(log_length(seed, row)):
            mask |= 1 << ((start + cell + offset) % WIDTH)
    return mask

def road_direction(seed, row):
    """Independent reproducible direction per lane."""
    return -1 if mix32(seed ^ (row * 0x27d4eb2d)) & 1 else 1

def road_period(seed, row):
    """One tile per 1 or 2 shared traffic updates."""
    return 1 + mix32(seed ^ (row * 0x165667b1)) % 2

def road_position(seed, row, phase):
    """Monotonic lane clock: never derive positions from score."""
    return (phase // road_period(seed, row)) * road_direction(seed, row)

def road_origins(seed, row):
    value = mix32(seed ^ (row * 0x9e3779b9))
    first = value % WIDTH
    separation = 5 + (value >> 12) % 4
    return first, (first + separation) % WIDTH

def road_mask(seed, row, phase):
    kind, lane, width = section(seed, row)
    if kind != "road":
        return 0
    shift = road_position(seed, row, phase)
    first, second = road_origins(seed, row)
    return (1 << ((first + shift) % WIDTH)) | (1 << ((second + shift) % WIDTH))

def seed_from_ticks(ticks):
    """Vary each new run, without storing anything to flash.

    Timing-based variability is not cryptographic randomness.
    """
    return mix32(ticks ^ 0xa5a5c3c3)

def mixed_section_candidate(seed, row):
    """Experimental mixed-section proposal; NOT used by live section().

    A 12-row block retains the existing grass buffer. Only interior hazard
    lanes may alternate road/logs, and the first/last hazard lanes stay road.
    This function describes candidate layouts for offline route validation;
    it does not claim that a crossing is time-feasible.
    """
    kind, lane, width = _base_section(seed, row)
    if kind == "grass":
        return "grass"
    if width < 4 or kind != "road":
        return kind
    block = (row - 8) // BLOCK
    variant = mix32(seed ^ (block * 0x6d2b79f5))
    if (variant & 3) != 0:
        return kind
    if lane == 0 or lane == width - 1:
        return "road"
    return "logs" if ((lane + (variant >> 8)) & 1) else "road"

# Controlled physical-hardware trial; revert to False for baseline terrain.
# Offline route witnesses do not establish human reaction-time fairness.
MIXED_TERRAIN = True


def section(seed, row):
    """Single authoritative terrain kind for masks, collision and drawing."""
    kind, lane, width = _base_section(seed, row)
    if MIXED_TERRAIN and kind == "road":
        kind = mixed_section_candidate(seed, row)
    return kind, lane, width
