"""Live mixed-terrain flag and offline validator must agree."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import crossy_worldgen as w
import crossy_mixed_validator as v


class MixedLiveParityTests(unittest.TestCase):
    def test_trial_flag_is_enabled(self):
        self.assertTrue(w.MIXED_TERRAIN)

    def test_default_matches_base_sections(self):
        previous = w.MIXED_TERRAIN
        try:
            w.MIXED_TERRAIN = False
            for seed in (0, 1, 0x3F564588, 0x0676964C):
                for row in range(0, 180):
                    self.assertEqual(w.section(seed, row), w._base_section(seed, row))
        finally:
            w.MIXED_TERRAIN = previous

    def test_enabled_terrain_and_masks_match_validator(self):
        previous = w.MIXED_TERRAIN
        try:
            w.MIXED_TERRAIN = True
            found = 0
            for seed in (0, 1, 2, 3, 0x3F564588, 0x0676964C):
                for row in range(8, 160):
                    kind = w.section(seed, row)[0]
                    self.assertEqual(kind, v.lane_kind(seed, row))
                    if kind == "logs":
                        for phase in (0, 1, 2, 5):
                            self.assertEqual(w.log_mask(seed, row, phase),
                                             v.occupancy(seed, row, phase, kind))
                    elif kind == "road":
                        for phase in (0, 1, 2, 5):
                            self.assertEqual(w.road_mask(seed, row, phase),
                                             v.occupancy(seed, row, phase, kind))
                    if kind != w._base_section(seed, row)[0]:
                        found += 1
            self.assertGreater(found, 0)
        finally:
            w.MIXED_TERRAIN = previous


if __name__ == "__main__":
    unittest.main()
