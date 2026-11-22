"""Integer fixed-point hazard motion and swept overlap primitives.

Coordinates are in subtiles; 256 units = one tile. Time is in simulation
ticks. A moving periodic obstacle spans [start, start + length) and repeats
every spacing units. The player occupies [x, x + 256).
"""
SUBTILE = 256
BOARD_UNITS = 12 * SUBTILE

def _valid(length, spacing):
    if not (isinstance(length, int) and isinstance(spacing, int)
            and 0 < length < spacing):
        raise ValueError("require 0 < length < spacing")

def periodic_overlap(left, right, start, length, spacing):
    """True if [left,right) overlaps any periodic obstacle interval."""
    _valid(length, spacing)
    if right <= left:
        raise ValueError("empty player interval")
    # For some integer k, start+k*spacing < right and
    # start+k*spacing+length > left.
    low = (left - start - length) // spacing + 1
    high = (right - start - 1) // spacing
    return low <= high

def swept_overlap(left, right, start, length, spacing, delta):
    """Conservative swept intersection during one tick.

    Moving objects traverse delta units, without teleporting at wrap.
    Periodic copies are treated as a continuous unwrapped lattice.
    Collision at any intermediate instant is detected. This assumes
    a stationary player for the tick; use relative delta if player moves.
    """
    _valid(length, spacing)
    if not isinstance(delta, int):
        raise ValueError("delta must be integer")
    swept_start = start + min(0, delta)
    swept_length = length + abs(delta)
    # Swept interval may exceed spacing: in that case the full lane is hit.
    if swept_length >= spacing:
        return True
    return periodic_overlap(left, right, swept_start, swept_length, spacing)

def road_collision(player_x, phase, length_tiles, spacing_tiles, velocity):
    """Swept vehicle collision over one tick, all parameters integer."""
    return swept_overlap(player_x, player_x + SUBTILE, phase,
                         length_tiles * SUBTILE, spacing_tiles * SUBTILE,
                         velocity)

def carry_on_log(player_x, phase, length_tiles, spacing_tiles, velocity):
    """Move with a log if supported at tick start and throughout the tick.

    Returns new x in subtiles or None if unsupported or carried offscreen.
    This is a one-tick same-log model, not a full river crossing solver.
    """
    length = length_tiles * SUBTILE
    spacing = spacing_tiles * SUBTILE
    _valid(length, spacing)
    if not periodic_overlap(player_x, player_x + SUBTILE,
                            phase, length, spacing):
        return None
    # Require the entire player footprint to lie on one log.
    # Pick the log whose start is <= player's left edge.
    k = (player_x - phase) // spacing
    log_left = phase + k * spacing
    if player_x + SUBTILE > log_left + length:
        return None
    new_x = player_x + velocity
    if new_x < 0 or new_x + SUBTILE > BOARD_UNITS:
        return None
    return new_x
