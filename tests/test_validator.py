import unittest
from crossy_core.patterns import Row, GRASS, ROAD, RIVER, RAIL
from crossy_core.validator import occupied, validate

class ValidatorPrototypeTests(unittest.TestCase):
    def test_clear_grass(self):
        rows = [Row(i, GRASS) for i in range(4)]
        self.assertTrue(validate(rows, horizon=4))

    def test_blocked_join(self):
        rows = [Row(0, GRASS), Row(1, GRASS, trees=(1 << 12) - 1),
                Row(2, GRASS)]
        self.assertFalse(validate(rows))

    def test_blocked_entry(self):
        self.assertFalse(validate([Row(0, GRASS, trees=1 << 5),
                                   Row(1, GRASS)]))

    def test_periodic_road_and_river(self):
        road = Row(1, ROAD, direction=1, speed=1, spacing=8, length=2)
        river = Row(2, RIVER, direction=-1, speed=1, spacing=8, length=3)
        self.assertTrue(occupied(road, 0, 0))
        self.assertFalse(occupied(road, 3, 0))
        self.assertFalse(occupied(river, 0, 0))
        self.assertTrue(occupied(river, 4, 0))
        self.assertEqual(occupied(road, 0, 0), occupied(road, 0, 8))

    def test_train_phase(self):
        train = Row(1, RAIL, direction=1, speed=2, length=3,
                    period=12, warning=4, phase=0)
        self.assertTrue(occupied(train, 5, 0))
        self.assertTrue(occupied(train, 5, 2))
        self.assertFalse(occupied(train, 5, 3))
        self.assertTrue(occupied(train, 5, 12))

    def test_phase_sensitive_join(self):
        rows = [Row(0, GRASS),
                Row(1, RAIL, direction=1, speed=1, length=2,
                    period=8, warning=2),
                Row(2, GRASS)]
        self.assertTrue(validate(rows, horizon=8, entry_phases=(0, 1, 2, 3)))

    def test_reject_bad_input(self):
        with self.assertRaises(ValueError):
            validate([])
        with self.assertRaises(ValueError):
            validate([Row(0, GRASS), Row(2, GRASS)])

if __name__ == "__main__":
    unittest.main()
