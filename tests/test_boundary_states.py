import unittest
from crossy_core.boundary_states import trace_boundaries
from crossy_core.patterns import Row, GRASS, ROAD

class BoundaryStateTests(unittest.TestCase):
    def test_open_sections(self):
        sections = [[Row(0, GRASS), Row(1, GRASS)],
                    [Row(2, GRASS), Row(3, GRASS)]]
        result = trace_boundaries(sections, horizon=4)
        self.assertTrue(result["reached"])
        self.assertGreater(result["boundary_counts"][0], 0)
        self.assertGreater(result["boundary_counts"][1], 0)

    def test_blocked_second_section(self):
        sections = [[Row(0, GRASS), Row(1, GRASS)],
                    [Row(2, GRASS, trees=(1 << 12)-1),
                     Row(3, GRASS)]]
        result = trace_boundaries(sections, horizon=10)
        self.assertFalse(result["reached"])
        self.assertGreater(result["boundary_counts"][0], 0)
        self.assertEqual(result["boundary_counts"][1], 0)

    def test_camera_continues_across_join(self):
        sections = [[Row(0, GRASS), Row(1, GRASS)],
                    [Row(2, GRASS), Row(3, GRASS)]]
        result = trace_boundaries(sections, horizon=10, reaction_ticks=5,
                                  grace_ticks=1, pressure_interval=1,
                                  initial_boundary=-1)
        self.assertFalse(result["reached"])

    def test_reaction_delay(self):
        sections = [[Row(0, GRASS)], [Row(1, GRASS), Row(2, GRASS)]]
        self.assertFalse(trace_boundaries(sections, horizon=3,
                                         reaction_ticks=2)["reached"])
        self.assertTrue(trace_boundaries(sections, horizon=4,
                                        reaction_ticks=2)["reached"])

    def test_reject_invalid_input(self):
        with self.assertRaises(ValueError):
            trace_boundaries([[Row(0, GRASS)]], entry_phase=-1)
        with self.assertRaises(ValueError):
            trace_boundaries([[Row(0, GRASS)]], entry_columns=(12,))
        with self.assertRaises(ValueError):
            trace_boundaries([[Row(0, GRASS)]], horizon=0)

    def test_noncontiguous_rejected(self):
        with self.assertRaises(ValueError):
            trace_boundaries([[Row(0, GRASS)], [Row(2, GRASS)]])

if __name__ == "__main__":
    unittest.main()
