import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

SPEC = importlib.util.spec_from_file_location('phone', Path(__file__).parents[1] / 'tools' / 'thf_apps_phone_resources_v1.py')
phone = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(phone)


class PhoneResourcesTest(unittest.TestCase):
    def fixture(self, td: Path, pkg='com.topherofit.thf.core') -> Path:
        root = td / 'src'
        main = root / 'android/app/src/main'
        (main / 'res/values').mkdir(parents=True)
        (main / 'AndroidManifest.xml').write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            f'<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="{pkg}">'
            '<application android:label="Old"><activity android:name=".MainActivity"/></application></manifest>', encoding='utf-8')
        (main / 'res/values/strings.xml').write_text('<resources><string name="existing">Keep me</string><string name="app_name">Old</string></resources>', encoding='utf-8')
        return root

    def test_preserves_package_and_existing_strings(self):
        with tempfile.TemporaryDirectory() as t:
            root = self.fixture(Path(t))
            report = phone.apply(root, 'core', 'com.topherofit.thf.core', 'THF Hub')
            manifest = (root/'android/app/src/main/AndroidManifest.xml').read_text()
            strings = (root/'android/app/src/main/res/values/strings.xml').read_text()
            self.assertIn('com.topherofit.thf.core', manifest)
            self.assertIn('THF Hub', strings)
            self.assertIn('Keep me', strings)
            self.assertEqual(report['locale_count'], 20)
            self.assertFalse(report['final_or_play_ready'])
            self.assertFalse(report['functional_behavior_synthesized'])

    def test_adaptive_monochrome_and_store_icon_are_real_assets(self):
        with tempfile.TemporaryDirectory() as t:
            root = self.fixture(Path(t), 'com.topherofit.thf.vault')
            report = phone.apply(root, 'vault', 'com.topherofit.thf.vault', 'THF Wallet')
            res = root/'android/app/src/main/res'
            adaptive = (res/'mipmap-anydpi-v26/ic_launcher.xml').read_text()
            self.assertIn('<adaptive-icon', adaptive)
            self.assertIn('<monochrome', adaptive)
            store = root/'store-assets/google-play/icon-512.png'
            self.assertTrue(store.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))
            self.assertGreater(store.stat().st_size, 1024)
            self.assertEqual(hashlib.sha256(store.read_bytes()).hexdigest(), report['store_icon_sha256'])

    def test_package_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            root = self.fixture(Path(t), 'com.topherofit.thf.echo')
            with self.assertRaises(SystemExit):
                phone.apply(root, 'echo', 'com.topherofit.thf.wrong', 'THF Community')

    def test_all_approved_apps_have_distinct_store_assets(self):
        hashes = set()
        names = {
            'core':'THF Hub','forge':'THF Market','echo':'THF Community','codex':'THF Learn',
            'vault':'THF Wallet','signal':'THF Publisher','command':'THF Admin'}
        packages = {a:f'com.topherofit.thf.{a}' for a in names}
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            for app, name in names.items():
                root = self.fixture(base/app, packages[app])
                r = phone.apply(root, app, packages[app], name)
                hashes.add(r['store_icon_sha256'])
            self.assertEqual(len(hashes), len(names))

if __name__ == '__main__':
    unittest.main()
