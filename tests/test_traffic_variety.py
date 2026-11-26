"""Traffic variety must remain deterministic, unsynchronized and collision-consistent."""
import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("traffic_worldgen",ROOT/"crossy_worldgen.py")
w=importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
class TrafficVarietyTests(unittest.TestCase):
    def test_lane_motion_and_wrap(self):
        directions=set()
        periods=set()
        same=opposite=0
        for seed in range(100):
            for block in range(12):
                start=8+block*w.BLOCK
                kind,lane,width=w.section(seed,start)
                if kind!="road":continue
                self.assertEqual(lane,0)
                self.assertTrue(1<=width<=8)
                self.assertTrue(all(w.section(seed,start+i)[0] in ("road","logs") for i in range(width)))
                self.assertEqual(w.section(seed,start+width-1)[0],"road")
                for row in range(start,start+width):
                    if w.section(seed,row)[0] != "road":
                        self.assertEqual(w.road_mask(seed,row,0),0)
                        continue
                    d=w.road_direction(seed,row)
                    period=w.road_period(seed,row)
                    directions.add(d);periods.add(period)
                    for phase in range(24):
                        mask=w.road_mask(seed,row,phase)
                        self.assertEqual(w.count_bits(mask),2)
                        self.assertEqual(mask,w.road_mask(seed,row,phase+24))
                        before=w.road_position(seed,row,phase)
                        after=w.road_position(seed,row,phase+1)
                        self.assertIn(after-before,(0,d))
                for row in range(start,start+width-1):
                    if any(w.section(seed,r)[0] != "road" for r in (row,row+1)):
                        continue
                    if w.road_direction(seed,row)==w.road_direction(seed,row+1):
                        same+=1
                    else:opposite+=1
        self.assertEqual(directions,{-1,1})
        self.assertEqual(periods,{1,2})
        self.assertGreater(same,0)
        self.assertGreater(opposite,0)
