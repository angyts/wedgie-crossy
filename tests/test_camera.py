import unittest
from crossy_core.camera import Camera
from crossy_core.camera_validator import validate_camera
from crossy_core.patterns import Row, GRASS

class CameraTests(unittest.TestCase):
    def test_grace_then_pressure(self):
        c = Camera(grace_ticks=3, pressure_interval=2)
        self.assertFalse(c.update(0, 3))
        self.assertEqual(c.boundary, -3)
        self.assertFalse(c.update(0, 4))
        self.assertEqual(c.boundary, -2)
        self.assertFalse(c.update(0, 5))
        self.assertEqual(c.boundary, -2)
        self.assertFalse(c.update(0, 6))
        self.assertEqual(c.boundary, -1)
        self.assertTrue(c.update(0, 8))

    def test_only_new_progress_resets(self):
        c = Camera(grace_ticks=2, pressure_interval=1)
        c.update(2, 1)
        c.update(1, 2)
        c.update(2, 3)
        self.assertEqual(c.last_progress_tick, 1)
        c.update(3, 4)
        self.assertEqual(c.last_progress_tick, 4)
        self.assertEqual(c.best_row, 3)

    def test_boundary_never_recedes(self):
        c = Camera(grace_ticks=1, pressure_interval=1)
        c.update(0, 8)
        old = c.boundary
        c.update(5, 9)
        self.assertEqual(c.boundary, old)

    def test_clone_independent(self):
        c = Camera()
        other = c.clone()
        other.update(4, 1)
        self.assertEqual(c.best_row, 0)

    def test_camera_blocks_slow_route(self):
        rows = [Row(i, GRASS) for i in range(5)]
        self.assertFalse(validate_camera(rows, horizon=10,
                         reaction_ticks=5, grace_ticks=1,
                         pressure_interval=1, initial_boundary=-1))
        self.assertTrue(validate_camera(rows, horizon=5,
                        grace_ticks=10, pressure_interval=2))

    def test_blocked_join(self):
        rows = [Row(0, GRASS), Row(1, GRASS, trees=(1 << 12)-1),
                Row(2, GRASS)]
        self.assertFalse(validate_camera(rows, horizon=10))

    def test_bad_parameters(self):
        with self.assertRaises(ValueError):
            Camera(pressure_interval=0)
        with self.assertRaises(ValueError):
            validate_camera([], horizon=10)

if __name__ == "__main__":
    unittest.main()
