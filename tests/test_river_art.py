"""Variable log lanes and game-over portrait geometry."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RiverArtTests(unittest.TestCase):
    def test_log_variety(self):
        import crossy_worldgen as w
        directions=set();periods=set();same=opposite=0
        for seed in range(100):
            for block in range(30):
                start=8+block*w.BLOCK
                kind,_,width=w.section(seed,start)
                if kind!="logs":continue
                for row in range(start,start+width):
                    directions.add(w.log_direction(seed,row))
                    periods.add(w.log_period(seed,row))
                    for phase in range(24):
                        self.assertEqual(w.log_mask(seed,row,phase),w.log_mask(seed,row,phase+24))
                for row in range(start,start+width-1):
                    if w.log_direction(seed,row)==w.log_direction(seed,row+1):same+=1
                    else:opposite+=1
        self.assertEqual(directions,{-1,1})
        self.assertEqual(periods,{1,2})
        self.assertGreater(same,0)
        self.assertEqual(opposite,0)
        self.assertGreater(same,0)
    def test_death_portrait_bounded(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_death_portrait",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            class Screen:
                def __init__(self):self.rects=[]
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h))
            for kind in ("road","water"):
                for frame in range(1,6):
                    s=Screen();m.draw_dead_chicken(s,kind,frame)
                    self.assertTrue(all(0<=x and 44<=y and x+w<=240 and y+h<112 for x,y,w,h in s.rects))
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
