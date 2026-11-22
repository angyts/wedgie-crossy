"""Deterministic rising danger boundary, measured in simulation ticks.

Rows increase in the forward direction. The boundary starts behind row 0.
Only a new furthest row resets the inactivity clock. After the grace
period, the boundary advances one row every pressure_interval ticks.
This is a proposed game rule, not a physical-device timing measurement.
"""

class Camera:
    def __init__(self, grace_ticks=100, pressure_interval=20,
                 initial_boundary=-3):
        if (type(grace_ticks) is not int or grace_ticks < 0
                or type(pressure_interval) is not int or pressure_interval < 1
                or type(initial_boundary) is not int
                or initial_boundary >= 0):
            raise ValueError("invalid camera parameters")
        self.grace_ticks = grace_ticks
        self.pressure_interval = pressure_interval
        self.initial_boundary = initial_boundary
        self.reset()

    def reset(self):
        self.best_row = 0
        self.last_progress_tick = 0
        self.boundary = self.initial_boundary

    def update(self, row, tick):
        if type(row) is not int or row < 0 or type(tick) is not int or tick < 0:
            raise ValueError("invalid row/tick")
        if tick < self.last_progress_tick:
            raise ValueError("tick moved backwards")
        if row > self.best_row:
            self.best_row = row
            self.last_progress_tick = tick
        elapsed = tick - self.last_progress_tick
        if elapsed > self.grace_ticks:
            # Absolute boundary formula avoids frame-dependent drift.
            advance = (elapsed - self.grace_ticks - 1) // self.pressure_interval + 1
            candidate = self.initial_boundary + advance
            if candidate > self.boundary:
                self.boundary = candidate
        return row <= self.boundary

    def clone(self):
        other = Camera(self.grace_ticks, self.pressure_interval,
                       self.initial_boundary)
        other.best_row = self.best_row
        other.last_progress_tick = self.last_progress_tick
        other.boundary = self.boundary
        return other
