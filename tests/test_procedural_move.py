"""Procedural movement entry must use the same hazards as rendering."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
class ProceduralMoveTests(unittest.TestCase):
    def test_entry_and_collision(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_procedural_move",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            m.PROCEDURAL_WORLD=True
            for seed in range(32):
                world=m.World(seed)
                world.advance(16)
                for row in range(16,25):
                    for col in range(12):
                        if row<world.first or row>world.last:continue
                        for direction in ("up","down","left","right"):
                            nc,nr,hit=m.generated_move(world,col,row,direction,0)
                            self.assertTrue(0<=nc<12)
                            self.assertTrue(world.first<=nr<=world.last)
                            if (nc,nr)!=(col,row):
                                self.assertEqual(hit,m.hazard_at(seed,nr,nc,0))
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
