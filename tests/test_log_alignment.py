"""Adjacent log rows share traversable support; regression for seed 2647D06D."""
import unittest
import crossy_worldgen as w
import reachability as r
class LogAlignmentTests(unittest.TestCase):
    def test_seed_2647d06d(self):
        seed=int("2647D06D",16)
        for row in range(54,66):
            if w.section(seed,row)[0]=="logs" and w.section(seed,row+1)[0]=="logs":
                for phase in range(24):
                    self.assertEqual(w.log_mask(seed,row,phase),w.log_mask(seed,row+1,phase))
        block=(59-8)//w.BLOCK
        possible,tick=r.crossing_possible(seed,block)
        self.assertTrue(possible,(seed,block,tick))
    def test_adjacent_log_masks(self):
        for seed in range(100):
            for block in range(20):
                start=8+block*w.BLOCK
                kind,_,width=w.section(seed,start)
                if kind!="logs":continue
                for row in range(start,start+width-1):
                    for phase in (0,1,2,7,12,23):
                        self.assertEqual(w.log_mask(seed,row,phase),w.log_mask(seed,row+1,phase))
