import unittest
from crossy_core.route_witness import find_witness, replay_witness
from crossy_core.patterns import Row, GRASS, ROAD

class RouteWitnessTests(unittest.TestCase):
    def test_open_grass_replays(self):
        sections = ((Row(0, GRASS), Row(1, GRASS)),
                    (Row(2, GRASS),))
        witness = find_witness(sections, horizon=3)
        self.assertTrue(witness["found"])
        self.assertEqual(witness["ticks"], 2)
        replay = replay_witness(sections, witness["moves"])
        self.assertTrue(replay["survived"])
        self.assertTrue(replay["finished"])
        self.assertEqual(replay["positions"], witness["positions"])

    def test_blocked_world_has_no_witness(self):
        sections = ((Row(0, GRASS),),
                    (Row(1, GRASS, trees=(1 << 12)-1),))
        self.assertFalse(find_witness(sections, horizon=4)["found"])

    def test_short_deadline(self):
        sections = ((Row(0, GRASS), Row(1, GRASS)),
                    (Row(2, GRASS),))
        self.assertFalse(find_witness(sections, horizon=1)["found"])

    def test_road_replay(self):
        sections = ((Row(0, GRASS),),
                    (Row(1, ROAD, direction=1, speed=2,
                         spacing=8, length=2), Row(2, GRASS)))
        found = []
        for phase in range(4):
            witness = find_witness(sections, entry_phase=phase, horizon=8)
            if witness["found"]:
                replay = replay_witness(sections, witness["moves"],
                                        entry_phase=phase)
                self.assertTrue(replay["finished"])
                self.assertEqual(replay["positions"], witness["positions"])
                found.append(phase)
        self.assertTrue(found)

    def test_deterministic_witness(self):
        sections = ((Row(0, GRASS),), (Row(1, GRASS),))
        self.assertEqual(find_witness(sections), find_witness(sections))

    def test_invalid_inputs(self):
        sections = ((Row(0, GRASS),), (Row(1, GRASS),))
        with self.assertRaises(ValueError):
            find_witness(sections, horizon=0)
        with self.assertRaises(ValueError):
            find_witness(sections, max_states=0)
        with self.assertRaises(ValueError):
            replay_witness(sections, (), entry_column=12)

if __name__ == "__main__":
    unittest.main()
