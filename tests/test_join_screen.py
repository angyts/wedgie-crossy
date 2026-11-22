import unittest
from crossy_core.patterns import Row, GRASS, ROAD, RAIL
from crossy_core.join_screen import screen_join

class JoinScreenTests(unittest.TestCase):
    def test_open_join(self):
        sections = [[Row(0, GRASS), Row(1, GRASS)],
                    [Row(2, GRASS), Row(3, GRASS)]]
        evidence = screen_join(sections, horizon=5)
        self.assertTrue(evidence["passed"])
        self.assertEqual(evidence["section_count"], 2)
        self.assertEqual(evidence["row_count"], 4)

    def test_blocked_boundary(self):
        sections = [[Row(0, GRASS), Row(1, GRASS)],
                    [Row(2, GRASS, trees=(1 << 12)-1),
                     Row(3, GRASS)]]
        self.assertFalse(screen_join(sections, horizon=10)["passed"])

    def test_phase_enumeration_across_join(self):
        sections = [[Row(0, GRASS),
                     Row(1, ROAD, direction=1, speed=2,
                         spacing=8, length=2)],
                    [Row(2, GRASS), Row(3, GRASS)]]
        self.assertEqual(screen_join(sections, horizon=20)["phases_checked"], 4)

    def test_invalid_schedule_fails_closed(self):
        sections = [[Row(0, GRASS)],
                    [Row(1, RAIL, direction=1, speed=1, length=3,
                         period=12, warning=3), Row(2, GRASS)]]
        with self.assertRaises(ValueError):
            screen_join(sections)

    def test_excessive_phase_domain_fails_closed(self):
        sections = [[Row(0, GRASS),
                     Row(1, ROAD, direction=1, speed=1,
                         spacing=11, length=2)],
                    [Row(2, ROAD, direction=1, speed=1,
                         spacing=13, length=2), Row(3, GRASS)]]
        with self.assertRaises(ValueError):
            screen_join(sections, max_period=100)

    def test_bad_boundary_indices(self):
        with self.assertRaises(ValueError):
            screen_join([[Row(0, GRASS)], [Row(2, GRASS)]])

    def test_camera_clock_crosses_boundary(self):
        sections = [[Row(0, GRASS), Row(1, GRASS)],
                    [Row(2, GRASS), Row(3, GRASS)]]
        self.assertFalse(screen_join(sections, horizon=12,
            reaction_ticks=5, grace_ticks=1,
            pressure_interval=1, initial_boundary=-1)["passed"])

if __name__ == "__main__":
    unittest.main()
