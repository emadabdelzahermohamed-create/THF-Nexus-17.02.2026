#!/usr/bin/env python3
import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

MODULE_PATH = Path(__file__).with_name('capture_android_device_evidence_v2.py')
spec = importlib.util.spec_from_file_location('capture_device', MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class DeviceCollectorTests(unittest.TestCase):
    def test_sha_mismatch_fails_before_adb(self):
        with tempfile.TemporaryDirectory() as td:
            apk = Path(td) / 'candidate.apk'
            apk.write_bytes(b'candidate')
            args = argparse.Namespace(
                apk=str(apk), expected_sha256='0' * 64, adb='adb',
                product='THF Test', package='com.example.test'
            )
            with self.assertRaisesRegex(RuntimeError, 'exact candidate SHA mismatch'):
                mod.collect(args)

    def test_one_device_requires_exactly_one_authorized_device(self):
        original = mod.run
        try:
            mod.run = lambda *a, **k: SimpleNamespace(returncode=0, stdout='List of devices attached\nabc\tdevice\ndef\tdevice\n')
            with self.assertRaisesRegex(RuntimeError, 'exactly one authorized adb device required'):
                mod.one_device('adb')
            mod.run = lambda *a, **k: SimpleNamespace(returncode=0, stdout='List of devices attached\nabc\tdevice\n')
            self.assertEqual(mod.one_device('adb'), 'abc')
        finally:
            mod.run = original

    def test_objective_capture_never_auto_promotes_manual_gameplay_gates(self):
        source = MODULE_PATH.read_text(encoding='utf-8')
        for key in (
            "'touch_pass': False",
            "'orientation_layout_pass': False",
            "'offline_network_transition_pass': False",
            "'core_user_journey_pass': False",
            "'gameplay_interaction_pass': False",
            "'combat_pass': False",
            "'sensor_motion_pass': False",
        ):
            self.assertIn(key, source)


if __name__ == '__main__':
    unittest.main()
