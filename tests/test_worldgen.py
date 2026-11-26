"""Procedural-world generator invariants and seed replay."""
import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location(
    "crossy_worldgen",Path(__file__).resolve().parents[1]/"crossy_worldgen.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class WorldGenTests(unittest.TestCase):
    def test_many_seeds_and_rows(self):
        for seed in range(1000):
            for row in range(16,160):
                kind,lane,width=m.section(seed,row)
                self.assertIn(kind,("grass","road","logs","lilies","rail"))
                self.assertTrue(0<=width<=8)
                if kind=="rail":
                    self.assertEqual((lane,width),(0,1))
                    self.assertEqual(m.section(seed,row-1)[0],"grass")
                    self.assertEqual(m.section(seed,row+1)[0],"grass")
                elif kind!="grass":
                    start=row-lane
                    low,high=(1,2) if start<30 else (2,5) if start<70 else (5,7) if start<120 else (6,8)
                    self.assertTrue(low<=width<=high)
                self.assertFalse(m.tree_mask(seed,row) & (1<<m.CENTER))
                if kind=="lilies":
                    self.assertTrue(m.lily_mask(seed,row)&(1<<m.lily_route_col(seed,row)))
                    self.assertGreaterEqual(m.lily_mask(seed,row).bit_count(),3)
                    self.assertLessEqual(m.lily_mask(seed,row).bit_count(),5)
                    if m.section(seed,row-1)[0]=="lilies":
                        prev=m.lily_route_col(seed,row-1)
                        self.assertLessEqual(abs(m.lily_route_col(seed,row)-prev),1)
                        self.assertTrue(m.lily_mask(seed,row)&(1<<prev))
                    for bank in (row-1,row+1):
                        if m.section(seed,bank)[0]=="grass":
                            self.assertEqual(m.tree_mask(seed,bank)&m.lily_bank_route(seed,bank),0)
                    self.assertEqual(m.log_mask(seed,row,0),0)
                if kind=="logs":
                    self.assertEqual(m.lily_mask(seed,row),0)
                self.assertLessEqual(m.road_mask(seed,row,0),m.MASK)
                self.assertLessEqual(m.log_mask(seed,row,0),m.MASK)
    def test_replay_and_variation(self):
        seed=m.seed_from_ticks(123456)
        self.assertEqual(seed,m.seed_from_ticks(123456))
        self.assertNotEqual(seed,m.seed_from_ticks(123457))
        a=[m.section(seed,row) for row in range(16,400)]
        b=[m.section(m.seed_from_ticks(999),row) for row in range(16,400)]
        self.assertNotEqual(a,b)
    def test_grass_buffer(self):
        for seed in range(100):
            for block in range(20):
                base=8+block*m.BLOCK
                self.assertTrue(all(m.section(seed,base+i)[0]=="grass"
                                    for i in (8,9,11)))
                self.assertIn(m.section(seed,base+10)[0],("grass","rail"))
if __name__=="__main__":
    unittest.main()
