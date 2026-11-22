import unittest
from crossy_core.prng import PRNG, MASK
from crossy_core.patterns import Row, GRASS, ROAD, RIVER, RAIL, MAX_DANGER_RUN
from crossy_core.world import World, difficulty

class FoundationTests(unittest.TestCase):
    def test_seed_replay(self):
        a, b = World(0), World(0)
        for i in range(10000):
            a.advance_to(i)
            b.advance_to(i)
            self.assertEqual(a.get(i).signature(), b.get(i).signature())

    def test_prng_range_and_zero(self):
        self.assertEqual(PRNG(0).next_u32(), PRNG(0).next_u32())
        for limit in (1, 2, 3, 17, 256, 65537, 1 << 32):
            rng = PRNG(MASK)
            for _ in range(500):
                self.assertTrue(0 <= rng.below(limit) < limit)
        for seed in (-1, MASK + 1):
            with self.assertRaises(ValueError):
                PRNG(seed)

    def test_invalid_rows(self):
        cases = [
            dict(index=-1, kind=GRASS),
            dict(index=1, kind=GRASS, trees=1 << 12),
            dict(index=1, kind=ROAD, direction=0, speed=1, spacing=8, length=2),
            dict(index=1, kind=RIVER, direction=1, speed=1, spacing=2, length=2),
            dict(index=1, kind=RAIL, direction=1, speed=2, length=3, period=10, warning=7),
        ]
        for case in cases:
            with self.assertRaises(ValueError):
                Row(**case)

    def test_bounded_window_and_difficulty(self):
        w = World(123)
        kinds = set()
        longest = 0
        for i in range(10000):
            w.advance_to(i)
            row = w.get(i)
            kinds.add(row.kind)
            longest = longest + 1 if row.kind != GRASS else 0
            self.assertLessEqual(longest, MAX_DANGER_RUN)
            self.assertLessEqual(w.next_index - w.first, w.window)
        self.assertEqual(kinds, {GRASS, ROAD, RIVER, RAIL})
        with self.assertRaises(IndexError):
            w.get(0)
        self.assertEqual(difficulty(1000000), 200)

    def test_million_rows(self):
        w = World(20261122)
        for i in range(1000000):
            w.advance_to(i)
        self.assertEqual(w.next_index, 1000000)
        self.assertEqual(w.first, 1000000 - w.window)
        self.assertEqual(w.get(999999).index, 999999)
        self.assertEqual(len(w.rows), w.window)

if __name__ == "__main__":
    unittest.main()
