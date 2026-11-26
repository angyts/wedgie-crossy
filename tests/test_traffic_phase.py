"""Regression tests for the yellow-car row-30 phase jump."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

class TrafficPhaseTests(unittest.TestCase):
    def test_score_transition_does_not_teleport(self):
        lcd = types.ModuleType("lcd")
        lcd.LCD = object
        lcd.Keys = object
        lcd.color = lambda r,g,b: (r,g,b)
        old = sys.modules.get("lcd")
        try:
            sys.modules["lcd"] = lcd
            spec = importlib.util.spec_from_file_location(
                "crossy_phase", Path(__file__).resolve().parents[1] / "crossy.py")
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            self.assertEqual(m.traffic_interval(29), 3)
            self.assertEqual(m.traffic_interval(30), 2)
            phase = 20
            self.assertEqual(m.next_traffic_phase(phase), 21)
            before = m.moving_car_mask(123, 30, phase)
            after = m.moving_car_mask(123, 30, m.next_traffic_phase(phase))
            self.assertEqual(after, m.moving_car_mask(123, 30, 21))
            self.assertNotEqual(before, after)
            self.assertEqual(m.next_traffic_phase(21), 22)
            self.assertFalse(m.DEV_MODE)
        finally:
            if old is None:
                sys.modules.pop("lcd", None)
            else:
                sys.modules["lcd"] = old

if __name__ == "__main__":
    unittest.main()
