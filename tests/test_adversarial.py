import unittest
from crossy_core.adversarial import sweep_join
from crossy_core.patterns import Row, GRASS, ROAD, RIVER, RAIL

class AdversarialTests(unittest.TestCase):
    def test_open_grass_all_phases(self):
        sections = [[Row(0, GRASS), Row(1, GRASS)],
                    [Row(2, GRASS), Row(3, GRASS)]]
        e = sweep_join(sections, horizon=4)
        self.assertTrue(e["passed"])
        self.assertEqual(e["phases_checked"], 1)
        self.assertEqual(e["failing_phases"], ())
        self.assertFalse(e["deployable"])

    def test_blocked_join_fails(self):
        sections = [[Row(0, GRASS), Row(1, GRASS)],
                    [Row(2, GRASS, trees=(1 << 12)-1),
                     Row(3, GRASS)]]
        e = sweep_join(sections, horizon=10)
        self.assertFalse(e["passed"])
        self.assertEqual(e["failing_phases"], (0,))

    def test_road_phase_domain(self):
        sections = [[Row(0, GRASS),
                     Row(1, ROAD, direction=1, speed=2,
                         spacing=8, length=2)],
                    [Row(2, GRASS)]]
        e = sweep_join(sections, horizon=8)
        self.assertEqual(e["phases_checked"], 4)
        self.assertEqual(e["deployable"], False)

    def test_river_phase_domain(self):
        sections = [[Row(0, GRASS),
                     Row(1, RIVER, direction=1, speed=1,
                         spacing=12, length=6, phase=3)],
                    [Row(2, GRASS)]]
        e = sweep_join(sections, horizon=8)
        self.assertEqual(e["phases_checked"], 12)

    def test_rail_phase_domain(self):
        sections = [[Row(0, GRASS),
                     Row(1, RAIL, direction=1, speed=2,
                         length=3, period=30, warning=4)],
                    [Row(2, GRASS)]]
        e = sweep_join(sections, horizon=8)
        self.assertEqual(e["phases_checked"], 30)

    def test_excessive_domain_rejected(self):
        sections = [[Row(0, GRASS),
                     Row(1, ROAD, direction=1, speed=1,
                         spacing=11, length=2)],
                    [Row(2, RIVER, direction=1, speed=1,
                         spacing=13, length=3), Row(3, GRASS)]]
        with self.assertRaises(ValueError):
            sweep_join(sections, max_period=100)

    def test_camera_pressure_rejects(self):
        sections = [[Row(0, GRASS), Row(1, GRASS)],
                    [Row(2, GRASS), Row(3, GRASS)]]
        e = sweep_join(sections, horizon=12, reaction_ticks=5,
                       grace_ticks=1, pressure_interval=1,
                       initial_boundary=-1)
        self.assertFalse(e["passed"])

if __name__ == "__main__":
    unittest.main()
