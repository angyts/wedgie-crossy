import unittest
from crossy_core.physics import (
    SUBTILE, BOARD_UNITS, periodic_overlap, swept_overlap,
    road_collision, carry_on_log,
)

class PhysicsTests(unittest.TestCase):
    def test_swept_vehicle_tunneling(self):
        # Starts left of player and ends right of player.
        self.assertFalse(periodic_overlap(4*SUBTILE, 5*SUBTILE,
                                          0, SUBTILE, 12*SUBTILE))
        self.assertFalse(periodic_overlap(4*SUBTILE, 5*SUBTILE,
                                          7*SUBTILE, SUBTILE, 12*SUBTILE))
        self.assertTrue(road_collision(4*SUBTILE, 0, 1, 12, 7*SUBTILE))

    def test_reverse_direction_tunneling(self):
        self.assertTrue(swept_overlap(4*SUBTILE, 5*SUBTILE,
                                      8*SUBTILE, SUBTILE,
                                      12*SUBTILE, -7*SUBTILE))

    def test_wrap_collision(self):
        self.assertTrue(swept_overlap(0, SUBTILE, 10*SUBTILE,
                                      SUBTILE, 12*SUBTILE, 3*SUBTILE))

    def test_near_miss(self):
        self.assertFalse(swept_overlap(5*SUBTILE, 6*SUBTILE,
                                       0, SUBTILE, 12*SUBTILE, SUBTILE))

    def test_fast_sweep_covers_lane(self):
        self.assertTrue(swept_overlap(4*SUBTILE, 5*SUBTILE,
                                      0, SUBTILE, 12*SUBTILE, 12*SUBTILE))

    def test_log_carries_player(self):
        self.assertEqual(carry_on_log(3*SUBTILE, 2*SUBTILE,
                                     4, 10, SUBTILE//2),
                         3*SUBTILE + SUBTILE//2)

    def test_log_edge_and_water(self):
        self.assertIsNone(carry_on_log(5*SUBTILE + 1, 2*SUBTILE,
                                       4, 10, 0))
        self.assertIsNone(carry_on_log(7*SUBTILE, 2*SUBTILE,
                                       4, 10, 0))

    def test_log_drift_offscreen(self):
        self.assertIsNone(carry_on_log(11*SUBTILE, 10*SUBTILE,
                                       2, 12, SUBTILE))

    def test_bad_geometry(self):
        with self.assertRaises(ValueError):
            swept_overlap(0, SUBTILE, 0, 3, 3, 1)
        with self.assertRaises(ValueError):
            periodic_overlap(0, 0, 0, 1, 2)

if __name__ == "__main__":
    unittest.main()
