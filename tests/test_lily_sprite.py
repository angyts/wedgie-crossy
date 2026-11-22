"""Giant leaf sprite stays within its 20px cell."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
class LilySpriteTests(unittest.TestCase):
    def test_leaf_geometry(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_lily",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            class Screen:
                def __init__(self):self.rects=[]
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h,c))
            for x,y in ((0,0),(100,100),(220,220)):
                screen=Screen()
                m.draw_lily(screen,x,y)
                self.assertGreaterEqual(len(screen.rects),10)
                self.assertTrue(all(x<=rx and y<=ry and rx+w<=x+20 and ry+h<=y+20 for rx,ry,w,h,c in screen.rects))
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
