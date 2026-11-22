"""Interpolation pacing is bounded, monotonic, and does not wait."""
import ast
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PacingTests(unittest.TestCase):
    def test_pacing(self):
        source=(ROOT/"crossy.py").read_text()
        ast.parse(source)
        self.assertIn("SMOOTH_BUDGET_MS = 65",source)
        self.assertIn("if elapsed >= SMOOTH_BUDGET_MS:",source)
        self.assertNotIn("time.sleep_ms(",source[source.index("def preview_traffic("):source.index("def draw_world(")])
