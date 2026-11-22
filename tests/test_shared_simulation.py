import unittest
from crossy_core.patterns import Row, GRASS, ROAD, RIVER
from crossy_core.simulation import step
from crossy_core.shared_validator import validate_shared

class SharedSimulationTests(unittest.TestCase):
    def test_movement_and_trees(self):
        rows = [Row(0, GRASS), Row(1, GRASS, trees=1 << 5)]
        self.assertIsNone(step(rows, (0, 5), 0, (1, 0)))
        self.assertEqual(step(rows, (0, 5), 0, (0, 1)), (0, 6))

    def test_swept_collision(self):
        rows = [Row(0, GRASS),
                Row(1, ROAD, direction=1, speed=8, spacing=12, length=4)]
        self.assertIsNone(step(rows, (0, 5), 0, (1, 0)))

    def test_open_route(self):
        rows = [Row(i, GRASS) for i in range(3)]
        self.assertTrue(validate_shared(rows, horizon=2))
        self.assertFalse(validate_shared(rows, horizon=1))

    def test_blocked_join(self):
        rows = [Row(0, GRASS), Row(1, GRASS, trees=(1 << 12)-1),
                Row(2, GRASS)]
        self.assertFalse(validate_shared(rows, horizon=20))

    def test_reaction_delay(self):
        rows = [Row(i, GRASS) for i in range(3)]
        self.assertTrue(validate_shared(rows, horizon=4, reaction_ticks=2))
        self.assertFalse(validate_shared(rows, horizon=3, reaction_ticks=2))

    def test_unsupported_terrain(self):
        rows = [Row(0, GRASS),
                Row(1, RIVER, direction=1, speed=1, spacing=8, length=3)]
        with self.assertRaises(NotImplementedError):
            validate_shared(rows)

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            validate_shared([])
        with self.assertRaises(ValueError):
            step([Row(0, GRASS)], (0, 5), 0, (2, 0))

if __name__ == "__main__":
    unittest.main()
