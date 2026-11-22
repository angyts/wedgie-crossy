"""Stage 11: sparse static roads and crash/restart rendering."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

class RoadTests(unittest.TestCase):
    def test_road_layout_and_crash_screen(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_stage11",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            self.assertTrue(m.is_road(6))
            self.assertTrue(m.is_road(18))
            self.assertFalse(m.is_road(7))
            self.assertEqual(m.row_mask(123,6),0)
            self.assertTrue(m.road_hit(123,6,2))
            self.assertFalse(m.road_hit(123,6,5))
            self.assertTrue(m.road_hit(123,18,1))
            class Screen:
                def __init__(self):self.texts=[];self.rects=[]
                def fill(self,c):pass
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h))
                def text(self,s,x,y,c):self.texts.append(s)
                def show(self):pass
            screen=Screen()
            m.draw_world(screen,m.World(123),5,0,0,0,dead=True)
            self.assertIn("CRASH!",screen.texts)
            self.assertIn("NEW RUN",screen.texts)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old

if __name__=="__main__":
    unittest.main()
