import unittest
from crossy_core.patterns import Row, GRASS, ROAD
from crossy_core.joins import join_rows, validate_join

class JoinTests(unittest.TestCase):
    def test_open_join(self):
        sections = [[Row(0, GRASS), Row(1, GRASS)],
                    [Row(2, GRASS), Row(3, GRASS)]]
        self.assertEqual(len(join_rows(sections)), 4)
        self.assertTrue(validate_join(sections, horizon=4))

    def test_individually_open_sections_bad_join(self):
        # Each section contains a valid entry/exit tile in isolation.
        # Together the fully blocked boundary is impossible to cross.
        a = [Row(0, GRASS), Row(1, GRASS)]
        b = [Row(2, GRASS, trees=(1 << 12) - 1), Row(3, GRASS)]
        self.assertFalse(validate_join([a, b], horizon=12))

    def test_gap_rejected(self):
        with self.assertRaises(ValueError):
            join_rows([[Row(0, GRASS)], [Row(2, GRASS)]])

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            join_rows([])
        with self.assertRaises(ValueError):
            join_rows([[Row(0, GRASS)], []])

    def test_danger_limit_across_boundary(self):
        def road(i):
            return Row(i, ROAD, direction=1, speed=1, spacing=8, length=2)
        with self.assertRaises(ValueError):
            join_rows([[road(i) for i in range(3)],
                       [road(i) for i in range(3, 6)]])

    def test_safe_break_resets_limit(self):
        def road(i):
            return Row(i, ROAD, direction=1, speed=1, spacing=8, length=2)
        sections = [[road(i) for i in range(5)],
                    [Row(5, GRASS), road(6)]]
        self.assertEqual(len(join_rows(sections)), 7)

    def test_reaction_budget_across_join(self):
        sections = [[Row(0, GRASS)], [Row(1, GRASS), Row(2, GRASS)]]
        self.assertFalse(validate_join(sections, horizon=3,
                                       reaction_ticks=2))
        self.assertTrue(validate_join(sections, horizon=4,
                                      reaction_ticks=2))

if __name__ == "__main__":
    unittest.main()
