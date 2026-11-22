"""Continuous log sprite and road weighting regression tests."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class LogArtTests(unittest.TestCase):
    def test_contiguous_log_is_single_body(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_log_art",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            class Screen:
                def __init__(self):self.rects=[]
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h,c))
            s=Screen()
            m.draw_log_runs(s,0b000111000,100)
            bodies=[v for v in s.rects if v[4]==m.LOG_DARK]
            self.assertEqual(len(bodies),1)
            self.assertEqual(bodies[0][2],60)
            self.assertTrue(all(0<=x and 100<=y and x+w<=240 and y+h<=120
                                for x,y,w,h,c in s.rects))
            s=Screen()
            m.draw_log_runs(s,(1<<0)|(1<<11),0)
            self.assertEqual(len([v for v in s.rects if v[4]==m.LOG_DARK]),2)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
    def test_more_roads_but_rivers_remain(self):
        import crossy_worldgen as w
        counts={"road":0,"logs":0,"lilies":0}
        for seed in range(100):
            for block in range(20):
                kind,_,_=w.section(seed,8+block*w.BLOCK)
                counts[kind]+=1
        self.assertGreater(counts["road"],sum(counts.values())*68//100)
        self.assertGreater(counts["logs"],0)
        self.assertGreater(counts["lilies"],0)
