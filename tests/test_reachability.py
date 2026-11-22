"""Finite time-expanded reachability checks and reproducibility."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import reachability as r
import crossy_worldgen as w

class ReachabilityTests(unittest.TestCase):
    def test_static_lily_crossings(self):
        checked=0
        for seed in range(100):
            for block in range(8):
                if w.section(seed,8+block*w.BLOCK)[0]=="lilies":
                    possible,tick=r.crossing_possible(seed,block)
                    self.assertTrue(possible,(seed,block))
                    checked+=1
        self.assertGreater(checked,0)

    def test_deterministic_search(self):
        for seed in range(12):
            for block in range(3):
                self.assertEqual(r.crossing_possible(seed,block),
                                 r.crossing_possible(seed,block))

    def test_road_occupancy(self):
        for seed in range(10):
            row=8
            if w.section(seed,row)[0]=="road":
                for phase in range(12):
                    for col in range(12):
                        self.assertEqual(r.safe(seed,row,col,phase),
                            not bool(w.road_mask(seed,row,phase)&(1<<col)))
if __name__=="__main__":
    unittest.main()
