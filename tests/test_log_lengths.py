"""Log lengths vary by lane, remain deterministic and bounded."""
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
                self.assertIn(length,(3,4,5))
                self.assertEqual(w.log_mask(seed,row,0),w.log_mask(seed,row,24))
        self.assertEqual(lengths,{3,4,5})
