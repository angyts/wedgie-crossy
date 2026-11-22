"""Integration bridge tests without changing default hardware behavior."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
class BridgeTests(unittest.TestCase):
    def test_procedural_mode_render_and_collision_masks(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_bridge",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            self.assertFalse(m.PROCEDURAL_WORLD)
            self.assertEqual(m.new_run_seed(123),0x13579bdf)
            m.PROCEDURAL_WORLD=True
            self.assertNotEqual(m.new_run_seed(123),m.new_run_seed(124))
            seed=m.new_run_seed(123)
            world=m.World(seed)
            for row in range(16,256):
                kind=m.terrain_kind(seed,row)
                self.assertIn(kind,("grass","road","logs","lilies"))
                if kind=="grass":
                    self.assertFalse(m.generated_trees(seed,row)&(1<<m.START_COL))
                if kind=="lilies":
                    self.assertTrue(m.generated_mask(seed,row,0)&(1<<m.START_COL))
                if kind=="logs":
                    self.assertEqual(m.generated_mask(seed,row,0),m.worldgen.log_mask(seed,row,0))
            world.advance(250)
            self.assertEqual(len(world.rows),12)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
