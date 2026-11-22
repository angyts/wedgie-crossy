import unittest
from crossy_core.phase_successors import audit_successors
from crossy_core.patterns import Row, GRASS, ROAD

class PhaseSuccessorTests(unittest.TestCase):
    def test_open_grass(self):
        sections = ((Row(0, GRASS), Row(1, GRASS)),
                    (Row(2, GRASS), Row(3, GRASS)))
        result = audit_successors(sections, horizon=3,
                                  continuation_horizon=3)
        self.assertTrue(result["passed"])
        self.assertEqual(result["phases_checked"], 1)
        self.assertGreater(result["states_checked"], 0)
        self.assertFalse(result["deployable"])

    def test_blocked_successor(self):
        sections = ((Row(0, GRASS), Row(1, GRASS)),
                    (Row(2, GRASS, trees=(1 << 12)-1), Row(3, GRASS)))
        result = audit_successors(sections, horizon=3,
                                  continuation_horizon=3)
        self.assertFalse(result["passed"])
        self.assertTrue(result["failures"])

    def test_road_phase_domain(self):
        sections = ((Row(0, GRASS),),
                    (Row(1, ROAD, direction=1, speed=2,
                         spacing=8, length=2), Row(2, GRASS)))
        result = audit_successors(sections, horizon=2,
                                  continuation_horizon=3)
        self.assertEqual(result["phases_checked"], 4)
        self.assertFalse(result["deployable"])

    def test_phase_cap_rejected(self):
        sections = ((Row(0, GRASS),),
                    (Row(1, ROAD, direction=1, speed=1,
                         spacing=12, length=2), Row(2, GRASS)))
        with self.assertRaises(ValueError):
            audit_successors(sections, max_period=4)

    def test_missing_boundary_fails_closed(self):
        sections = ((Row(0, GRASS), Row(1, GRASS, trees=(1 << 12)-1)),
                    (Row(2, GRASS),))
        self.assertFalse(audit_successors(sections, horizon=2)["passed"])

    def test_invalid_bounds(self):
        sections = ((Row(0, GRASS),), (Row(1, GRASS),))
        with self.assertRaises(ValueError):
            audit_successors(sections, boundary_index=1)
        with self.assertRaises(ValueError):
            audit_successors(sections, max_states=0)

if __name__ == "__main__":
    unittest.main()
