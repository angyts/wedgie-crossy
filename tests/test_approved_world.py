import unittest
from crossy_core.approved_world import (
    ApprovedWorld, assert_approved, CORRIDOR,
)
from crossy_core.patterns import Row, GRASS, ROAD
from crossy_core.camera_validator import validate_camera

class ApprovedWorldTests(unittest.TestCase):
    def test_reproducible(self):
        a, b = ApprovedWorld(42), ApprovedWorld(42)
        for i in range(1000):
            a.advance_to(i)
            b.advance_to(i)
            self.assertEqual(a.get(i).signature(), b.get(i).signature())

    def test_bounded(self):
        w = ApprovedWorld(0)
        w.advance_to(100000)
        self.assertEqual(len(w.rows), 30)
        self.assertEqual(w.first, 99971)
        self.assertEqual(w.get(100000).index, 100000)

    def test_corridor_stays_open(self):
        w = ApprovedWorld(123)
        for i in range(10000):
            w.advance_to(i)
            self.assertEqual(w.get(i).kind, GRASS)
            self.assertFalse(w.get(i).trees & (1 << CORRIDOR))

    def test_screened_join(self):
        w = ApprovedWorld(99)
        w.advance_to(5)
        rows = [w.get(i) for i in range(6)]
        self.assertTrue(assert_approved(rows))
        self.assertTrue(validate_camera(rows, horizon=8))

    def test_reject_road_and_blocked_corridor(self):
        with self.assertRaises(ValueError):
            assert_approved([Row(0, GRASS),
                Row(1, ROAD, direction=1, speed=1, spacing=8, length=2)])
        with self.assertRaises(ValueError):
            assert_approved([Row(0, GRASS, trees=1 << CORRIDOR)])

    def test_reject_gap_and_empty(self):
        with self.assertRaises(ValueError):
            assert_approved([])
        with self.assertRaises(ValueError):
            assert_approved([Row(0, GRASS), Row(2, GRASS)])

if __name__ == "__main__":
    unittest.main()
