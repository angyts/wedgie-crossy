"""Stage 9 HUD rendering and milestone timer checks."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

class HUDTests(unittest.TestCase):
    def test_hud_variants(self):
        lcd = types.ModuleType("lcd")
        lcd.LCD = object
        lcd.Keys = object
        lcd.color = lambda r,g,b: (r,g,b)
        save = types.ModuleType("save")
        save.load = lambda name, default=0: default
        save.store = lambda name, value: None
        old_lcd, old_save = sys.modules.get("lcd"), sys.modules.get("save")
        try:
            sys.modules["lcd"], sys.modules["save"] = lcd, save
            spec = importlib.util.spec_from_file_location(
                "crossy_stage9", Path(__file__).resolve().parents[1] / "crossy.py")
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            class Screen:
                def __init__(self): self.texts=[]; self.rects=[]
                def fill(self, c): pass
                def fill_rect(self, x,y,w,h,c): self.rects.append((x,y,w,h,c))
                def text(self, s,x,y,c): self.texts.append((s,x,y,c))
                def show(self): pass
            normal, highlight, paused = Screen(), Screen(), Screen()
            world = m.World(123)
            m.draw_world(normal, world, 5, 0, 10, 20)
            m.draw_world(highlight, world, 5, 0, 10, 20, milestone_active=True)
            m.draw_world(paused, world, 5, 0, 10, 20, paused=True)
            self.assertEqual(sum(s == "SCORE 10" for s,x,y,c in normal.texts), 1)
            self.assertEqual(sum(s == "SCORE 10" for s,x,y,c in highlight.texts), 2)
            self.assertFalse(any(s == "x10" for s,x,y,c in highlight.texts))
            self.assertFalse(any(s == "ROW 10!" for s,x,y,c in highlight.texts))
            self.assertFalse(any(s == "Y" for s,x,y,c in normal.texts))
            self.assertTrue(any(s == "RESUME" for s,x,y,c in paused.texts))
            self.assertFalse(any(s == "Y" for s,x,y,c in paused.texts))
            self.assertFalse(any(h == 2 and y == 21 for x,y,w,h,c in normal.rects))
            self.assertTrue(any(s == "BEST 20" for s,x,y,c in normal.texts))
        finally:
            for name, old in (("lcd", old_lcd), ("save", old_save)):
                if old is None: sys.modules.pop(name, None)
                else: sys.modules[name] = old

if __name__ == "__main__":
    unittest.main()
