"""Half-tile traffic preview uses partial transfers, stable vehicle identity."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class SmoothPartialTests(unittest.TestCase):
    def test_preview_and_colors(self):
        fake=types.ModuleType("lcd");fake.LCD=object;fake.Keys=object
        fake.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd");sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=fake
            spec=importlib.util.spec_from_file_location("crossy_smooth_partial",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            class Screen:
                def __init__(self):self.rects=[];self.flush=[];self.full=0
                def fill_rect(self,x,y,w,h,c):
                    self.assertTrue(0<=x and 0<=y and x+w<=240 and y+h<=240 and w>0 and h>0)
                    self.rects.append((x,y,w,h,c))
                def show_rect(self,x,y,w,h):self.flush.append((x,y,w,h))
                def show(self):self.full+=1
            class Keys:
                def pressed(self):return ()
            for seed in (1,123,0x2647D06D):
                world=m.World(seed);world.advance(20)
                s=Screen()
                m.preview_traffic(s,world,0,1,world.first+5,Keys())
                self.assertEqual(s.full,0)
                self.assertTrue(all(h==20 and w<=240 for x,y,w,h in s.flush))
            self.assertIn(m.SMOOTH_TRAFFIC, (True, False))
            self.assertEqual(m.SMOOTH_STEPS, (5, 10, 15))
            self.assertEqual(m.car_color(6,2,1,123),m.car_color(6,2,1,123))
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
