"""Fail-closed, finite-domain section screening; NOT universal fairness proof.

Uses the shared fixed-point simulation plus camera model. A successful
screen means only that each enumerated phase admits some route under the
specified initial state, horizon, reaction budget and camera parameters.
"""
from .patterns import GRASS, ROAD, RIVER, RAIL, MAX_DANGER_RUN
from .railway import check_schedule
from .camera_validator import validate_camera

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    return a // gcd(a, b) * b

def phase_period(rows, max_period=256):
    """Find a bounded repeat period, refusing excessive phase domains."""
    if type(max_period) is not int or max_period < 1:
        raise ValueError("invalid phase cap")
    period = 1
    for row in rows:
        if row.kind in (ROAD, RIVER):
            # Displacement per tick is speed tiles, so phase repeats
            # after spacing/gcd(spacing,speed) ticks.
            p = row.spacing // gcd(row.spacing, row.speed)
        elif row.kind == RAIL:
            check_schedule(row)
            p = row.period
        elif row.kind == GRASS:
            p = 1
        else:
            raise ValueError("unknown terrain")
        period = lcm(period, p)
        if period > max_period:
            raise ValueError("phase domain exceeds cap")
    return period

def screen_section(rows, horizon=64, reaction_ticks=0,
                   entry_columns=(5,), max_period=256,
                   grace_ticks=100, pressure_interval=20,
                   initial_boundary=-3):
    """Return an explicit evidence record; never silently sample phases."""
    if not rows or rows[0].kind != GRASS or rows[-1].kind != GRASS:
        raise ValueError("section must start and end with grass")
    if any(row.index != rows[0].index + i for i, row in enumerate(rows)):
        raise ValueError("noncontiguous section")
    danger = 0
    for row in rows:
        danger = 0 if row.kind == GRASS else danger + 1
        if danger > MAX_DANGER_RUN:
            raise ValueError("danger run too long")
    period = phase_period(rows, max_period)
    result = validate_camera(
        rows, entry_columns=entry_columns,
        entry_phases=range(period), horizon=horizon,
        reaction_ticks=reaction_ticks, grace_ticks=grace_ticks,
        pressure_interval=pressure_interval,
        initial_boundary=initial_boundary)
    return {"passed": bool(result), "phases_checked": period,
            "horizon": horizon, "reaction_ticks": reaction_ticks,
            "entry_columns": tuple(entry_columns),
            "model": "camera-validator-fp-prototype-v1"}
