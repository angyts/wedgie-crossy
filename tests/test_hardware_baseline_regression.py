"""Regression checks for the hardware-accepted rendering and packaging rules.

These checks intentionally avoid importing firmware-only lcd/save modules.
"""
import ast
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class HardwareBaselineRegression(unittest.TestCase):
    def test_manifest_contains_every_crossy_runtime_import(self):
        manifest = json.loads((ROOT / "wedgie.json").read_text())
        files = set(manifest["apps"][0]["files"])
        self.assertTrue(all(name == "crossy.py" or name.startswith("crossy_")
                            for name in files))
        self.assertTrue(all((ROOT / name).is_file() for name in files))
        for name in ("crossy.py", "crossy_runtime.py"):
            tree = ast.parse((ROOT / name).read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("crossy_"):
                    self.assertIn(node.module + ".py", files)
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith("crossy_"):
                            self.assertIn(alias.name + ".py", files)

    def test_lazy_entry_preserved(self):
        source = (ROOT / "crossy.py").read_text()
        tree = ast.parse(source)
        run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run")
        self.assertTrue(any(isinstance(n, ast.ImportFrom) and n.module == "crossy_runtime"
                            for n in ast.walk(run)))

    def test_hud_and_log_partial_flush_guards(self):
        source = (ROOT / "crossy.py").read_text()
        self.assertIn("if screen_row == WINDOW - 1:", source)
        self.assertIn("if absolute == world.first + WINDOW - 1:", source)
        self.assertIn('if previous_phase is not None and kind == "logs":', source)

    def test_no_blocking_log_carry_in_runtime(self):
        source = (ROOT / "crossy_runtime.py").read_text()
        self.assertNotIn("captured = animate_log_carry(", source)
        self.assertIn("dirty_rows=dirty", source)


if __name__ == "__main__":
    unittest.main()
