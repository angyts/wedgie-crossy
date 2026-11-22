"""Log support must persist on slow-lane ticks without movement."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class LogSupportRegression(unittest.TestCase):
    def test_slow_log_stays_supported(self):
        fake=types.ModuleType("lcd")
        fake.LCD=object;fake.Keys=object;fake.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd");sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=fake
            spec=importlib.util.spec_from_file_location("crossy_log_support",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            found=False
            for seed in range(100):
                for row in range(8,100):
                    if m.terrain_kind(seed,row)!="logs" or m.worldgen.log_period(seed,row)!=2:
                        continue
                    before=m.generated_mask(seed,row,0)
                    after=m.generated_mask(seed,row,1)
                    self.assertEqual(before,after)
                    self.assertTrue(before)
                    for col in range(m.GRID_SIZE):
                        if before & (1<<col):
                            self.assertFalse(m.hazard_at(seed,row,col,0))
                            self.assertFalse(m.hazard_at(seed,row,col,1))
                            found=True
                            break
                if found:break
            self.assertTrue(found)
            source=(ROOT/"crossy.py").read_text()
            self.assertIn("elif hazard_at(seed, row, col, phase):",source)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
