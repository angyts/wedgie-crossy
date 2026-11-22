"""No extra full-screen preview transfer on traffic updates."""
import ast
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class NoPreviewTests(unittest.TestCase):
    def test_single_traffic_render(self):
        source=(ROOT/"crossy.py").read_text()
        tree=ast.parse(source)
        self.assertNotIn("def draw_moving_preview(",source)
        self.assertNotIn("draw_moving_preview(",source)
        self.assertIn("dirty_rows=changed_hazard_rows(",source)
        self.assertIn("SMOOTH_TRAFFIC = False",source)
        draw=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="draw_world")
        shows=[n for n in ast.walk(draw) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="show"]
        self.assertEqual(len(shows),1)
