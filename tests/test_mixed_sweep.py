"""Fast deterministic smoke tests for the large-scale sweep driver."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import sweep_mixed_terrain as sweep


class MixedSweepTests(unittest.TestCase):
    def test_small_sweep_is_deterministic(self):
        a = sweep.sweep(seeds=2, phases=2, ticks=32, blocks=2)
        b = sweep.sweep(seeds=2, phases=2, ticks=32, blocks=2)
        self.assertEqual(a["total_cases"], 12)
        self.assertEqual(a["total_cases"],
                         a["witness_cases"] + a["no_witness_cases"])
        self.assertEqual(a["bands"], b["bands"])
        self.assertEqual(a["failure_examples"], b["failure_examples"])
        self.assertFalse(a["certifies_human_fairness"])
        self.assertFalse(a["live_terrain_enabled"])

    def test_invalid_parameters(self):
        for kwargs in ({"seeds": 0}, {"phases": 0}, {"ticks": 0},
                       {"blocks": 0}, {"max_failures": -1}):
            with self.assertRaises(ValueError):
                sweep.sweep(**kwargs)

    def test_failure_capture_bound(self):
        result = sweep.sweep(seeds=2, phases=1, ticks=1, max_failures=2)
        self.assertEqual(result["no_witness_cases"], 6)
        self.assertLessEqual(len(result["failure_examples"]), 2)
        self.assertTrue(result["failures_truncated"])


if __name__ == "__main__":
    unittest.main()
