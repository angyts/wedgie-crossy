import unittest
from crossy_core.patterns import Row, GRASS
from crossy_core.physics import SUBTILE
from crossy_core.successor_contracts import can_continue, check_successors

class SuccessorContractTests(unittest.TestCase):
    def setUp(self):
        self.sections = [[Row(0, GRASS), Row(1, GRASS)],
                         [Row(2, GRASS), Row(3, GRASS)]]
        self.rows = [r for section in self.sections for r in section]

    def test_valid_state_continues(self):
        state = (1, 5*SUBTILE, 1, 1, 1, -3)
        self.assertTrue(can_continue(self.rows, state, horizon=2))

    def test_insufficient_horizon(self):
        state = (1, 5*SUBTILE, 1, 1, 1, -3)
        self.assertFalse(can_continue(self.rows, state, horizon=1))

    def test_blocked_successor(self):
        sections = [[Row(0, GRASS), Row(1, GRASS)],
                    [Row(2, GRASS, trees=(1<<12)-1), Row(3, GRASS)]]
        rows = [r for section in sections for r in section]
        self.assertFalse(can_continue(rows, (1, 5*SUBTILE, 1, 1, 1, -3)))

    def test_preserves_absolute_hazard_phase(self):
        state = (1, 5*SUBTILE, 101, 1, 1, -3)
        self.assertTrue(can_continue(self.rows, state, entry_phase=100,
                                     horizon=2))

    def test_camera_state_not_reset(self):
        state = (1, 5*SUBTILE, 5, 1, 1, 1)
        self.assertFalse(can_continue(self.rows, state, horizon=5,
                         grace_ticks=1, pressure_interval=1,
                         initial_boundary=-1))

    def test_state_already_behind_boundary_is_dead(self):
        state = (1, 5*SUBTILE, 5, 1, 1, 2)
        self.assertFalse(can_continue(self.rows, state, horizon=5,
                         grace_ticks=1, pressure_interval=1,
                         initial_boundary=-1))

    def test_state_just_ahead_of_boundary_can_continue(self):
        state = (1, 5*SUBTILE, 1, 1, 1, 0)
        self.assertTrue(can_continue(self.rows, state, horizon=2,
                        grace_ticks=1, pressure_interval=1,
                        initial_boundary=-1))

    def test_empty_fails_closed(self):
        self.assertFalse(check_successors(self.sections, ())["passed"])

    def test_batch_all_states(self):
        states = ((1, 5*SUBTILE, 1, 1, 1, -3),
                  (1, 6*SUBTILE, 1, 1, 1, -3))
        result = check_successors(self.sections, states, horizon=2)
        self.assertTrue(result["passed"])
        self.assertEqual(result["checked"], 2)
        self.assertFalse(result["deployable"])

    def test_invalid_state_rejected(self):
        with self.assertRaises(ValueError):
            can_continue(self.rows, (1, 5, 0))
        with self.assertRaises(ValueError):
            can_continue(self.rows, (1, -1, 1, 1, 1, -3))

if __name__ == "__main__":
    unittest.main()
