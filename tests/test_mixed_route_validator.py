"""Deterministic tests for the offline mixed-terrain route model."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import crossy_mixed_validator as v


class MixedRouteTests(unittest.TestCase):
    def test_waiting_is_a_real_move(self):
        self.assertIn((0, 0), v.MOVES)
        self.assertNotIn((1, 1), v.MOVES)

    def test_road_collision_at_either_endpoint(self):
        for seed in (0, 1, 0x3F564588):
            for row in range(8, 30):
                if v.lane_kind(seed, row) != "road":
                    continue
                for phase in range(3):
                    mask = v.occupancy(seed, row, phase, "road")
                    for col in range(12):
                        if mask & (1 << col):
                            self.assertFalse(v.safe(seed, row, col, phase))

    def test_log_support_and_offscreen(self):
        seed = 0x0676964C
        for row in range(8, 80):
            if v.lane_kind(seed, row) != "logs":
                continue
            for phase in range(3):
                mask = v.occupancy(seed, row, phase, "logs")
                for col in range(12):
                    self.assertEqual(v.safe(seed, row, col, phase),
                                     bool(mask & (1 << col)))

    def test_reproducible_route_and_phase_report(self):
        for seed in (0x3F564588, 0x0676964C):
            for block in (0, 1, 2):
                first = v.route(seed, block, max_ticks=48)
                second = v.route(seed, block, max_ticks=48)
                self.assertEqual(first, second)
                if first is not None:
                    self.assertLessEqual(len(first), 48)
                successes, phases = v.validate(seed, block, phases=3, max_ticks=48)
                self.assertGreaterEqual(successes, 0)
                self.assertLessEqual(successes, phases)
                self.assertEqual(phases, 3)


if __name__ == "__main__":
    unittest.main()
