import unittest
from crossy_core.patterns import Row, GRASS, ROAD, RIVER, RAIL
from crossy_core.shared_validator_fp import validate_fp

class SharedFPValidatorTests(unittest.TestCase):
    def test_grass_route(self):
        self.assertTrue(validate_fp([Row(i, GRASS) for i in range(3)],
                                    horizon=2))

    def test_blocked_route(self):
        self.assertFalse(validate_fp([
            Row(0, GRASS), Row(1, GRASS, trees=(1 << 12)-1),
            Row(2, GRASS)], horizon=20))

    def test_river_carry_crossing(self):
        rows = [Row(0, GRASS),
                Row(1, RIVER, direction=1, speed=1,
                    spacing=12, length=4, phase=3),
                Row(2, GRASS)]
        self.assertTrue(validate_fp(rows, horizon=3))

    def test_river_no_support_at_entry(self):
        rows = [Row(0, GRASS),
                Row(1, RIVER, direction=1, speed=1,
                    spacing=12, length=2, phase=0),
                Row(2, GRASS)]
        self.assertFalse(validate_fp(rows, horizon=1))

    def test_reaction_delay(self):
        rows = [Row(i, GRASS) for i in range(3)]
        self.assertFalse(validate_fp(rows, horizon=3, reaction_ticks=2))
        self.assertTrue(validate_fp(rows, horizon=4, reaction_ticks=2))

    def test_rail_crossing(self):
        rows = [Row(0, GRASS),
                Row(1, RAIL, direction=1, speed=2,
                    length=3, period=30, warning=4),
                Row(2, GRASS)]
        self.assertTrue(validate_fp(rows, entry_phases=(12, 15), horizon=3))

    def test_rail_warning_delays_crossing(self):
        rows = [Row(0, GRASS),
                Row(1, RAIL, direction=1, speed=2,
                    length=3, period=30, warning=4),
                Row(2, GRASS)]
        self.assertFalse(validate_fp(rows, entry_phases=(27,), horizon=2))

    def test_bad_entry(self):
        with self.assertRaises(ValueError):
            validate_fp([Row(0, ROAD, direction=1, speed=1,
                             spacing=8, length=2)])

if __name__ == "__main__":
    unittest.main()
