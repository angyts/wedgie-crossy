"""Development overlay and wheel geometry stay bounded."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class DebugWheelTests(unittest.TestCase):
    def test_overlay_and_wheel(self):
        lcd=types.ModuleType("lcd");lcd.LCD=object;lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd");sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_debug_wheel",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            class Screen:
                def __init__(self):self.rects=[];self.texts=[]
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h))
                def text(self,s,x,y,c):self.texts.append(s)
            m.DEBUG=True
            screen=Screen()
            m.draw_debug_overlay(screen,0x12345678,4)
            self.assertTrue(any("12345678" in s for s in screen.texts))
            self.assertTrue(any("P:4" in s for s in screen.texts))
            for frame in range(1,6):
                screen=Screen()
                m.draw_dead_chicken(screen,"road",frame)
                self.assertTrue(all(x>=0 and y>=44 and x+w<=240 and y+h<112 for x,y,w,h in screen.rects))
            m.DEBUG=False
            screen=Screen();m.draw_debug_overlay(screen,123,1)
            self.assertEqual(screen.rects,[])
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
