import unittest
from crossy_core.patterns import Row, GRASS, ROAD, RIVER, RAIL
from crossy_core.physics import SUBTILE
from crossy_core.simulation_fp import step_fp

class FixedPointSimulationTests(unittest.TestCase):
    def test_grass_move(self):
        rows = [Row(0, GRASS), Row(1, GRASS)]
        self.assertEqual(step_fp(rows, (0, 5*SUBTILE), 0, (1, 0)),
                         (1, 5*SUBTILE))

    def test_tree_blocks_without_killing(self):
        rows = [Row(0, GRASS), Row(1, GRASS, trees=1 << 5)]
        self.assertEqual(step_fp(rows, (0, 5*SUBTILE), 0, (1, 0)),
                         (0, 5*SUBTILE))

    def test_road_sweep(self):
        rows = [Row(0, GRASS), Row(1, ROAD, direction=1,
                                   speed=8, spacing=12, length=4)]
        self.assertIsNone(step_fp(rows, (0, 5*SUBTILE), 0, (1, 0)))

    def test_river_carry(self):
        rows = [Row(0, GRASS), Row(1, RIVER, direction=1,
                                   speed=1, spacing=12, length=4, phase=3)]
        self.assertEqual(step_fp(rows, (0, 5*SUBTILE), 0, (1, 0)),
                         (1, 6*SUBTILE))

    def test_river_unsupported(self):
        rows = [Row(0, GRASS), Row(1, RIVER, direction=1,
                                   speed=1, spacing=12, length=2, phase=0)]
        self.assertIsNone(step_fp(rows, (0, 5*SUBTILE), 0, (1, 0)))

    def test_river_edge_death(self):
        rows = [Row(0, GRASS), Row(1, RIVER, direction=1,
                                   speed=2, spacing=12, length=3, phase=10)]
        self.assertIsNone(step_fp(rows, (0, 11*SUBTILE), 0, (1, 0)))

    def test_rail_clear_entry(self):
        rows = [Row(0, GRASS), Row(1, RAIL, direction=1, speed=2,
                                   length=3, period=30, warning=4)]
        self.assertEqual(step_fp(rows, (0, 5*SUBTILE), 15, (1, 0)),
                         (1, 5*SUBTILE))

    def test_rail_warning_blocks_entry(self):
        rows = [Row(0, GRASS), Row(1, RAIL, direction=1, speed=2,
                                   length=3, period=30, warning=4)]
        self.assertIsNone(step_fp(rows, (0, 5*SUBTILE), 27, (1, 0)))

    def test_rail_swept_collision(self):
        rows = [Row(0, GRASS), Row(1, RAIL, direction=1, speed=8,
                                   length=3, period=30, warning=4)]
        self.assertIsNone(step_fp(rows, (0, 2*SUBTILE), 0, (1, 0)))

    def test_rail_invalid_schedule(self):
        rows = [Row(0, GRASS), Row(1, RAIL, direction=1, speed=1,
                                   length=3, period=12, warning=3)]
        with self.assertRaises(ValueError):
            step_fp(rows, (0, 5*SUBTILE), 0, (1, 0))

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            step_fp([Row(0, GRASS)], (0, 5*SUBTILE), -1, (0, 0))
        with self.assertRaises(ValueError):
            step_fp([Row(0, GRASS)], (0, 5*SUBTILE), 0, (2, 0))

if __name__ == "__main__":
    unittest.main()
