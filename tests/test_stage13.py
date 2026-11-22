"""Road sprite and crash UI regression tests."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

class CrashPresentationTests(unittest.TestCase):
    def test_speed_car_and_game_over(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_crash",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            self.assertEqual(m.TRAFFIC_TICKS,3)
            self.assertTrue(m.DEV_MODE)
            class Screen:
                def __init__(self):self.rects=[];self.texts=[]
                def fill(self,c):pass
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h,c))
                def text(self,s,x,y,c):self.texts.append(s)
                def show(self):pass
            car=Screen()
            m.draw_car(car,0,0)
            self.assertGreaterEqual(len(car.rects),5)
            screen=Screen()
            m.draw_world(screen,m.World(123),5,0,23,23,dead=True,phase=0,crash_frame=3)
            self.assertIn("ALWAYS LOOK",screen.texts)
            self.assertIn("BEFORE YOU",screen.texts)
            self.assertIn("CROSS THE ROAD",screen.texts)
            self.assertIn("YOUR SCORE: 23",screen.texts)
            self.assertIn("PRESS ANY BUTTON",screen.texts)
            self.assertTrue(any(w==12 and h==12 for x,y,w,h,c in screen.rects))
            self.assertEqual(m.CRASH_FRAMES,5)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old

if __name__=="__main__":
    unittest.main()
