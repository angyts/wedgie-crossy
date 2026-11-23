"""Three visually distinct vehicle silhouettes remain inside a tile."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class VehicleSpritesTests(unittest.TestCase):
    def test_vehicle_styles_bounded_and_distinct(self):
        fake=types.ModuleType("lcd");fake.LCD=object;fake.Keys=object
        fake.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd");sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=fake
            spec=importlib.util.spec_from_file_location("crossy_vehicle_sprites",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            class Screen:
                def __init__(self):self.rects=[]
                def fill_rect(self,x,y,w,h,c):self.rects.append((x,y,w,h,c))
            styles={}
            for row in range(100):
                style=m.car_style(row)
                if style in styles:continue
                s=Screen();m.draw_car(s,100,100,row,0,123)
                self.assertTrue(all(100<=x and 100<=y and x+w<=120 and y+h<=120
                                    for x,y,w,h,c in s.rects))
                styles[style]=[(x,y,w,h) for x,y,w,h,c in s.rects]
            self.assertEqual(set(styles),{0,1,2,3})
            self.assertEqual(len({str(v) for v in styles.values()}),3)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
