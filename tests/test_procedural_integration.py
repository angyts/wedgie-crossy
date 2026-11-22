"""Procedural movement and vehicle identity integration checks."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
class IntegrationTests(unittest.TestCase):
    def test_colors_and_movement(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_integration",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            m.PROCEDURAL_WORLD=True
            for seed in range(64):
                world=m.World(seed)
                world.advance(16)
                for row in range(16,32):
                    if m.terrain_kind(seed,row)!="road":continue
                    direction=-1 if m.worldgen.section(seed,row)[1]&1 else 1
                    for origin in range(12):
                        initial=m.car_color(row,origin,0,seed)
                        for phase in range(24):
                            col=(origin+phase*direction)%12
                            self.assertEqual(m.car_color(row,col,phase,seed),initial)
                self.assertEqual(m.generated_move(world,5,16,"down",0)[:2],(5,16))
            self.assertTrue(m.DEV_MODE)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
