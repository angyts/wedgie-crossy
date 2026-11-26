import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class LiveCameraPressureTests(unittest.TestCase):
    def test_pressure_boundaries(self):
        tree = ast.parse((ROOT / "crossy.py").read_text())
        helper = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                      and n.name == "pressure_rows")
        namespace = {}
        exec(compile(ast.Module(body=[helper], type_ignores=[]), "<pressure>", "exec"), namespace)
        pressure = namespace["pressure_rows"]
        for elapsed, expected in ((0,0),(4999,0),(5000,0),(5999,0),
                                  (6000,1),(6999,1),(7000,2),(15000,10)):
            self.assertEqual(pressure(elapsed), expected)

    def test_runtime_wiring(self):
        source = (ROOT / "crossy_runtime.py").read_text()
        ast.parse(source)
        self.assertIn("if target > row:", source)
        self.assertIn("world.advance(target)", source)
        self.assertIn('death_kind = "eagle"', source)
        self.assertIn("time.ticks_diff(time.ticks_ms(), paused_at)", source)
