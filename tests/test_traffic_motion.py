import unittest

from crossy_traffic_motion import pixel_offset, wrapped_position, dirty_span


class TrafficMotionTests(unittest.TestCase):
    def test_endpoints_and_clamping(self):
        self.assertEqual(pixel_offset(-1, 300), 0)
        self.assertEqual(pixel_offset(0, 300), 0)
        self.assertEqual(pixel_offset(150, 300), 10)
        self.assertEqual(pixel_offset(300, 300), 20)
        self.assertEqual(pixel_offset(999, 300), 20)
        self.assertEqual(pixel_offset(1, 0), 20)

    def test_monotonic_every_millisecond(self):
        positions = [pixel_offset(t, 300) for t in range(301)]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(set(positions), set(range(21)))

    def test_both_directions_and_wrap(self):
        self.assertEqual(wrapped_position(235, 1, 10), 5)
        self.assertEqual(wrapped_position(5, -1, 10), 235)
        with self.assertRaises(ValueError):
            wrapped_position(0, 0, 2)

    def test_dirty_region_clips(self):
        self.assertEqual(dirty_span(30, 33, 20), (30, 23))
        self.assertEqual(dirty_span(-30, -25, 20), None)
        self.assertEqual(dirty_span(230, 235, 20), (230, 10))


if __name__ == "__main__":
    unittest.main()
