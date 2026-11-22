"""Seeded log lanes must vary while retaining initial transfer overlap."""
import unittest
import crossy_worldgen as w
import reachability as r

class LogAlignmentTests(unittest.TestCase):
    def test_seed_2647d06d(self):
        seed = int("2647D06D", 16)
        block = (59 - 8) // w.BLOCK
        self.assertEqual(w.section(seed, 8 + block * w.BLOCK)[0], "logs")
        possible, tick = r.crossing_possible(seed, block)
        self.assertTrue(possible, (seed, block, tick))

    def test_adjacent_lanes_vary_but_overlap_at_entry(self):
        different = 0
        same_direction = 0
        opposite_direction = 0
        for seed in range(100):
            for block in range(20):
                start = 8 + block * w.BLOCK
                kind, _, width = w.section(seed, start)
                if kind != "logs":
                    continue
                for row in range(start, start + width - 1):
                    a = w.log_mask(seed, row, 0)
                    b = w.log_mask(seed, row + 1, 0)
                    self.assertTrue(a & b)
                    if a != b:
                        different += 1
                    if w.log_direction(seed, row) == w.log_direction(seed, row + 1):
                        same_direction += 1
                    else:
                        opposite_direction += 1
        self.assertGreater(different, 0)
        self.assertGreater(same_direction, 0)
        self.assertGreater(opposite_direction, 0)
