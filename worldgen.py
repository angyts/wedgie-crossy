"""Pure, allocation-light procedural terrain planning for Wedgie Crossy.

Prototype only: not yet wired into the device gameplay loop.
All terrain decisions are reproducible from a 32-bit seed and absolute row.
"""
WIDTH = 12
CENTER = 5
BLOCK = 16
MASK = (1 << WIDTH) - 1

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
    width = 1 + (value >> 8) % 8
    if offset >= width:
        return ("grass", 0, 0)
    kind = ("road", "logs", "lilies")[value % 3]
    return (kind, offset, width)

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
    return mask

def lily_mask(seed, row):
    kind, lane, width = section(seed, row)
    if kind != "lilies":
        return 0
    # Every row has 2–4 pads. Center guarantees a continuous crossing,
    # and tree_mask leaves the center clear on both banks.
    value = mix32(seed ^ (row * 0x27d4eb2d))
    mask = 1 << CENTER
    target = 2 + value % 3
    start = (value >> 8) % WIDTH
    for step in range(WIDTH):
        col = (start + step) % WIDTH
        if col != CENTER:
            mask |= 1 << col
            if mask.bit_count() >= target:
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

def road_mask(seed, row, phase):
    kind, lane, width = section(seed, row)
    if kind != "road":
        return 0
    direction = -1 if lane & 1 else 1
    offset = (phase * direction) % WIDTH
    origin = mix32(seed ^ row) % WIDTH
    return (1 << ((origin + offset) % WIDTH)) | (1 << ((origin + 6 + offset) % WIDTH))

def seed_from_ticks(ticks):
    """Vary each new run, without storing anything to flash.

    Timing-based variability is not cryptographic randomness.
    """
    return mix32(ticks ^ 0xa5a5c3c3)
