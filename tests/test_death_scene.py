"""Separate game-over portrait geometry and optional render profiling."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class DeathSceneTests(unittest.TestCase):
    def test_portrait_stays_above_popup(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_death_scene",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            class Screen:
                def __init__(self):self.rects=[]
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h))
            for kind in ("road","water"):
                for frame in range(1,6):
                    screen=Screen()
                    m.draw_dead_chicken(screen,kind,frame)
                    self.assertGreater(len(screen.rects),3)
                    self.assertTrue(all(x>=0 and y>=44 and x+w<=240 and y+h<112 for x,y,w,h in screen.rects))
            self.assertFalse(m.PROFILE_RENDER)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
