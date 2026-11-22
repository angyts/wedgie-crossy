import unittest
from crossy_core.road_outcomes import classify_boundary
from crossy_core.patterns import Row, GRASS, ROAD

class RoadOutcomeTests(unittest.TestCase):
    def test_grass_has_continuable_states(self):
        sections = ((Row(0, GRASS), Row(1, GRASS)),
                    (Row(2, GRASS),))
        result = classify_boundary(sections, horizon=3)
        self.assertEqual(result["phases_checked"], 1)
        self.assertGreater(result["outcomes"][0]["continuable"], 0)
        self.assertFalse(result["deployable"])

    def test_late_arrivals_are_distinguished(self):
        sections = ((Row(0, GRASS), Row(1, GRASS)),
                    (Row(2, GRASS),))
        result = classify_boundary(sections, horizon=3)
        self.assertEqual(result["outcomes"][0]["classification"],
                         "mixed-continuation")

    def test_blocked_successor(self):
        sections = ((Row(0, GRASS), Row(1, GRASS)),
                    (Row(2, GRASS, trees=(1<<12)-1),))
        result = classify_boundary(sections, horizon=3)
        self.assertEqual(result["outcomes"][0]["classification"],
                         "no-viable-continuation")

    def test_road_phase_count(self):
        sections = ((Row(0, GRASS),),
                    (Row(1, ROAD, direction=1, speed=2,
                         spacing=8, length=2), Row(2, GRASS)))
        result = classify_boundary(sections, horizon=4)
        self.assertEqual(result["phases_checked"], 4)

    def test_invalid_cap(self):
        sections = ((Row(0, GRASS),), (Row(1, GRASS),))
        with self.assertRaises(ValueError):
            classify_boundary(sections, max_states=0)

if __name__ == "__main__":
    unittest.main()
