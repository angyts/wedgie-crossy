import unittest
from crossy_core.patterns import Row, GRASS, ROAD, RIVER, RAIL
from crossy_core.validator_v2 import validate_swept_roads

class SweptValidatorTests(unittest.TestCase):
    def test_clear_grass(self):
        self.assertTrue(validate_swept_roads([Row(i, GRASS) for i in range(4)],
                                             horizon=4))

    def test_blocked_join(self):
        self.assertFalse(validate_swept_roads([
            Row(0, GRASS), Row(1, GRASS, trees=(1 << 12)-1),
            Row(2, GRASS)]))

    def test_fast_road_rejected(self):
        # Spacing 12, length 1, speed 8 sweeps most of the lane each
        # tick; all available columns are covered during the crossing.
        rows = [Row(0, GRASS),
                Row(1, ROAD, direction=1, speed=8, spacing=12, length=4),
                Row(2, GRASS)]
        self.assertFalse(validate_swept_roads(rows, horizon=12))

    def test_reaction_delay(self):
        rows = [Row(i, GRASS) for i in range(3)]
        self.assertTrue(validate_swept_roads(rows, horizon=4, reaction_ticks=2))
        self.assertFalse(validate_swept_roads(rows, horizon=3, reaction_ticks=2))

    def test_reject_unsupported_dynamics(self):
        for kind in (RIVER, RAIL):
            if kind == RIVER:
                row = Row(1, kind, direction=1, speed=1, spacing=8, length=3)
            else:
                row = Row(1, kind, direction=1, speed=1, length=3,
                          period=12, warning=4)
            with self.assertRaises(NotImplementedError):
                validate_swept_roads([Row(0, GRASS), row])

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            validate_swept_roads([])
        with self.assertRaises(ValueError):
            validate_swept_roads([Row(0, GRASS)], entry_phases=(-1,))
        with self.assertRaises(ValueError):
            validate_swept_roads([Row(0, GRASS)], reaction_ticks=-1)

if __name__ == "__main__":
    unittest.main()
