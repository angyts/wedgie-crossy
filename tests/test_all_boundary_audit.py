import unittest
from crossy_core.all_boundary_audit import audit_all_boundaries
from crossy_core.patterns import Row, GRASS, ROAD

class AllBoundaryAuditTests(unittest.TestCase):
    def test_three_open_sections(self):
        sections = ((Row(0, GRASS), Row(1, GRASS)),
                    (Row(2, GRASS), Row(3, GRASS)),
                    (Row(4, GRASS),))
        result = audit_all_boundaries(sections, horizon=4,
                                      continuation_horizon=4)
        self.assertTrue(result["passed"])
        self.assertEqual(result["boundaries_checked"], 2)
        self.assertEqual([r["boundary_index"] for r in result["results"]],
                         [0, 1])
        self.assertFalse(result["deployable"])

    def test_later_blocked_boundary(self):
        sections = ((Row(0, GRASS), Row(1, GRASS)),
                    (Row(2, GRASS), Row(3, GRASS)),
                    (Row(4, GRASS, trees=(1 << 12)-1), Row(5, GRASS)))
        result = audit_all_boundaries(sections, horizon=5,
                                      continuation_horizon=5)
        self.assertFalse(result["passed"])
        self.assertTrue(any(not r["passed"] for r in result["results"]))

    def test_phase_cap_fails_closed(self):
        sections = ((Row(0, GRASS),),
                    (Row(1, ROAD, direction=1, speed=1,
                         spacing=12, length=2), Row(2, GRASS)))
        with self.assertRaises(ValueError):
            audit_all_boundaries(sections, max_period=4)

    def test_invalid_sections(self):
        with self.assertRaises(ValueError):
            audit_all_boundaries(())
        with self.assertRaises(ValueError):
            audit_all_boundaries(((Row(0, GRASS),),))

    def test_two_sections_one_boundary(self):
        sections = ((Row(0, GRASS),), (Row(1, GRASS),))
        result = audit_all_boundaries(sections, horizon=2,
                                      continuation_horizon=2)
        self.assertEqual(result["boundaries_checked"], 1)
        self.assertTrue(result["passed"])

if __name__ == "__main__":
    unittest.main()
