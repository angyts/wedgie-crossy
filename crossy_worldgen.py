"""Pure, allocation-light procedural terrain planning for Wedgie Crossy.

Prototype only: not yet wired into the device gameplay loop.
All terrain decisions are reproducible from a 32-bit seed and absolute row.
"""
WIDTH = 12
CENTER = 5
BLOCK = 16
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

def section(seed, row):
    """Return (kind, local_lane, width), or grass.

    Blocks contain a hazard section followed by a grass buffer. A single
    section is never more than 8 rows, leaving room to preview terrain.
    """
    if row < 16:
        return ("grass", 0, 0)
    index = (row - 16) // BLOCK
    offset = (row - 16) % BLOCK
    value = mix32(seed ^ (index * 0x9e3779b9))
    start = 16 + index * BLOCK
    if start < 30:
        low, high = 1, 2
    elif start < 70:
        low, high = 2, 5
    elif start < 120:
        low, high = 5, 8
    else:
        low, high = 6, 8
    width = low + (value >> 8) % (high - low + 1)
    if offset >= width:
        return ("grass", 0, 0)
    kind = ("road", "logs", "lilies")[value % 3]
    return (kind, offset, width)

def lily_route_col(seed, row):
    kind, lane, width = section(seed, row)
    if kind != "lilies":
        return None
    block = (row - 16) // BLOCK
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

def log_mask(seed, row, phase):
    kind, lane, width = section(seed, row)
    if kind != "logs":
        return 0
    direction = -1 if lane & 1 else 1
    offset = (phase * direction) % WIDTH
    origin = mix32(seed ^ row) % WIDTH
    mask = 0
    for start in (origin, (origin + 6) % WIDTH):
        for cell in range(3):
            mask |= 1 << ((start + cell + offset) % WIDTH)
    return mask

def road_direction(seed, row):
    """Independent reproducible direction per lane."""
    return -1 if mix32(seed ^ (row * 0x27d4eb2d)) & 1 else 1

def road_period(seed, row):
    """One tile per 1, 2 or 3 shared traffic updates."""
    return 1 + mix32(seed ^ (row * 0x165667b1)) % 3

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
