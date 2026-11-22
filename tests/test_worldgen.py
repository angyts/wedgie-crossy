"""Procedural-world generator invariants and seed replay."""
import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location(
    "worldgen",Path(__file__).resolve().parents[1]/"worldgen.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class WorldGenTests(unittest.TestCase):
    def test_many_seeds_and_rows(self):
        for seed in range(1000):
            for row in range(16,160):
                kind,lane,width=m.section(seed,row)
                self.assertIn(kind,("grass","road","logs","lilies"))
                self.assertTrue(0<=width<=8)
                self.assertFalse(m.tree_mask(seed,row) & (1<<m.CENTER))
                if kind=="lilies":
                    self.assertTrue(m.lily_mask(seed,row)&(1<<m.CENTER))
                    self.assertGreaterEqual(m.lily_mask(seed,row).bit_count(),2)
                    self.assertLessEqual(m.lily_mask(seed,row).bit_count(),4)
                    self.assertEqual(m.tree_mask(seed,row-1)&(1<<m.CENTER),0)
                    self.assertEqual(m.tree_mask(seed,row+1)&(1<<m.CENTER),0)
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
                base=16+block*m.BLOCK
                self.assertTrue(all(m.section(seed,base+i)[0]=="grass"
                                    for i in range(8,16)))
if __name__=="__main__":
    unittest.main()
