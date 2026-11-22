"""Desktop debug-clock compatibility and rising water portrait."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class WaterDebugTests(unittest.TestCase):
    def test_debug_without_micropython_clock(self):
        lcd=types.ModuleType("lcd");lcd.LCD=object;lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd");sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_water_debug",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            class Screen:
                def __init__(self):self.rects=[];self.texts=[]
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h,c))
                def text(self,s,x,y,c):self.texts.append(s)
            s=Screen()
            original=m.time
            m.time=types.SimpleNamespace()
            try:
                m.draw_debug_overlay(s,0x12345678,4)
            finally:
                m.time=original
            self.assertTrue(any("12345678" in x for x in s.texts))
            self.assertTrue(any("P:4" in x for x in s.texts))
            tops=[]
            for frame in range(1,6):
                s=Screen()
                m.draw_dead_chicken(s,"water",frame)
                water=[v for v in s.rects if v[4]==m.WATER]
                self.assertEqual(len(water),1)
                tops.append(water[0][1])
                self.assertTrue(all(0<=x and 44<=y and x+w<=240 and y+h<112 for x,y,w,h,c in s.rects))
            self.assertEqual(tops,sorted(tops,reverse=True))
            self.assertGreater(tops[0],tops[-1])
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
