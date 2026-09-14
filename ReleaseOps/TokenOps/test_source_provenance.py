#!/usr/bin/env python3
import importlib.util
import pathlib
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("source_provenance", HERE / "source_provenance.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class SourceProvenanceTests(unittest.TestCase):
    def _tree(self, root: pathlib.Path, suffix: str = "") -> None:
        for rel in M.INVENTORY:
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(rel + suffix + "\n")

    def test_provenance_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._tree(root)
            a = M.build_provenance(root, "a" * 40)
            b = M.build_provenance(root, "a" * 40)
            self.assertEqual(a["tokenops_source_root_sha256"], b["tokenops_source_root_sha256"])
            self.assertEqual(a["provenance_sha256"], b["provenance_sha256"])

    def test_one_byte_change_changes_root_digest(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._tree(root)
            before = M.build_provenance(root)["tokenops_source_root_sha256"]
            target = root / M.INVENTORY[0]
            target.write_text(target.read_text() + "x")
            after = M.build_provenance(root)["tokenops_source_root_sha256"]
            self.assertNotEqual(before, after)

    def test_missing_inventory_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._tree(root)
            (root / M.INVENTORY[-1]).unlink()
            with self.assertRaises(ValueError):
                M.build_provenance(root)

    def test_wave_is_explicitly_outside_inventory(self):
        self.assertFalse(any("wave" in rel.lower() for rel in M.INVENTORY))


if __name__ == "__main__":
    unittest.main(verbosity=2)
