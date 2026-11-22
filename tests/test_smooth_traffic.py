"""Smooth traffic preview does not change physics and uses half-tile offsets."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class SmoothTrafficTests(unittest.TestCase):
    def test_preview_keeps_collision_state(self):
        fake=types.ModuleType("lcd")
        fake.LCD=object;fake.Keys=object;fake.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd");sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=fake
            spec=importlib.util.spec_from_file_location("crossy_smooth",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            class Screen:
                def __init__(self):self.rects=[];self.shows=0
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h,c))
                def show(self):self.shows+=1
            world=m.World(123);world.advance(20)
            masks=[(r,m.generated_mask(123,r,0),m.generated_mask(123,r,1))
                   for r in range(world.first,world.last+1)]
            screen=Screen()
            m.draw_moving_preview(screen,world,0,1,world.first+5)
            self.assertEqual(screen.shows,1)
            self.assertTrue(all(x>=0 and y>=0 and x+w<=240 and y+h<=240
                                for x,y,w,h,c in screen.rects))
            self.assertEqual(masks,[(r,m.generated_mask(123,r,0),m.generated_mask(123,r,1))
                                    for r in range(world.first,world.last+1)])
            self.assertTrue(m.SMOOTH_TRAFFIC)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
