import unittest
from crossy_core.patterns import Row, RAIL, ROAD
from crossy_core.physics import SUBTILE
from crossy_core.railway import (
    transit_ticks, check_schedule, warning_active,
    train_interval, train_collision,
)

def rail(direction=1, speed=2, phase=0, period=30, warning=4):
    return Row(1, RAIL, direction=direction, speed=speed,
               length=3, period=period, warning=warning, phase=phase)

class RailwayTests(unittest.TestCase):
    def test_transit_duration(self):
        self.assertEqual(transit_ticks(rail()), 8)

    def test_train_enters_from_left(self):
        self.assertEqual(train_interval(rail(), 0), (-3*SUBTILE, 0))
        self.assertTrue(train_collision(rail(), 0, 1))

    def test_train_enters_from_right(self):
        r = rail(direction=-1)
        self.assertEqual(train_interval(r, 0), (12*SUBTILE, 15*SUBTILE))
        self.assertTrue(train_collision(r, 11*SUBTILE, 1))

    def test_swept_tunneling(self):
        r = rail(speed=8)
        self.assertTrue(train_collision(r, 2*SUBTILE, 0))

    def test_warning_before_arrival(self):
        r = rail()
        self.assertTrue(warning_active(r, 26))
        self.assertFalse(warning_active(r, 25))
        self.assertFalse(warning_active(r, 0))

    def test_period_wrap(self):
        r = rail()
        self.assertEqual(train_interval(r, 0), train_interval(r, 30))
        self.assertTrue(train_collision(r, 0, 31))

    def test_safe_gap(self):
        r = rail()
        self.assertIsNone(train_interval(r, 15))
        self.assertFalse(train_collision(r, 5*SUBTILE, 15))

    def test_schedule_rejects_overlap(self):
        with self.assertRaises(ValueError):
            check_schedule(rail(period=12, warning=5))

    def test_wrong_terrain(self):
        r = Row(1, ROAD, direction=1, speed=1, spacing=8, length=2)
        with self.assertRaises(ValueError):
            transit_ticks(r)

if __name__ == "__main__":
    unittest.main()
