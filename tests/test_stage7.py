"""Host checks for pause HUD and milestone classification."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

class Stage7Tests(unittest.TestCase):
    def test_milestone_values(self):
        lcd = types.ModuleType("lcd")
        lcd.LCD = object
        lcd.Keys = object
        lcd.color = lambda r, g, b: (r, g, b)
        save = types.ModuleType("save")
        save.load = lambda name, default=0: default
        save.store = lambda name, value: None
        old_lcd, old_save = sys.modules.get("lcd"), sys.modules.get("save")
        try:
            sys.modules["lcd"], sys.modules["save"] = lcd, save
            spec = importlib.util.spec_from_file_location(
                "crossy_stage7", Path(__file__).resolve().parents[1] / "crossy.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.assertEqual([module.milestone(n) for n in (0, 1, 9, 10, 11, 20)],
                             [0, 0, 0, 10, 0, 20])
        finally:
            for name, old in (("lcd", old_lcd), ("save", old_save)):
                if old is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = old

if __name__ == "__main__":
    unittest.main()
