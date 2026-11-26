"""Dynamic dirty rows track only changed masks."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RenderBatchTests(unittest.TestCase):
    def test_changed_rows(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_render_batch",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            for seed in range(12):
                world=m.World(seed);world.advance(20)
                player=world.first+5
                for phase in range(24):
                    rows=m.changed_hazard_rows(world,phase,phase+1,player)
                    self.assertIn(player,rows)
                    self.assertEqual(len(rows),len(set(rows)))
                    for row in range(world.first,world.last+1):
                        if row!=player and m.terrain_kind(seed,row) in ("road","logs"):
                            self.assertEqual(row in rows,m.generated_mask(seed,row,phase)!=m.generated_mask(seed,row,phase+1))
            self.assertFalse(m.DEV_MODE)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
