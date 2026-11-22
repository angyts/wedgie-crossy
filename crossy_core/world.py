"""Bounded sliding-window row generator. Fairness validation is NOT yet implemented."""
from .prng import PRNG
from .patterns import Row, WIDTH, GRASS, ROAD, RIVER, RAIL, MAX_DANGER_RUN

WINDOW = 30

def difficulty(row_index):
    return min(max(row_index, 0), 200)

class World:
    def __init__(self, seed, window=WINDOW):
        if not isinstance(window, int) or not 12 <= window <= 64:
            raise ValueError("window must be 12..64")
        self.rng = PRNG(seed)
        self.window = window
        self.rows = [None] * window
        self.first = 0
        self.next_index = 0
        self.danger_run = 0

    def _generate(self, index):
        if index < 3 or self.danger_run >= MAX_DANGER_RUN:
            kind = GRASS
        else:
            # Provisional candidates only: must pass offline time-aware validation
            kind = (GRASS, GRASS, ROAD, ROAD, RIVER, RAIL)[self.rng.below(6)]
        if kind == GRASS:
            self.danger_run = 0
            # Leave a guaranteed open corridor at column 5.
            mask = self.rng.below(1 << WIDTH) & ~(1 << 5)
            return Row(index, GRASS, trees=mask)
        self.danger_run += 1
        band = difficulty(index)
        speed = 1 + self.rng.below(2 + band // 50)
        direction = (-1, 1)[self.rng.below(2)]
        if kind == RAIL:
            length = 2 + self.rng.below(4)
            period = 24 + self.rng.below(24)
            return Row(index, kind, direction, speed, length=length,
                       phase=self.rng.below(period), period=period, warning=8)
        length = 2 + self.rng.below(3)
        spacing = length + 5 + self.rng.below(6)
        return Row(index, kind, direction, speed, spacing, length,
                   self.rng.below(spacing))

    def advance_to(self, index):
        """Generate through index, retaining only the latest window rows."""
        if not isinstance(index, int) or index < self.next_index - 1:
            raise ValueError("cannot rewind world")
        while self.next_index <= index:
            row = self._generate(self.next_index)
            self.rows[self.next_index % self.window] = row
            self.next_index += 1
            self.first = max(0, self.next_index - self.window)

    def get(self, index):
        if not self.first <= index < self.next_index:
            raise IndexError("row outside active window")
        return self.rows[index % self.window]
