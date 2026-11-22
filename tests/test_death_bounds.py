"""All death-animation frames stay within the reserved scene."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class DeathBoundsTests(unittest.TestCase):
    def test_all_frames_and_variants(self):
        fake = types.ModuleType("lcd")
        fake.LCD = object
        fake.Keys = object
        fake.color = lambda r,g,b: (r,g,b)
        old = sys.modules.get("lcd")
        sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"] = fake
            spec = importlib.util.spec_from_file_location("crossy_bounds",ROOT/"crossy.py")
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            class Screen:
                def __init__(self): self.rects=[]
                def fill_rect(self,x,y,w,h,c): self.rects.append((x,y,w,h,c))
            for kind in ("road","water"):
                for frame in range(0,12):
                    screen=Screen()
                    m.draw_dead_chicken(screen,kind,frame)
                    self.assertTrue(screen.rects)
                    for x,y,w,h,c in screen.rects:
                        self.assertGreater(w,0)
                        self.assertGreater(h,0)
                        self.assertGreaterEqual(x,0)
                        self.assertGreaterEqual(y,44)
                        self.assertLessEqual(x+w,240)
                        self.assertLess(y+h,112)
        finally:
            if old is None: sys.modules.pop("lcd",None)
            else: sys.modules["lcd"]=old
            sys.path.pop(0)
