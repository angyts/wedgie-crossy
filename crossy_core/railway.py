"""Experimental moving-train geometry, integer subtile coordinates.

A train starts entirely outside the board at cycle tick zero, then
traverses it at constant speed. Warnings precede cycle zero.
This module is independent of the older whole-row pulse prototype.
"""
from .patterns import RAIL, WIDTH
from .physics import SUBTILE

def transit_ticks(row):
    if row.kind != RAIL:
        raise ValueError("rail row required")
    return (WIDTH + row.length + row.speed - 1) // row.speed

def check_schedule(row):
    duration = transit_ticks(row)
    if duration + row.warning >= row.period:
        raise ValueError("train period too short for crossing and warning")
    return duration

def warning_active(row, tick):
    check_schedule(row)
    phase = (tick + row.phase) % row.period
    return phase >= row.period - row.warning

def train_interval(row, tick):
    """Return half-open [left,right) train interval at integer tick."""
    check_schedule(row)
    phase = (tick + row.phase) % row.period
    if phase >= transit_ticks(row):
        return None
    distance = phase * row.speed * SUBTILE
    length = row.length * SUBTILE
    if row.direction == 1:
        left = -length + distance
    else:
        left = WIDTH * SUBTILE - distance
    return (left, left + length)

def train_collision(row, player_x, tick):
    """Swept collision across [tick,tick+1], including train entry/exit."""
    check_schedule(row)
    phase = (tick + row.phase) % row.period
    if phase >= transit_ticks(row):
        return False
    length = row.length * SUBTILE
    delta = row.direction * row.speed * SUBTILE
    start = (-length if row.direction == 1 else WIDTH * SUBTILE)
    start += row.direction * phase * row.speed * SUBTILE
    swept_left = start + min(0, delta)
    swept_right = start + length + max(0, delta)
    return swept_left < player_x + SUBTILE and player_x < swept_right
