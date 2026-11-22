"""Input is sampled before a visual frame can be dropped for lateness."""
import ast
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class AnimationInputBudgetTests(unittest.TestCase):
    def test_poll_precedes_budget_check(self):
        source=(ROOT/"crossy.py").read_text()
        ast.parse(source)
        fn=source[source.index("def preview_traffic("):source.index("def draw_world(")]
        self.assertLess(fn.index("pressed = keys.pressed()"),fn.index("if elapsed >= SMOOTH_BUDGET_MS:"))
        self.assertIn("return pressed[0]",fn)
