import unittest
from crossy_core.mixed_audit import (
    mixed_sections, audit_mixed, hazard_row,
)
from crossy_core.patterns import GRASS, ROAD, RIVER, RAIL
from crossy_core.approved_world import assert_approved

class MixedAuditTests(unittest.TestCase):
    def test_mixed_sequence_indices(self):
        sections = mixed_sections((ROAD, RIVER, RAIL))
        rows = [r for section in sections for r in section]
        self.assertEqual([r.index for r in rows], list(range(7)))
        self.assertEqual([r.kind for r in rows],
                         [GRASS, ROAD, GRASS, RIVER, GRASS, RAIL, GRASS])

    def test_pair_enumeration(self):
        cases = audit_mixed(2, max_period=60, horizon=10)
        self.assertEqual(len(cases), 9)
        self.assertEqual(len({c["families"] for c in cases}), 9)
        self.assertTrue(all(c["deployable"] is False for c in cases))

    def test_phase_cap_rejection_is_recorded(self):
        cases = audit_mixed(2, max_period=5, horizon=8)
        self.assertTrue(any(c["rejection"] is not None for c in cases))
        self.assertTrue(all(not c["passed"] for c in cases
                            if c["rejection"] is not None))

    def test_all_three_terrain_types(self):
        cases = audit_mixed(1, max_period=60, horizon=10)
        self.assertEqual({c["families"][0] for c in cases},
                         {ROAD, RIVER, RAIL})

    def test_runtime_allowlist_not_bypassed(self):
        for kind in (ROAD, RIVER, RAIL):
            sections = mixed_sections((kind,))
            rows = [r for section in sections for r in section]
            with self.assertRaises(ValueError):
                assert_approved(rows)

    def test_bad_input_rejected(self):
        with self.assertRaises(ValueError):
            mixed_sections(())
        with self.assertRaises(ValueError):
            hazard_row(1, GRASS)
        with self.assertRaises(ValueError):
            audit_mixed(4)
        with self.assertRaises(ValueError):
            audit_mixed(3, max_cases=5)

if __name__ == "__main__":
    unittest.main()
