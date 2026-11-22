"""Bounded scrolling and reproducible grass world invariants."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "crossy.py"

def load():
    lcd = types.ModuleType("lcd")
    lcd.LCD = object
    lcd.Keys = object
    lcd.color = lambda r,g,b: (r,g,b)
    old = sys.modules.get("lcd")
    try:
        sys.modules["lcd"] = lcd
        spec = importlib.util.spec_from_file_location("crossy_world_tests", APP)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if old is None:
            sys.modules.pop("lcd", None)
        else:
            sys.modules["lcd"] = old

class EndlessGrassTests(unittest.TestCase):
    def test_seed_replay_and_clear_corridor(self):
        m = load()
        for row in range(10000):
            self.assertEqual(m.row_mask(123, row), m.row_mask(123, row))
            self.assertFalse(m.row_mask(123, row) & (1 << m.START_COL))
            self.assertLessEqual(m.row_mask(123, row), m.MASK_ALL)

    def test_bounded_million_rows(self):
        m = load()
        world = m.World(123)
        for row in range(1, 1000001):
            world.advance(row)
        self.assertEqual(len(world.rows), 12)
        self.assertEqual(world.last - world.first + 1, 12)
        self.assertEqual(world.mask(world.last), m.row_mask(123, world.last))
        self.assertIsNone(world.mask(0))

    def test_blocking_and_reset(self):
        m = load()
        world = m.World(123)
        self.assertEqual(m.move_world(world, 5, 0, "up"), (5, 1))
        self.assertEqual(m.move_world(world, 5, 0, "down"), (5, 0))
        world.advance(20)
        self.assertEqual(m.move_world(world, 5, 20, "down"), (5, 20))
        reset = m.World(123)
        self.assertEqual(reset.first, 0)
        self.assertEqual(reset.mask(9), m.row_mask(123, 9))

if __name__ == "__main__":
    unittest.main()
