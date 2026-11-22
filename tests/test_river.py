"""River rendering, support, carry and splash tests."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

class RiverTests(unittest.TestCase):
    def test_river_support_and_animation(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_river",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            self.assertTrue(m.is_river(12))
            self.assertFalse(m.is_road(12))
            self.assertTrue(m.supported_by_log(12,1,0))
            self.assertFalse(m.supported_by_log(12,0,0))
            self.assertEqual(m.carry_on_log(12,1,0),2)
            self.assertIsNone(m.carry_on_log(12,11,0))
            self.assertEqual(m.row_mask(123,12),0)
            class Screen:
                def __init__(self):self.rects=[]
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h))
            screen=Screen()
            for frame in range(1,5):
                m.draw_splash(screen,0,0,frame)
            self.assertEqual(len(screen.rects),16)
            self.assertTrue(all(x>=0 and y>=0 and x+w<=240 and y+h<=240 for x,y,w,h in screen.rects))
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old

if __name__=="__main__":
    unittest.main()
