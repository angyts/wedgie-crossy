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
            self.assertEqual(module.moved(x, y, "up"), (x, y - 20))
            self.assertEqual(module.moved(x, y, "down"), (x, y + 20))
            for _ in range(30):
                x, y = module.moved(x, y, "right")
            self.assertEqual(x, module.MAX_X)
            for _ in range(30):
                x, y = module.moved(x, y, "down")
            self.assertEqual(y, module.MAX_Y)
            for _ in range(30):
                x, y = module.moved(x, y, "up")
            self.assertEqual(y, module.MIN_Y)
            self.assertEqual((x - module.MIN_X) % 20, 0)
            self.assertEqual((y - module.MIN_Y) % 20, 0)
            self.assertEqual(module.moved(x, y, "A"), (x, y))
        finally:
            if old_lcd is None:
                sys.modules.pop("lcd", None)
            else:
                sys.modules["lcd"] = old_lcd

    def test_chicken_rectangles_stay_in_occupied_tile(self):
        fake_lcd = types.ModuleType("lcd")
        fake_lcd.LCD = LCDStub
        fake_lcd.Keys = KeysStub
        fake_lcd.color = lambda r, g, b: (r, g, b)
        old_lcd = sys.modules.get("lcd")
        try:
            sys.modules["lcd"] = fake_lcd
            spec = importlib.util.spec_from_file_location("crossy_tile_alignment", APP)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for col, row in ((0, 0), (5, 9), (11, 11)):
                screen = LCDStub()
                x = module.MIN_X + col * module.STEP
                y = module.MIN_Y + row * module.STEP
                module.draw_chicken(screen, x, y)
                self.assertGreaterEqual(len(screen.calls), 6)
                for _, rx, ry, rw, rh, _ in screen.calls:
                    self.assertGreaterEqual(rx, col * 20)
                    self.assertGreaterEqual(ry, row * 20)
                    self.assertLessEqual(rx + rw, (col + 1) * 20)
                    self.assertLessEqual(ry + rh, (row + 1) * 20)
        finally:
            if old_lcd is None:
                sys.modules.pop("lcd", None)
            else:
                sys.modules["lcd"] = old_lcd

    def test_tree_collisions_and_open_route(self):
        fake_lcd = types.ModuleType("lcd")
        fake_lcd.LCD = LCDStub
        fake_lcd.Keys = KeysStub
        fake_lcd.color = lambda r, g, b: (r, g, b)
        old_lcd = sys.modules.get("lcd")
        try:
            sys.modules["lcd"] = fake_lcd
            spec = importlib.util.spec_from_file_location("crossy_tree_collision", APP)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            x, y = module.START_X, module.START_Y
            self.assertEqual(module.try_move(x, y, "right"), (x, y))
            self.assertEqual(module.try_move(x, y, "up"), (x, y - 20))
            self.assertEqual(module.try_move(x, y - 20, "left"), (x, y - 20))
            self.assertEqual(module.try_move(x, y, "left"), (x - 20, y))
            self.assertNotIn(((x - 10) // 20, (y - 9) // 20), module.TREES)
            self.assertEqual(len(module.TREES), len(set(module.TREES)))
        finally:
            if old_lcd is None:
                sys.modules.pop("lcd", None)
            else:
                sys.modules["lcd"] = old_lcd

    def test_score_only_increases_with_upward_progress(self):
        fake_lcd = types.ModuleType("lcd")
        fake_lcd.LCD = LCDStub
        fake_lcd.Keys = KeysStub
        fake_lcd.color = lambda r, g, b: (r, g, b)
        old_lcd = sys.modules.get("lcd")
        try:
            sys.modules["lcd"] = fake_lcd
            spec = importlib.util.spec_from_file_location("crossy_scoring", APP)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            best = 9
            self.assertEqual(module.score_value(best), 0)
            best = module.score_for_row(best, 169)
            self.assertEqual(module.score_value(best), 1)
            best = module.score_for_row(best, 189)
            self.assertEqual(module.score_value(best), 1)
            best = module.score_for_row(best, 149)
            self.assertEqual(module.score_value(best), 2)
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
        fake_save = types.ModuleType("save")
        fake_save.load = lambda name, default=0: default
        fake_save.store = lambda name, value: None
        fake_time = types.ModuleType("time")
        def sleep(ms):
            self.assertEqual(ms, 100)
            raise StopAfterFirstSleep()
        fake_time.sleep_ms = sleep
        old_lcd = sys.modules.get("lcd")
        old_time = sys.modules.get("time")
        old_save = sys.modules.get("save")
        try:
            sys.modules["lcd"] = fake_lcd
            sys.modules["time"] = fake_time
            sys.modules["save"] = fake_save
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
            if old_save is None:
                sys.modules.pop("save", None)
            else:
                sys.modules["save"] = old_save
            if old_time is None:
                sys.modules.pop("time", None)
            else:
                sys.modules["time"] = old_time
        self.assertIn(("text", "SCORE 0"), screen.calls)
        self.assertIn(("text", "SCORE 0"), screen.calls)
        self.assertIn(("text", "BEST 0"), screen.calls)
        self.assertNotIn(("text", "A RESET"), screen.calls)
        rects = [c for c in screen.calls if c[0] == "fill_rect"]
        self.assertGreaterEqual(len(rects), 18)
        # The HUD is one full-width rectangle at the top; road surfaces
        # may add other full-width rectangles as the world changes.
        self.assertEqual(len([c for c in rects if c[1:5] == (0, 0, 240, 20)]), 1)
        self.assertIn(("fill", (27, 105, 53)), screen.calls)
        self.assertTrue(all(0 <= c[1] and 0 <= c[2] and c[1] + c[3] <= 240 and c[2] + c[4] <= 240 for c in rects))
        self.assertEqual(sum(c[0] == "show" for c in screen.calls), 1)
        self.assertEqual(len(polls), 1)

if __name__ == "__main__":
    unittest.main()
