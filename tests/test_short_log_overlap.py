"""Adjacent short logs overlap at phase zero."""
import unittest
import crossy_worldgen as w

class ShortLogOverlapTests(unittest.TestCase):
    def test_adjacent_entry_overlap(self):
        for seed in range(100):
            for block in range(20):
                first = 8 + block * w.BLOCK
                kind, _, width = w.section(seed, first)
                if kind != "logs":
                    continue
                for row in range(first, first + width - 1):
                    self.assertTrue(
                        w.log_mask(seed, row, 0) & w.log_mask(seed, row + 1, 0),
                        (seed, row))
