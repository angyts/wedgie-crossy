"""Camera centering and terrain rendering smoke test."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
class CenterCameraTests(unittest.TestCase):
    def test_center_follow_and_rectangles(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_center",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            self.assertEqual(m.CAMERA_LEAD,5)
            world=m.World(123)
            for row in range(1,100):
                if row-world.first>m.CAMERA_LEAD:
                    world.advance(row-m.CAMERA_LEAD)
                self.assertEqual(len(world.rows),12)
                self.assertLessEqual(row-world.first,5)
                if row>=5:self.assertEqual(row-world.first,5)
            class Screen:
                def __init__(self):self.rects=[]
                def fill(self,c):pass
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h))
                def text(self,s,x,y,c):pass
                def show(self):pass
            for first in (0,7,24):
                world=m.World(123)
                world.advance(first)
                screen=Screen()
                m.draw_world(screen,world,5,first+5,first+5)
                self.assertTrue(all(x>=0 and y>=0 and x+w<=240 and y+h<=240 for x,y,w,h in screen.rects))
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
