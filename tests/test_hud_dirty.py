"""HUD must survive dirty updates of the topmost row."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class HudDirtyTests(unittest.TestCase):
    def test_top_row_redraw_repaints_hud(self):
        fake=types.ModuleType("lcd")
        fake.LCD=object;fake.Keys=object;fake.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd");sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=fake
            spec=importlib.util.spec_from_file_location("crossy_hud_dirty",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            m.DEBUG=False
            class Screen:
                def __init__(self):self.texts=[]
                def fill(self,c):pass
                def fill_rect(self,x,y,w,h,c):pass
                def text(self,s,x,y,c):self.texts.append(s)
                def show(self):pass
            world=m.World(123)
            screen=Screen()
            m.draw_world(screen,world,5,0,0,dirty_rows=[world.first+m.WINDOW-1])
            self.assertTrue(any(s.startswith("SCORE") for s in screen.texts))
            screen=Screen()
            m.draw_world(screen,world,5,0,0,dirty_rows=[world.first])
            self.assertFalse(any(s.startswith("SCORE") for s in screen.texts))
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
