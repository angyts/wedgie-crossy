"""Host smoke checks for the device entry point (without real hardware)."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest

APP = Path(__file__).resolve().parents[1] / "crossy.py"

class StopAfterFirstSleep(BaseException):
    pass

class LCDStub:
    def __init__(self):
        self.calls = []
    def fill(self, value):
        self.calls.append(("fill", value))
    def text(self, text, x, y, color):
        self.calls.append(("text", text))
    def fill_rect(self, x, y, w, h, color):
        self.calls.append(("fill_rect", x, y, w, h, color))
    def show(self):
        self.calls.append(("show",))

class KeysStub:
    def pressed(self):
        return ()

class BootSmokeTests(unittest.TestCase):
    def test_pure_movement_and_bounds(self):
        fake_lcd = types.ModuleType("lcd")
        fake_lcd.LCD = LCDStub
        fake_lcd.Keys = KeysStub
        fake_lcd.color = lambda r, g, b: (r, g, b)
        old_lcd = sys.modules.get("lcd")
        try:
            sys.modules["lcd"] = fake_lcd
            spec = importlib.util.spec_from_file_location("crossy_movement", APP)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            x, y = module.START_X, module.START_Y
            self.assertEqual(module.moved(x, y, "left"), (x - 20, y))
            self.assertEqual(module.moved(x, y, "right"), (x + 20, y))
            self.assertEqual(module.moved(x, y, "up"), (x, y))
            self.assertEqual(module.moved(x, y, "down"), (x, y + 20))
            for _ in range(30):
                x, y = module.moved(x, y, "right")
            self.assertEqual(x, module.MAX_X)
            for _ in range(30):
                x, y = module.moved(x, y, "down")
            self.assertEqual(y, module.MAX_Y)
            self.assertEqual(module.moved(x, y, "A"), (x, y))
        finally:
            if old_lcd is None:
                sys.modules.pop("lcd", None)
            else:
                sys.modules["lcd"] = old_lcd

    def test_entry_draws_ready_and_polls_input(self):
        screen = LCDStub()
        polls = []
        fake_lcd = types.ModuleType("lcd")
        fake_lcd.LCD = lambda: screen
        fake_lcd.Keys = lambda: types.SimpleNamespace(
            pressed=lambda: polls.append(True) or ())
        fake_lcd.color = lambda r, g, b: (r, g, b)
        fake_time = types.ModuleType("time")
        def sleep(ms):
            self.assertEqual(ms, 100)
            raise StopAfterFirstSleep()
        fake_time.sleep_ms = sleep
        old_lcd = sys.modules.get("lcd")
        old_time = sys.modules.get("time")
        try:
            sys.modules["lcd"] = fake_lcd
            sys.modules["time"] = fake_time
            spec = importlib.util.spec_from_file_location("crossy_baseline_smoke", APP)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            with self.assertRaises(StopAfterFirstSleep):
                module.run()
        finally:
            if old_lcd is None:
                sys.modules.pop("lcd", None)
            else:
                sys.modules["lcd"] = old_lcd
            if old_time is None:
                sys.modules.pop("time", None)
            else:
                sys.modules["time"] = old_time
        self.assertIn(("text", "READY"), screen.calls)
        self.assertIn(("text", "JOYSTICK TEST"), screen.calls)
        rects = [c for c in screen.calls if c[0] == "fill_rect"]
        self.assertEqual(len(rects), 6)
        self.assertTrue(all(0 <= c[1] and 0 <= c[2] and c[1] + c[3] <= 240 and c[2] + c[4] <= 240 for c in rects))
        self.assertEqual(sum(c[0] == "show" for c in screen.calls), 1)
        self.assertEqual(len(polls), 1)

if __name__ == "__main__":
    unittest.main()
