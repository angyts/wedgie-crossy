"""Ensure Wedgie-prefixed generator remains accessible via the runtime alias."""
import ast
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class GeneratorImportTests(unittest.TestCase):
    def test_runtime_import_alias_and_manifest(self):
        source=(ROOT/"crossy.py").read_text()
        tree=ast.parse(source)
        aliases=[alias for node in tree.body if isinstance(node,ast.Import)
                 for alias in node.names if alias.name=="crossy_worldgen"]
        self.assertEqual(len(aliases),1)
        self.assertEqual(aliases[0].asname,"worldgen")
        self.assertTrue((ROOT/"crossy_worldgen.py").is_file())
        import json
        manifest=json.loads((ROOT/"wedgie.json").read_text())
        self.assertIn("crossy_worldgen.py",manifest["apps"][0]["files"])
