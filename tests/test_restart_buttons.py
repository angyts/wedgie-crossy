"""Any recognized game button restarts after death."""
import ast
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RestartButtonsTests(unittest.TestCase):
    def test_all_buttons_restart(self):
        source=(ROOT/"crossy.py").read_text()
        ast.parse(source)
        self.assertIn('if key in ("A", "B", "Y", "up", "down", "left", "right"):',source)
        self.assertIn('seed = new_run_seed(time.ticks_ms())',source)
