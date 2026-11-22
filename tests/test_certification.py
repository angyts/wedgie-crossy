import unittest
from crossy_core.patterns import Row, GRASS, ROAD, RIVER, RAIL
from crossy_core.certification import phase_period, screen_section

class CertificationScreenTests(unittest.TestCase):
    def test_grass_all_phases(self):
        rows = [Row(i, GRASS) for i in range(3)]
        evidence = screen_section(rows, horizon=4, reaction_ticks=1)
        self.assertTrue(evidence["passed"])
        self.assertEqual(evidence["phases_checked"], 1)

    def test_blocked_section(self):
        rows = [Row(0, GRASS), Row(1, GRASS, trees=(1 << 12)-1),
                Row(2, GRASS)]
        self.assertFalse(screen_section(rows, horizon=10)["passed"])

    def test_road_period(self):
        rows = [Row(0, GRASS),
                Row(1, ROAD, direction=1, speed=2, spacing=8, length=2),
                Row(2, GRASS)]
        self.assertEqual(phase_period(rows), 4)

    def test_mixed_period(self):
        rows = [Row(0, GRASS),
                Row(1, ROAD, direction=1, speed=2, spacing=8, length=2),
                Row(2, RIVER, direction=-1, speed=1, spacing=9, length=3),
                Row(3, GRASS)]
        self.assertEqual(phase_period(rows), 36)

    def test_phase_cap_fails_closed(self):
        rows = [Row(0, GRASS),
                Row(1, ROAD, direction=1, speed=1, spacing=11, length=2),
                Row(2, RIVER, direction=1, speed=1, spacing=13, length=3),
                Row(3, GRASS)]
        with self.assertRaises(ValueError):
            screen_section(rows, max_period=100)

    def test_bad_train_schedule_rejected(self):
        rows = [Row(0, GRASS),
                Row(1, RAIL, direction=1, speed=1, length=3,
                    period=12, warning=3),
                Row(2, GRASS)]
        with self.assertRaises(ValueError):
            screen_section(rows)

    def test_camera_rejects_long_reaction(self):
        rows = [Row(i, GRASS) for i in range(4)]
        evidence = screen_section(rows, horizon=12, reaction_ticks=5,
                                  grace_ticks=1, pressure_interval=1,
                                  initial_boundary=-1)
        self.assertFalse(evidence["passed"])

    def test_noncontiguous_rejected(self):
        with self.assertRaises(ValueError):
            screen_section([Row(0, GRASS), Row(2, GRASS)])

    def test_danger_limit_rejected(self):
        rows = [Row(0, GRASS)] + [
            Row(i, ROAD, direction=1, speed=1, spacing=8, length=2)
            for i in range(1, 7)] + [Row(7, GRASS)]
        with self.assertRaises(ValueError):
            screen_section(rows)

if __name__ == "__main__":
    unittest.main()
