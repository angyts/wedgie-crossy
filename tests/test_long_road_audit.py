import unittest
from crossy_core.long_road_audit import road_sections, audit_roads
from crossy_core.patterns import GRASS, ROAD
from crossy_core.approved_world import assert_approved

class LongRoadAuditTests(unittest.TestCase):
    def test_contiguous_three_roads(self):
        sections = road_sections(3)
        rows = [row for section in sections for row in section]
        self.assertEqual([r.index for r in rows], list(range(7)))
        self.assertEqual([r.kind for r in rows],
                         [GRASS, ROAD, GRASS, ROAD, GRASS, ROAD, GRASS])

    def test_alternating_directions(self):
        rows = [section[1] for section in road_sections(4)[:-1]]
        self.assertEqual([r.direction for r in rows], [1, -1, 1, -1])

    def test_review_includes_all_boundaries(self):
        evidence = audit_roads(count=2, horizon=8)
        self.assertEqual(evidence["boundaries"]["boundaries_checked"], 2)
        self.assertFalse(evidence["deployable"])

    def test_reject_invalid_count(self):
        with self.assertRaises(ValueError):
            road_sections(0)
        with self.assertRaises(ValueError):
            road_sections(5)

    def test_phase_limit_fails_closed(self):
        with self.assertRaises(ValueError):
            audit_roads(count=2, max_period=2)

    def test_runtime_allowlist_stays_closed(self):
        rows = [row for section in road_sections(2) for row in section]
        with self.assertRaises(ValueError):
            assert_approved(rows)

if __name__ == "__main__":
    unittest.main()
