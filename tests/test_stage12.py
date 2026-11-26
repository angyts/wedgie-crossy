"""Traffic direction, phase, collision, pause clock and development mode tests."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path

class TrafficTests(unittest.TestCase):
    def test_moving_traffic_and_dev_mode(self):
        lcd=types.ModuleType("lcd")
        lcd.LCD=object
        lcd.Keys=object
        lcd.color=lambda r,g,b:(r,g,b)
        old=sys.modules.get("lcd")
        try:
            sys.modules["lcd"]=lcd
            spec=importlib.util.spec_from_file_location("crossy_traffic",Path(__file__).resolve().parents[1]/"crossy.py")
            m=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            self.assertFalse(m.DEV_MODE)
            self.assertEqual(m.traffic_direction(6),1)
            self.assertEqual(m.traffic_direction(18),-1)
            self.assertEqual(m.moving_car_mask(123,6,0),m.car_mask(123,6))
            self.assertNotEqual(m.moving_car_mask(123,6,1),m.car_mask(123,6))
            self.assertEqual(m.moving_car_mask(123,6,12),m.car_mask(123,6))
            self.assertTrue(m.road_hit(123,6,2,0))
            self.assertFalse(m.road_hit(123,6,2,1))
            self.assertTrue(m.traffic_sweep_hit(123,6,2,0,1))
            self.assertFalse(m.traffic_sweep_hit(123,7,2,0,1))
        finally:
            if old is None:sys.modules.pop("lcd",None)
            else:sys.modules["lcd"]=old

if __name__=="__main__":
    unittest.main()
