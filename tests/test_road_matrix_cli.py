import unittest
from scripts.audit_road_matrix import CONFIGURATIONS, run

class RoadMatrixCLITests(unittest.TestCase):
    def test_matrix_has_unique_configurations(self):
        self.assertEqual(len(CONFIGURATIONS), len(set(CONFIGURATIONS)))
        self.assertEqual(len(CONFIGURATIONS), 8)

    def test_matrix_records_outcomes(self):
        report = run(horizon=5)
        self.assertEqual(report["cases"], 8)
        self.assertEqual(report["passed"] + report["failed"], 8)
        self.assertFalse(report["deployable"])
        self.assertTrue(all("boundary_failures" in r for r in report["reports"]))

    def test_invalid_period_cap_fails_closed(self):
        with self.assertRaises(ValueError):
            run(horizon=5, max_period=1)

if __name__ == "__main__":
    unittest.main()
