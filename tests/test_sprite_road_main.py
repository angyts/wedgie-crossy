"""Decorative sprites stay within their tile; road sections remain varied."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class SpriteRoadTests(unittest.TestCase):
    def test_sprites_bounded(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_sprite_main",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            class Screen:
                def __init__(self):self.rects=[]
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h))
            for fn in (m.draw_tree,m.draw_flower):
                for variant in range(3):
                    screen=Screen()
                    fn(screen,100,100,variant)
                    self.assertGreater(len(screen.rects),2)
                    self.assertTrue(all(100<=x and 100<=y and x+w<=120 and y+h<=120 for x,y,w,h in screen.rects))
            self.assertFalse(m.DEV_MODE)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
    def test_road_weighting(self):
        import crossy_worldgen as w
        counts={"road":0,"logs":0,"lilies":0}
        for seed in range(100):
            for block in range(20):
                kind,_,_=w.section(seed,8+block*w.BLOCK)
                counts[kind]+=1
        self.assertGreater(counts["road"],sum(counts.values())*6//10)
        self.assertGreater(counts["logs"],0)
        self.assertGreater(counts["lilies"],0)
