"""Fail-closed experimental generator using an explicit reviewed allowlist.

Only a straight, tree-free grass corridor is approved here. This is a
safe baseline for integrating the generator gate, NOT the intended
multi-terrain game or a universal fairness certification.
"""
from .patterns import Row, GRASS, WIDTH
from .prng import PRNG

APPROVAL_VERSION = 1
CORRIDOR = 5
WINDOW = 30

def approved_row(index, rng):
    """Generate only a reviewed baseline row; no arbitrary hazards."""
    if type(index) is not int or index < 0:
        raise ValueError("invalid row index")
    # Decorative trees never occupy the fixed corridor or its neighbors.
    allowed = ((1 << WIDTH) - 1) & ~sum(1 << c for c in (4, 5, 6))
    trees = rng.below(1 << WIDTH) & allowed
    return Row(index, GRASS, trees=trees)

class ApprovedWorld:
    def __init__(self, seed, window=WINDOW):
        if type(window) is not int or not 12 <= window <= 64:
            raise ValueError("invalid window")
        self.rng = PRNG(seed)
        self.window = window
        self.rows = [None] * window
        self.next_index = 0
        self.first = 0

    def advance_to(self, index):
        if type(index) is not int or index < self.next_index - 1:
            raise ValueError("cannot rewind")
        while self.next_index <= index:
            row = approved_row(self.next_index, self.rng)
            self.rows[self.next_index % self.window] = row
            self.next_index += 1
            self.first = max(0, self.next_index - self.window)

    def get(self, index):
        if not self.first <= index < self.next_index:
            raise IndexError("outside active window")
        return self.rows[index % self.window]

def assert_approved(rows):
    """Reject all unknown terrain/trees in the protected corridor."""
    if not rows:
        raise ValueError("empty section")
    for i, row in enumerate(rows):
        if row.kind != GRASS or row.trees & (1 << CORRIDOR):
            raise ValueError("unapproved terrain")
        if i and row.index != rows[i-1].index + 1:
            raise ValueError("noncontiguous section")
    return True
