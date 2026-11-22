"""Ensure road-focused terrain variety without eliminating rivers."""
import importlib.util
import unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"crossy_worldgen.py"
spec=importlib.util.spec_from_file_location("balanced_worldgen",p)
w=importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
class BalanceTests(unittest.TestCase):
    def test_distribution_and_early_width(self):
        counts={"road":0,"logs":0,"lilies":0}
        for seed in range(100):
            for block in range(20):
                start=8+block*w.BLOCK
                kind,lane,width=w.section(seed,start)
                counts[kind]+=1
                if start<30:self.assertLessEqual(width,2)
                if 70<=start<120:self.assertLessEqual(width,7)
                if kind=="road":
                    for row in range(start,start+width):
                        self.assertIn(w.road_period(seed,row),(1,2))
        total=sum(counts.values())
        self.assertGreater(counts["road"],total//2)
        self.assertGreater(counts["logs"],0)
        self.assertGreater(counts["lilies"],0)
