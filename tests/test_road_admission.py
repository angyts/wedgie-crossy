import unittest
from crossy_core.road_admission import road_fixture, review_road_fixture
from crossy_core.approved_world import ApprovedWorld, assert_approved
from crossy_core.patterns import GRASS, ROAD

class RoadAdmissionTests(unittest.TestCase):
    def test_fixture_contiguous(self):
        sections = road_fixture()
        rows = [row for section in sections for row in section]
        self.assertEqual([row.index for row in rows], list(range(5)))
        self.assertEqual([row.kind for row in rows],
                         [GRASS, ROAD, GRASS, ROAD, GRASS])

    def test_review_has_both_evidence_types(self):
        evidence = review_road_fixture()
        self.assertIn("whole_join", evidence)
        self.assertIn("successors", evidence)
        self.assertEqual(evidence["whole_join"]["phases_checked"], 4)
        self.assertEqual(evidence["successors"]["phases_checked"], 4)

    def test_review_never_grants_runtime_approval(self):
        evidence = review_road_fixture()
        self.assertFalse(evidence["deployable"])
        self.assertFalse(evidence["runtime_allowlisted"])

    def test_road_still_rejected_by_allowlist(self):
        rows = [row for section in road_fixture() for row in section]
        with self.assertRaises(ValueError):
            assert_approved(rows)

    def test_existing_generator_still_grass_only(self):
        world = ApprovedWorld(7)
        world.advance_to(15)
        self.assertTrue(all(world.get(i).kind == GRASS for i in range(16)))

    def test_phase_cap_fails_closed(self):
        with self.assertRaises(ValueError):
            review_road_fixture(max_period=2)

if __name__ == "__main__":
    unittest.main()
