import unittest
from crossy_core.state_contracts import trace_contracts
from crossy_core.patterns import Row, GRASS, ROAD

class StateContractTests(unittest.TestCase):
    def test_exact_states_include_clock(self):
        sections = [[Row(0, GRASS), Row(1, GRASS)],
                    [Row(2, GRASS), Row(3, GRASS)]]
        evidence = trace_contracts(sections, horizon=4, entry_phase=7)
        self.assertTrue(evidence["reached"])
        self.assertTrue(all(len(state) == 6 for state in
                            evidence["successful_exits"]))
        self.assertTrue(all(state[2] >= 10 for state in
                            evidence["successful_exits"]))
        self.assertFalse(evidence["deployable"])

    def test_blocked_join_has_no_final_exit(self):
        sections = [[Row(0, GRASS), Row(1, GRASS)],
                    [Row(2, GRASS, trees=(1 << 12)-1), Row(3, GRASS)]]
        evidence = trace_contracts(sections, horizon=8)
        self.assertFalse(evidence["reached"])
        self.assertTrue(evidence["boundary_states"][0])
        self.assertFalse(evidence["boundary_states"][-1])

    def test_phase_is_preserved(self):
        sections = [[Row(0, GRASS)], [Row(1, GRASS)]]
        result = trace_contracts(sections, horizon=1, entry_phase=11)
        self.assertTrue(result["reached"])
        self.assertEqual({state[2] for state in result["successful_exits"]},
                         {12})

    def test_camera_pressure_filters_exits(self):
        sections = [[Row(0, GRASS), Row(1, GRASS)],
                    [Row(2, GRASS), Row(3, GRASS)]]
        evidence = trace_contracts(sections, horizon=10,
            reaction_ticks=5, grace_ticks=1, pressure_interval=1,
            initial_boundary=-1)
        self.assertFalse(evidence["reached"])

    def test_reaction_delay(self):
        sections = [[Row(0, GRASS)], [Row(1, GRASS), Row(2, GRASS)]]
        self.assertFalse(trace_contracts(sections, horizon=3,
                         reaction_ticks=2)["reached"])
        self.assertTrue(trace_contracts(sections, horizon=4,
                        reaction_ticks=2)["reached"])

    def test_invalid_arguments(self):
        with self.assertRaises(ValueError):
            trace_contracts([[Row(0, GRASS)]], entry_phase=-1)
        with self.assertRaises(ValueError):
            trace_contracts([[Row(0, GRASS)]], entry_columns=(12,))
        with self.assertRaises(ValueError):
            trace_contracts([[Row(0, GRASS)]], horizon=0)

    def test_join_rejects_noncontiguous(self):
        with self.assertRaises(ValueError):
            trace_contracts([[Row(0, GRASS)], [Row(2, GRASS)]])

    def test_dangerous_row_no_automatic_approval(self):
        sections = [[Row(0, GRASS)],
                    [Row(1, ROAD, direction=1, speed=1,
                         spacing=12, length=2), Row(2, GRASS)]]
        result = trace_contracts(sections, horizon=8)
        self.assertFalse(result["deployable"])

if __name__ == "__main__":
    unittest.main()
