"""River death-message smoke tests."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
class RiverPresentationTests(unittest.TestCase):
    def test_messages(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_river_msg",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            class Screen:
                def __init__(self):self.texts=[]
                def fill(self,c):pass
                def fill_rect(self,x,y,w,h,c):pass
                def text(self,s,x,y,c):self.texts.append(s)
                def show(self):pass
            for kind,msg in (("water","WHERE YOU STEP"),("offscreen","BE DECISIVE"),(None,"CROSS THE ROAD")):
                s=Screen()
                m.draw_world(s,m.World(123),5,0,12,12,dead=True,death_kind=kind)
                self.assertIn(msg,s.texts)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
