"""HUD and facing smoke tests for the Stage 8 device app."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

class Stage8Tests(unittest.TestCase):
    def test_milestone_does_not_draw_center_popup(self):
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
                "crossy_stage8", Path(__file__).resolve().parents[1] / "crossy.py")
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            class Screen:
                def __init__(self): self.texts=[]; self.rects=[]
                def fill(self, color): pass
                def fill_rect(self, x,y,w,h,color): self.rects.append((x,y,w,h))
                def text(self, text,x,y,color): self.texts.append(text)
                def show(self): pass
            screen = Screen()
            m.draw_world(screen, m.World(123), 5, 0, 10, 12)
            self.assertIn("SCORE 10", screen.texts)
            self.assertNotIn("ROW 10!", screen.texts)
            self.assertFalse(any(y == 100 and w == 130 for x,y,w,h in screen.rects))
            paused = Screen()
            m.draw_world(paused, m.World(123), 5, 0, 0, 12, True)
            self.assertIn("B RESUME", paused.texts)
            self.assertIn("A NEW RUN", paused.texts)
            self.assertNotIn("A RESET", paused.texts)
            left, right = Screen(), Screen()
            m.draw_chicken(left, m.MIN_X, m.MIN_Y, "left")
            m.draw_chicken(right, m.MIN_X, m.MIN_Y, "right")
            self.assertNotEqual(left.rects, right.rects)
        finally:
            for name, old in (("lcd", old_lcd), ("save", old_save)):
                if old is None: sys.modules.pop(name, None)
                else: sys.modules[name] = old

if __name__ == "__main__":
    unittest.main()
