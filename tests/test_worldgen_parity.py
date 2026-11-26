"""Collision/render parity for the procedural integration bridge."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
class ParityTests(unittest.TestCase):
    def test_masks_match_hazards(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_parity",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            m.PROCEDURAL_WORLD=True
            for seed in range(32):
                for row in range(16,160):
                    kind=m.terrain_kind(seed,row)
                    for phase in (0,1,7,11):
                        mask=m.generated_mask(seed,row,phase)
                        for col in range(12):
                            if kind in ("road","rail"): expected=bool(mask&(1<<col))
                            elif kind in ("logs","lilies"):expected=not bool(mask&(1<<col))
                            else:expected=bool(m.generated_trees(seed,row)&(1<<col))
                            self.assertEqual(m.hazard_at(seed,row,col,phase),expected)
            self.assertFalse(m.PROCEDURAL_WORLD is False)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
