"""Section joins must preserve the actual time and column across blocks."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import crossy_mixed_validator as v
import crossy_worldgen as w


class JoinedRouteTests(unittest.TestCase):
    def test_invalid_bounds(self):
        with self.assertRaises(ValueError):
            v.joined_route(1, 0, block_count=0)
        with self.assertRaises(ValueError):
            v.joined_route(1, 0, max_ticks=0)
        with self.assertRaises(ValueError):
            v.validate_joins(1, 0, phases=0)

    def test_joined_witness_replays_across_blocks(self):
        found = 0
        for seed in (0, 1, 2, 0x3F564588, 0x0676964C):
            for block in (0, 1):
                witness = v.joined_route(seed, block, 2, max_ticks=80)
                if witness is None:
                    continue
                moves, ending_phase, ending_col = witness
                final = v.replay_joined_route(seed, block, moves)
                self.assertIsNotNone(final)
                self.assertEqual(final[0], 8 + (block + 2) * w.BLOCK)
                self.assertEqual(final[1], ending_col)
                self.assertEqual(ending_phase, len(moves))
                found += 1
        self.assertGreater(found, 0)

    def test_phase_counts_and_reproducibility(self):
        for seed in (0x3F564588, 0x0676964C):
            result = v.validate_joins(seed, 0, phases=3, max_ticks=60)
            self.assertEqual(result, v.validate_joins(seed, 0, phases=3, max_ticks=60))
            self.assertTrue(0 <= result[0] <= result[1] == 3)

    def test_entry_column_is_respected(self):
        seed = 0x3F564588
        self.assertIsNone(v.joined_route(seed, 0, entry_columns=()))
        self.assertIsNone(v.replay_joined_route(seed, 0, (), entry_col=-1))


if __name__ == "__main__":
    unittest.main()
