import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC=importlib.util.spec_from_file_location('echo_patch',Path(__file__).parents[1]/'tools'/'thf_echo_remove_placeholder_demo_v1.py')
mod=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(mod)

class EchoPlaceholderPatchTest(unittest.TestCase):
    def test_removes_only_exact_seeded_demo(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); p=root/'app/main.py'; p.parent.mkdir(parents=True)
            p.write_text('before\n'+mod.OLD+'after\n',encoding='utf-8')
            mod.apply(root)
            s=p.read_text(encoding='utf-8')
            self.assertNotIn('https://example.com',s)
            self.assertNotIn('THF Native Demo',s)
            self.assertIn("No synthetic/default ad campaign",s)
            self.assertIn('before',s); self.assertIn('after',s)

    def test_anchor_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); p=root/'app/main.py'; p.parent.mkdir(parents=True); p.write_text('no known anchor',encoding='utf-8')
            with self.assertRaises(SystemExit): mod.apply(root)

    def test_multiple_main_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for base in ('one','two'):
                p=root/base/'app/main.py'; p.parent.mkdir(parents=True); p.write_text(mod.OLD,encoding='utf-8')
            with self.assertRaises(SystemExit): mod.apply(root)

if __name__=='__main__': unittest.main()
