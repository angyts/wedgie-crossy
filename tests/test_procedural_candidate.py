"""Randomized hardware-candidate configuration and replay tests."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
class CandidateTests(unittest.TestCase):
    def test_random_and_fixed_seed(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_candidate",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            self.assertTrue(m.PROCEDURAL_WORLD)
            self.assertFalse(m.DEV_MODE)
            self.assertIsNone(m.FIXED_SEED)
            self.assertNotEqual(m.new_run_seed(100),m.new_run_seed(101))
            m.FIXED_SEED=123456
            self.assertEqual(m.new_run_seed(100),123456)
            self.assertEqual(m.new_run_seed(101),123456)
            m.FIXED_SEED=None
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
            sys.path.pop(0)
