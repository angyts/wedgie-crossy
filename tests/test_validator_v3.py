import unittest
from crossy_core.patterns import Row, GRASS, ROAD, RIVER, RAIL
from crossy_core.validator_v3 import (
    validate_multiterrain, train_active, train_warning,
)

class MultiterrainPrototypeTests(unittest.TestCase):
    def test_grass_crossing(self):
        self.assertTrue(validate_multiterrain([Row(i, GRASS) for i in range(3)],
                                               horizon=3))

    def test_blocked_join(self):
        rows = [Row(0, GRASS), Row(1, GRASS, trees=(1 << 12)-1),
                Row(2, GRASS)]
        self.assertFalse(validate_multiterrain(rows, horizon=20))

    def test_river_with_no_starting_support(self):
        rows = [Row(0, GRASS),
                Row(1, RIVER, direction=1, speed=1, spacing=12,
                    length=2, phase=0), Row(2, GRASS)]
        # All possible landing columns are checked, not only column 5.
        self.assertFalse(validate_multiterrain(rows, entry_columns=(5,),
                                               horizon=1))

    def test_river_drift_blocks_edge(self):
        rows = [Row(0, RIVER, direction=1, speed=2, spacing=12,
                    length=3, phase=10), Row(1, GRASS)]
        self.assertFalse(validate_multiterrain(rows, entry_columns=(11,),
                                               horizon=2))

    def test_train_warning_and_active(self):
        row = Row(1, RAIL, direction=1, speed=2, length=2,
                  period=12, warning=3)
        self.assertTrue(train_active(row, 0))
        self.assertFalse(train_active(row, 2))
        self.assertTrue(train_warning(row, 9))
        self.assertFalse(train_warning(row, 8))

    def test_rail_crossing_when_clear(self):
        rows = [Row(0, GRASS),
                Row(1, RAIL, direction=1, speed=1, length=2,
                    period=12, warning=3, phase=3),
                Row(2, GRASS)]
        self.assertTrue(validate_multiterrain(rows, horizon=4))

    def test_wait_bound_and_reaction(self):
        rows = [Row(i, GRASS) for i in range(3)]
        self.assertFalse(validate_multiterrain(rows, horizon=5,
                         reaction_ticks=2, max_wait_ticks=1))
        self.assertTrue(validate_multiterrain(rows, horizon=5,
                        reaction_ticks=2, max_wait_ticks=2))

    def test_reject_bad_inputs(self):
        with self.assertRaises(ValueError):
            validate_multiterrain([])
        with self.assertRaises(ValueError):
            validate_multiterrain([Row(0, GRASS)], max_wait_ticks=-1)
        with self.assertRaises(ValueError):
            validate_multiterrain([Row(0, GRASS), Row(2, GRASS)])

if __name__ == "__main__":
    unittest.main()
