"""Partial LCD transfer must not send the entire screen on traffic ticks."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PartialFlushTests(unittest.TestCase):
    def test_dirty_transfer_and_full_fallback(self):
        fake=types.ModuleType("lcd");fake.LCD=object;fake.Keys=object
        fake.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd");sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=fake
            spec=importlib.util.spec_from_file_location("crossy_partial_flush",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            m.DEBUG=False
            class Screen:
                def __init__(self):self.rects=[];self.full=0
                def fill(self,c):pass
                def fill_rect(self,x,y,w,h,c):pass
                def text(self,s,x,y,c):pass
                def show(self):self.full+=1
                def show_rect(self,x,y,w,h):self.rects.append((x,y,w,h))
            world=m.World(123)
            top=world.first+m.WINDOW-1
            screen=Screen()
            m.draw_world(screen,world,5,0,0,dirty_rows=[world.first+4])
            self.assertEqual(screen.full,0)
            self.assertEqual(screen.rects,[(0,140,240,20)])
            screen=Screen()
            m.draw_world(screen,world,5,0,0,dirty_rows=[top])
            self.assertEqual(screen.full,0)
            self.assertEqual(screen.rects,[(0,0,240,20)])
            screen=Screen()
            m.draw_world(screen,world,5,0,0)
            self.assertEqual(screen.full,1)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
