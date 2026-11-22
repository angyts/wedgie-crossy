import unittest
from crossy_core.patterns import GRASS, ROAD, RIVER, RAIL
from crossy_core.candidate_catalog import (
    candidate, screen_candidate, screen_catalog,
)
from crossy_core.approved_world import ApprovedWorld, assert_approved

class CandidateCatalogTests(unittest.TestCase):
    def test_all_terrain_candidates(self):
        for kind in (ROAD, RIVER, RAIL):
            rows = candidate(kind)
            self.assertEqual(tuple(r.kind for r in rows),
                             (GRASS, kind, GRASS))

    def test_invalid_kind(self):
        with self.assertRaises(ValueError):
            candidate(GRASS)

    def test_catalog_returns_evidence(self):
        evidence = screen_catalog(horizon=32, max_period=256)
        self.assertEqual(len(evidence), 3)
        self.assertEqual({e["family"] for e in evidence},
                         {ROAD, RIVER, RAIL})
        self.assertTrue(all(e["phases_checked"] >= 1 for e in evidence))
        self.assertTrue(all(e["deployable"] is False for e in evidence))

    def test_phase_cap_fails_closed(self):
        with self.assertRaises(ValueError):
            screen_candidate(RAIL, max_period=10)

    def test_candidate_not_approved_for_runtime(self):
        for kind in (ROAD, RIVER, RAIL):
            with self.assertRaises(ValueError):
                assert_approved(candidate(kind))

    def test_approved_world_unchanged(self):
        world = ApprovedWorld(20261122)
        for i in range(100):
            world.advance_to(i)
            self.assertEqual(world.get(i).kind, GRASS)

if __name__ == "__main__":
    unittest.main()
