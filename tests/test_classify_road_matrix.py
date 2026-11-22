import unittest
from scripts.classify_road_matrix import run

class ClassifyRoadMatrixTests(unittest.TestCase):
    def test_eight_cases(self):
        report = run(horizon=4)
        self.assertEqual(report["cases"], 8)
        self.assertFalse(report["deployable"])
        self.assertEqual(len(report["reports"]), 8)

    def test_boundary_counts(self):
        report = run(horizon=4)
        for case in report["reports"]:
            self.assertEqual(len(case["boundaries"]),
                             case["configuration"][0])
            self.assertTrue(all(not b["deployable"]
                                for b in case["boundaries"]))

    def test_invalid_horizon(self):
        with self.assertRaises(ValueError):
            run(horizon=0)

    def test_phase_cap_rejected(self):
        with self.assertRaises(ValueError):
            run(horizon=4, max_period=1)

if __name__ == "__main__":
    unittest.main()
