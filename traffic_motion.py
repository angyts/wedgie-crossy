"""Pure integer helpers for non-blocking traffic rendering.

This module does not change the game's collision model. Integrate only after
swept-collision and hardware performance tests have been completed.
"""

def pixel_offset(elapsed_ms, interval_ms, tile_px=20):
    """Return monotonic sub-tile progress in [0, tile_px].

    A zero or negative interval is treated as complete, avoiding division by
    zero. No floating-point math or allocations are required.
    """
    if tile_px <= 0:
        return 0
    if interval_ms <= 0 or elapsed_ms >= interval_ms:
        return tile_px
    if elapsed_ms <= 0:
        return 0
    return (elapsed_ms * tile_px) // interval_ms


def wrapped_position(origin_px, direction, offset_px, width_px=240):
    """Pixel origin on a circular road, for either traffic direction."""
    if width_px <= 0:
        raise ValueError("width_px must be positive")
    if direction not in (-1, 1):
        raise ValueError("direction must be -1 or 1")
    return (origin_px + direction * offset_px) % width_px


def dirty_span(old_x, new_x, sprite_width, screen_width=240):
    """Clipped union of two sprite footprints; None if fully offscreen.

    Wrapping objects need separate clipped spans at both screen edges.
    This function deliberately does not silently create an oversized region
    when the sprite crosses the circular seam.
    """
    if sprite_width <= 0 or screen_width <= 0:
        return None
    left = max(0, min(old_x, new_x))
    right = min(screen_width, max(old_x, new_x) + sprite_width)
    if right <= left:
        return None
    return (left, right - left)
