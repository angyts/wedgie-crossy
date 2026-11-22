"""Four-way sprite and pause controls regression checks."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

class FourWayTests(unittest.TestCase):
    def test_distinct_facing_and_colored_pause_icons(self):
        lcd = types.ModuleType("lcd")
        lcd.LCD = object
        lcd.Keys = object
        lcd.color = lambda r,g,b: (r,g,b)
        save = types.ModuleType("save")
        save.load = lambda n,default=0: default
        save.store = lambda n,v: None
        old_lcd, old_save = sys.modules.get("lcd"),sys.modules.get("save")
        try:
            sys.modules["lcd"],sys.modules["save"] = lcd,save
            spec = importlib.util.spec_from_file_location(
                "crossy_stage10",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            class Screen:
                def __init__(self): self.rects=[];self.texts=[]
                def fill(self,c): pass
                def fill_rect(self,x,y,w,h,c): self.rects.append((x,y,w,h,c))
                def text(self,s,x,y,c): self.texts.append(s)
                def show(self): pass
            shapes=[]
            for facing in ("left","right","up","down"):
                screen=Screen()
                m.draw_chicken(screen,m.MIN_X,m.MIN_Y,facing)
                shapes.append(tuple(screen.rects))
                for x,y,w,h,c in screen.rects:
                    self.assertTrue(0<=x and 0<=y and x+w<=20 and y+h<=20)
            self.assertEqual(len(set(shapes)),4)
            screen=Screen()
            m.draw_world(screen,m.World(123),5,0,0,0,True,"down")
            self.assertIn("RESUME",screen.texts)
            self.assertIn("NEW RUN",screen.texts)
            self.assertFalse(any("B RESUME" in s or "A NEW RUN" in s for s in screen.texts))
            self.assertTrue(any(w==12 and h==12 for x,y,w,h,c in screen.rects))
        finally:
            for name,old in (("lcd",old_lcd),("save",old_save)):
                if old is None: sys.modules.pop(name,None)
                else: sys.modules[name]=old

if __name__=="__main__":
    unittest.main()
