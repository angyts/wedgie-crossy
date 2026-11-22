"""Log carry input-buffer regression test."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

class LogInputTests(unittest.TestCase):
    def test_up_press_during_carry_is_buffered(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_log_input",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            class Screen:
                def fill(self,c):pass
                def fill_rect(self,x,y,w,h,c):pass
                def text(self,s,x,y,c):pass
                def show(self):pass
            class Keys:
                calls=0
                def pressed(self):
                    self.calls+=1
                    return ("up",) if self.calls==2 else ()
            class StopSleep(BaseException):pass
            old_sleep=m.time.sleep_ms
            m.time.sleep_ms=lambda ms:None
            try:
                key=m.animate_log_carry(Screen(),m.World(123),1,12,12,12,"up",0,1,Keys())
                self.assertEqual(key,"up")
            finally:
                m.time.sleep_ms=old_sleep
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
