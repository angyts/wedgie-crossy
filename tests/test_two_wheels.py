"""Road-death car has two visible wheels inside the portrait area."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TwoWheelsTests(unittest.TestCase):
    def test_two_wheels(self):
        fake=types.ModuleType("lcd")
        fake.LCD=object;fake.Keys=object;fake.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd");sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=fake
            spec=importlib.util.spec_from_file_location("crossy_two_wheels",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            class Screen:
                def __init__(self):self.rects=[]
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h,c))
            for frame in range(1,6):
                s=Screen();m.draw_dead_chicken(s,"road",frame)
                wheels=[v for v in s.rects if v[2]==27 and v[3]==29 and v[4]==m.CAR_WHEEL]
                self.assertEqual(len(wheels),2)
                self.assertEqual(wheels[1][0]-wheels[0][0],31)
                self.assertTrue(all(x>=0 and y>=44 and x+w<=240 and y+h<112 for x,y,w,h,c in s.rects))
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
