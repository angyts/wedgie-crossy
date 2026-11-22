"""Top-screen HUD must be restored after a moving top row."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TopHudTests(unittest.TestCase):
    def test_top_row_restores_hud(self):
        lcd=types.ModuleType("lcd");lcd.LCD=object;lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd");sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_top_hud",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            m.DEBUG=False
            class Screen:
                def __init__(self):self.texts=[]
                def fill(self,c):pass
                def fill_rect(self,x,y,w,h,c):pass
                def text(self,s,x,y,c):self.texts.append(s)
                def show(self):pass
            world=m.World(123)
            top=world.first+m.WINDOW-1
            screen=Screen()
            m.draw_world(screen,world,5,0,0,dirty_rows=[top])
            self.assertTrue(any(s.startswith("SCORE") for s in screen.texts))
            screen=Screen()
            m.draw_world(screen,world,5,0,0,dirty_rows=[world.first])
            self.assertFalse(any(s.startswith("SCORE") for s in screen.texts))
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
