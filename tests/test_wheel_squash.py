"""Road death animation is bounded and progressively squashes the chicken."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class WheelSquashTests(unittest.TestCase):
    def test_car_and_wheel_geometry(self):
        lcd=types.ModuleType("lcd");lcd.LCD=object;lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd");sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_wheel_squash",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            class Screen:
                def __init__(self):self.rects=[]
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h,c))
            heights=[]
            for frame in range(1,6):
                s=Screen();m.draw_dead_chicken(s,"road",frame)
                self.assertTrue(all(0<=x and 44<=y and x+w<=240 and y+h<112 and w>0 and h>0 for x,y,w,h,c in s.rects))
                self.assertTrue(any(w>=60 and c==m.CAR for x,y,w,h,c in s.rects))
                self.assertTrue(any(w==32 and c==m.CAR_WHEEL for x,y,w,h,c in s.rects))
                heights.append(next(h for x,y,w,h,c in s.rects if c==m.CHICKEN))
            self.assertEqual(heights,sorted(heights,reverse=True))
            self.assertLess(heights[-1],heights[0])
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
