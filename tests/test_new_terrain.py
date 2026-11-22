"""Multi-lane roads and stationary lily-pad tests."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

class NewTerrainTests(unittest.TestCase):
    def test_lilies_and_road_lanes(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_terrain",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            self.assertTrue(m.is_river(12))
            self.assertTrue(m.on_lily(12,5))
            self.assertTrue(m.water_supported(12,5,0))
            self.assertFalse(m.on_lily(12,6))
            self.assertFalse(m.is_road(7))
            self.assertTrue(m.is_road(42))
            self.assertTrue(m.is_road(43))
            self.assertNotEqual(m.traffic_direction(42),m.traffic_direction(43))
            self.assertEqual(m.row_mask(123,43),0)
            self.assertNotEqual(m.car_color(42,2),m.car_color(42,5))
            self.assertTrue(m.DEV_MODE)
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old
