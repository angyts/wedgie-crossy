"""Procedural packaging and log direction tests."""
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class DevicePreflight(unittest.TestCase):
    def test_manifest_includes_worldgen(self):
        manifest=json.loads((ROOT/"wedgie.json").read_text())
        self.assertIn("worldgen.py",manifest["apps"][0]["files"])
        self.assertIn("crossy.py",manifest["apps"][0]["files"])
    def test_carry_animation_matches_lane_direction(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_preflight",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            m.PROCEDURAL_WORLD=True
            class Screen:
                def fill(self,c):pass
                def fill_rect(self,x,y,w,h,c):pass
                def text(self,s,x,y,c):pass
                def show(self):pass
            class Keys:
                def pressed(self):return ()
            for seed in range(20):
                world=m.World(seed)
                for row in range(16,80):
                    kind,lane,width=m.worldgen.section(seed,row)
                    if kind!="logs":continue
                    world.advance(max(world.first,row-5))
                    direction=-1 if lane&1 else 1
                    col=5
                    frames=[]
                    original=m.draw_world
                    def capture(*args,**kwargs):
                        frames.append(kwargs.get("chicken_dx",0))
                    m.draw_world=capture
                    try:
                        m.animate_log_carry(Screen(),world,col,row,row,row,"up",0,1,Keys())
                    finally:
                        m.draw_world=original
                    self.assertEqual(frames,[5*direction,10*direction,15*direction,20*direction])
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
