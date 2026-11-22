"""Interpolation uses three clipped partial-refresh substeps."""
import ast
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class SmoothStepsTests(unittest.TestCase):
    def test_steps_and_no_full_flush(self):
        source=(ROOT/"crossy.py").read_text()
        tree=ast.parse(source)
        self.assertIn("SMOOTH_STEPS = (5, 10, 15)",source)
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="preview_traffic")
        calls=[n for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
        self.assertTrue(any(n.func.attr=="show_rect" for n in calls))
        self.assertFalse(any(n.func.attr=="show" for n in calls))
        self.assertTrue(any(n.func.attr=="pressed" for n in calls))
