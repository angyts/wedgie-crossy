import unittest
from crossy_core.phase_successors import audit_successors
from crossy_core.all_boundary_audit import audit_all_boundaries
from crossy_core.patterns import Row, GRASS

class TotalBudgetTests(unittest.TestCase):
    def setUp(self):
        self.sections = ((Row(0, GRASS), Row(1, GRASS)),
                         (Row(2, GRASS), Row(3, GRASS)))

    def test_enough_total_ticks(self):
        result = audit_successors(self.sections, horizon=3,
            continuation_horizon=3, total_horizon=6)
        self.assertTrue(result["passed"])
        self.assertEqual(result["total_horizon"], 6)

    def test_late_boundary_state_fails_deadline(self):
        result = audit_successors(self.sections, horizon=4,
            continuation_horizon=4, total_horizon=3)
        self.assertFalse(result["passed"])
        self.assertIn((0, "no-continuation-for-some-states"),
                      result["failures"])

    def test_all_boundaries_use_same_deadline(self):
        result = audit_all_boundaries(self.sections, horizon=4,
            continuation_horizon=4, total_horizon=3)
        self.assertFalse(result["passed"])
        self.assertEqual(result["results"][0]["total_horizon"], 3)

    def test_invalid_budget_rejected(self):
        with self.assertRaises(ValueError):
            audit_successors(self.sections, total_horizon=0)
        with self.assertRaises(ValueError):
            audit_successors(self.sections, total_horizon=True)

if __name__ == "__main__":
    unittest.main()
