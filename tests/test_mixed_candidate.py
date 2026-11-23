"""Mixed-terrain candidates are deterministic and disabled in live gameplay."""
import unittest
import crossy_worldgen as w


class MixedCandidateTests(unittest.TestCase):
    def test_candidates_preserve_live_generation(self):
        found = 0
        for seed in range(100):
            for row in range(8, 150):
                original = w.section(seed, row)[0]
                candidate = w.mixed_section_candidate(seed, row)
                self.assertIn(candidate, ("grass", "road", "logs", "lilies"))
                if original == "grass":
                    self.assertEqual(candidate, "grass")
                if candidate != original:
                    found += 1
                    self.assertEqual(original, "road")
                    self.assertEqual(candidate, "logs")
                    kind, lane, width = w.section(seed, row)
                    self.assertGreaterEqual(width, 4)
                    self.assertGreater(lane, 0)
                    self.assertLess(lane, width - 1)
        self.assertGreater(found, 0)

    def test_repeatable_and_boundary_safe(self):
        for seed in (0x3F564588, 0x0676964C, 0, 0xffffffff):
            for row in range(8, 256):
                self.assertEqual(w.mixed_section_candidate(seed, row),
                                 w.mixed_section_candidate(seed, row))
                kind, lane, width = w.section(seed, row)
                if kind == "road" and lane in (0, width - 1):
                    self.assertEqual(w.mixed_section_candidate(seed, row), "road")


if __name__ == "__main__":
    unittest.main()
