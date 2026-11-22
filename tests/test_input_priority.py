"""Input interrupts interpolation and avoids extra LCD transfers."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class InputPriorityTests(unittest.TestCase):
    def test_key_interrupts_preview(self):
        fake=types.ModuleType("lcd");fake.LCD=object;fake.Keys=object
        fake.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd");sys.path.insert(0,str(ROOT))
        try:
            sys.modules["lcd"]=fake
            spec=importlib.util.spec_from_file_location("crossy_input_priority",ROOT/"crossy.py")
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            class Screen:
                def __init__(self):self.flushed=0
                def show_rect(self,*args):self.flushed+=1
            class Keys:
                def pressed(self):return ("up",)
            world=m.World(123)
            world.advance(20)
            screen=Screen()
            result=m.preview_traffic(screen,world,0,1,world.first+5,Keys())
            self.assertEqual(result,"up")
            self.assertEqual(screen.flushed,0)
            m.SMOOTH_TRAFFIC=False
            screen=Screen()
            self.assertEqual(m.preview_traffic(screen,world,0,1,world.first+5,Keys()),"up")
            self.assertEqual(screen.flushed,0)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
