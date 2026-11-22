"""Moving hazard transfers only the union of old and new footprints."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class FootprintFlushTests(unittest.TestCase):
    def test_changed_cells_only(self):
        fake=types.ModuleType("lcd");fake.LCD=object;fake.Keys=object
        fake.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd");sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=fake
            spec=importlib.util.spec_from_file_location("crossy_footprints",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            m.DEBUG=False
            class Screen:
                def __init__(self):self.rects=[];self.full=0
                def fill(self,c):pass
                def fill_rect(self,x,y,w,h,c):pass
                def text(self,s,x,y,c):pass
                def show(self):self.full+=1
                def show_rect(self,x,y,w,h):self.rects.append((x,y,w,h))
            found=False
            for seed in range(30):
                world=m.World(seed);world.advance(8)
                for absolute in range(world.first,world.last):
                    if m.terrain_kind(seed,absolute)!="road":continue
                    if m.generated_mask(seed,absolute,0)==m.generated_mask(seed,absolute,1):continue
                    screen=Screen()
                    m.draw_world(screen,world,5,world.first+5,0,dirty_rows=[absolute],phase=1,previous_phase=0)
                    self.assertEqual(screen.full,0)
                    expected=m.generated_mask(seed,absolute,0)|m.generated_mask(seed,absolute,1)
                    cells=0
                    for x,y,w,h in screen.rects:
                        self.assertEqual(h,20)
                        self.assertEqual(y,(m.WINDOW-1-(absolute-world.first))*20)
                        self.assertLessEqual(w,240)
                        cells|=((1<<(w//20))-1)<<(x//20)
                    self.assertEqual(cells,expected)
                    found=True
                    break
                if found:break
            self.assertTrue(found)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
