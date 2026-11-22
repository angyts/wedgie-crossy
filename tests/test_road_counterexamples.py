import unittest
from crossy_core.road_counterexamples import inspect_roads, inspect_matrix
from crossy_core.approved_world import assert_approved
from crossy_core.patterns import Row, GRASS, ROAD

class RoadCounterexampleTests(unittest.TestCase):
    def test_report_contains_reproducible_configuration(self):
        report = inspect_roads(count=2, horizon=8)
        self.assertEqual(report["configuration"], (2, 2, 8, 2, 8))
        self.assertEqual(len(report["row_signatures"]), 5)
        self.assertFalse(report["deployable"])

    def test_report_has_boundary_diagnostics(self):
        report = inspect_roads(count=2, horizon=4)
        self.assertIsInstance(report["boundary_failures"], tuple)
        self.assertTrue(all(len(item) == 3 for item in
                            report["boundary_failures"]))

    def test_matrix_retains_order(self):
        reports = inspect_matrix(((1, 2, 8, 2), (2, 2, 8, 2)),
                                 horizon=6)
        self.assertEqual([r["configuration"][0] for r in reports], [1, 2])

    def test_invalid_matrix_rejected(self):
        with self.assertRaises(ValueError):
            inspect_matrix(())
        with self.assertRaises(ValueError):
            inspect_matrix(((2, 2, 8),))

    def test_phase_cap_fails_closed(self):
        with self.assertRaises(ValueError):
            inspect_roads(count=2, max_period=2)

    def test_no_runtime_approval(self):
        report = inspect_roads(count=1, horizon=4)
        self.assertFalse(report["deployable"])
        with self.assertRaises(ValueError):
            assert_approved([Row(0, GRASS),
                             Row(1, ROAD, direction=1, speed=2,
                                 spacing=8, length=2)])

if __name__ == "__main__":
    unittest.main()
