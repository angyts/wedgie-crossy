"""Short log lengths vary by lane and remain deterministic."""
import unittest
import crossy_worldgen as w
class LogLengthsTests(unittest.TestCase):
    def test_lengths(self):
        lengths=set()
        for seed in range(100):
            for row in range(8,160):
                if w.section(seed,row)[0]!="logs":continue
                length=w.log_length(seed,row)
                lengths.add(length)
                self.assertIn(length,(2,3))
                self.assertEqual(w.log_mask(seed,row,0),w.log_mask(seed,row,24))
        self.assertEqual(lengths,{2,3})
