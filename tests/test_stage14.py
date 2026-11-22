"""Stage 14 traffic visual variants and bounded difficulty tests."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

class TrafficVarietyTests(unittest.TestCase):
    def test_variants_and_speed(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_stage14",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            self.assertEqual([m.car_style(r) for r in (6,18,30)], [0,1,2])
            self.assertEqual([m.car_length(r) for r in (6,18,30)], [16,16,18])
            self.assertEqual([m.traffic_interval(n) for n in (0,29,30,59,60,1000)], [3,3,2,2,2,2])
            class Screen:
                def __init__(self):self.rects=[];self.texts=[]
                def fill(self,c):pass
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h,c))
                def text(self,s,x,y,c):self.texts.append(s)
                def show(self):pass
            cars=[]
            for r in (6,18,30):
                s=Screen()
                m.draw_car(s,0,0,r)
                cars.append(s.rects)
                self.assertTrue(all(0<=x and 0<=y and x+w<=20 and y+h<=20 for x,y,w,h,c in s.rects))
            self.assertNotEqual(cars[0],cars[1])
            self.assertNotEqual(cars[1],cars[2])
            s=Screen()
            m.draw_world(s,m.World(123),5,0,30,30)
            self.assertNotIn("FASTER!",s.texts)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old

if __name__=="__main__":
    unittest.main()
