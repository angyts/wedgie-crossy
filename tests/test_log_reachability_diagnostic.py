"""Regression: log crossings are not silently treated as guaranteed."""
import unittest
import reachability as r
import crossy_worldgen as w
class LogReachabilityDiagnostics(unittest.TestCase):
    def test_known_failure_is_reported(self):
        seed, block = 5, 2
        self.assertEqual(w.section(seed,8+block*w.BLOCK)[0],"logs")
        possible, tick = r.crossing_possible(seed,block)
        # This records an unresolved failure, rather than pretending all worlds are fair.
        self.assertFalse(possible)
        self.assertIsNone(tick)
