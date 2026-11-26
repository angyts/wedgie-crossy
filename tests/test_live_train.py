import unittest
import crossy_worldgen as w

class LiveTrainTests(unittest.TestCase):
    def test_cycle_and_sweep(self):
        for seed in range(20):
            row = 42
            stages = [w.train_stage(seed,row,p) for p in range(w.TRAIN_PERIOD)]
            self.assertEqual(stages.count(1),8)
            self.assertEqual(stages.count(2),4)
            union = 0
            for p in range(w.TRAIN_PERIOD):
                mask = w.train_mask(seed,row,p)
                union |= mask
                if stages[p] != 2:
                    self.assertEqual(mask,0)
                    continue
                for step in range(21):
                    x = w.train_left(seed,row,p,step)
                    for col in range(w.WIDTH):
                        if col*20 < x+w.TRAIN_LENGTH and (col+1)*20 > x:
                            self.assertTrue(mask & (1<<col))
            self.assertEqual(union,w.MASK)

    def test_grass_banks(self):
        old = w.RAILWAYS
        try:
            w.RAILWAYS = True
            found = 0
            for seed in range(20):
                for row in range(32,240):
                    if w.section(seed,row)[0] == "rail":
                        found += 1
                        self.assertEqual(w.section(seed,row-1)[0],"grass")
                        self.assertEqual(w.section(seed,row+1)[0],"grass")
            self.assertGreater(found,0)
        finally:
            w.RAILWAYS = old
