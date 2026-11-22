"""MicroPython-compatible popcount and source regression tests."""
import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("crossy_worldgen_compat",ROOT/"crossy_worldgen.py")
w=importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
class MicroPythonCompatTests(unittest.TestCase):
    def test_popcount(self):
        for n in (0,1,2,3,7,15,255,4095,0xaaaaaaaa,0xffffffff):
            self.assertEqual(w.count_bits(n),bin(n).count("1"))
    def test_no_bit_count_method(self):
        self.assertNotIn(".bit_count(",(ROOT/"crossy_worldgen.py").read_text())
    def test_lily_count(self):
        for seed in range(100):
            for row in range(16,160):
                if w.section(seed,row)[0]=="lilies":
                    n=w.count_bits(w.lily_mask(seed,row))
                    self.assertGreaterEqual(n,2)
                    self.assertLessEqual(n,4)
