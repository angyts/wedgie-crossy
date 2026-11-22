"""Compact immutable-by-convention row parameters; no hardware imports."""
WIDTH = 12
GRASS, ROAD, RIVER, RAIL = range(4)
KINDS = (GRASS, ROAD, RIVER, RAIL)
MAX_DANGER_RUN = 5

class Row:
    __slots__ = ("index", "kind", "direction", "speed", "spacing",
                 "length", "phase", "period", "warning", "trees")

    def __init__(self, index, kind, direction=0, speed=0, spacing=0,
                 length=0, phase=0, period=0, warning=0, trees=0):
        self.index = index
        self.kind = kind
        self.direction = direction
        self.speed = speed
        self.spacing = spacing
        self.length = length
        self.phase = phase
        self.period = period
        self.warning = warning
        self.trees = trees
        self.validate()

    def validate(self):
        if not isinstance(self.index, int) or self.index < 0 or self.kind not in KINDS:
            raise ValueError("invalid row")
        if self.kind == GRASS:
            if any((self.direction, self.speed, self.spacing, self.length,
                    self.phase, self.period, self.warning)):
                raise ValueError("grass has no moving hazards")
            if not 0 <= self.trees < (1 << WIDTH):
                raise ValueError("invalid tree mask")
        else:
            if self.trees or self.direction not in (-1, 1):
                raise ValueError("invalid hazard direction/trees")
            if not (1 <= self.speed <= 8 and 1 <= self.length <= WIDTH):
                raise ValueError("invalid speed/length")
            if self.kind == RAIL:
                if self.spacing or not (self.length < self.period <= 4096):
                    raise ValueError("invalid train period")
                if not (1 <= self.warning < self.period - self.length):
                    raise ValueError("invalid warning")
                if not 0 <= self.phase < self.period:
                    raise ValueError("invalid phase")
            else:
                if self.period or self.warning:
                    raise ValueError("non-rail has train parameters")
                if not self.length < self.spacing <= 64:
                    raise ValueError("invalid spacing")
                if not 0 <= self.phase < self.spacing:
                    raise ValueError("invalid phase")

    def signature(self):
        return (self.index, self.kind, self.direction, self.speed,
                self.spacing, self.length, self.phase, self.period,
                self.warning, self.trees)
