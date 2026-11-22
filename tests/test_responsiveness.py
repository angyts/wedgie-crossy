"""Input responsiveness: poll before LCD work and retain traffic timing."""
import ast
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ResponsivenessTests(unittest.TestCase):
    def test_pre_render_poll_and_short_idle(self):
        src=(ROOT/"crossy.py").read_text()
        self.assertIn("early_inputs = keys.pressed()",src)
        self.assertIn("time.sleep_ms(10)",src)
        self.assertIn("traffic_interval(score) * FRAME_MS",src)
        loop=src.index("        while True:\n",src.index("def run():"))
        pre=src.index("early_inputs = keys.pressed()",loop)
        traffic=src.index("if not paused and not dead and traffic_due(",loop)
        self.assertLess(pre,traffic)
        ast.parse(src)
