"""Traffic updates use partial redraws without replaying the old preview."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NoPreviewTests(unittest.TestCase):
    def test_single_traffic_render(self):
        runtime = (ROOT / "crossy_runtime.py").read_text()
        graphics = (ROOT / "crossy.py").read_text()
        ast.parse(runtime)
        tree = ast.parse(graphics)
        self.assertIn("dirty_rows=changed_hazard_rows(", runtime)
        self.assertNotIn("captured = preview_traffic(", runtime)
        self.assertIn("SMOOTH_TRAFFIC = True", graphics)
        draw = next(n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "draw_world")
        shows = [n for n in ast.walk(draw)
                 if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute)
                 and n.func.attr == "show"]
        self.assertEqual(len(shows), 1)
