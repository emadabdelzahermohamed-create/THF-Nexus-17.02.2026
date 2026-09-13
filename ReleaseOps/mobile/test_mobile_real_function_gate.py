#!/usr/bin/env python3
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

MODULE_PATH = Path(__file__).with_name('mobile_real_function_gate.py')
spec = importlib.util.spec_from_file_location('mobile_gate', MODULE_PATH)
gate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(gate)


def write_device(path: Path, sha: str, *, kind='app', online=True):
    d = {
        'exact_candidate_sha256': sha,
        'install_pass': True,
        'launch_pass': True,
        'touch_pass': True,
        'orientation_layout_pass': True,
        'background_resume_pass': True,
        'offline_network_transition_pass': True,
        'crash_free_smoke_pass': True,
        'core_user_journey_pass': True,
    }
    if online:
        d.update(backend_https_pass=True, backend_health_auth_pass=True)
    if kind == 'game':
        d.update(
            avatar_or_player_load_pass=True,
            movement_camera_pass=True,
            gameplay_interaction_pass=True,
            fps_ram_thermal_observed=True,
        )
    path.write_text(json.dumps(d), encoding='utf-8')


class MobileRealFunctionGateTests(unittest.TestCase):
    def test_device_evidence_must_match_exact_apk_sha(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'device.json'
            write_device(p, 'a' * 64)
            errs = gate.device_gate(p, 'app', True, 'b' * 64)
            self.assertTrue(any('SHA mismatch' in e for e in errs), errs)

    def test_device_evidence_matching_sha_passes_contract(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'device.json'
            sha = 'c' * 64
            write_device(p, sha)
            self.assertEqual(gate.device_gate(p, 'app', True, sha), [])

    def test_godot_engine_only_apk_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            apk = Path(td) / 'engine-only.apk'
            with zipfile.ZipFile(apk, 'w') as z:
                z.writestr('AndroidManifest.xml', b'manifest')
                z.writestr('lib/arm64-v8a/libgodot_android.so', b'godot')
            errs = gate.apk_payload_gate(apk, 'game')
            self.assertTrue(any('no exported game payload' in e for e in errs), errs)

    def test_godot_apk_with_payload_is_accepted_by_payload_gate(self):
        with tempfile.TemporaryDirectory() as td:
            apk = Path(td) / 'game.apk'
            with zipfile.ZipFile(apk, 'w') as z:
                z.writestr('AndroidManifest.xml', b'manifest')
                z.writestr('lib/arm64-v8a/libgodot_android.so', b'godot')
                z.writestr('assets/project.binary', b'project')
            self.assertEqual(gate.apk_payload_gate(apk, 'game'), [])

    def test_nested_godot_source_requires_sensor_landscape_expand_and_touch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'build.gradle').write_text('targetSdk = 36', encoding='utf-8')
            project = root / 'game'
            project.mkdir()
            (project / 'project.godot').write_text(
                'window/handheld/orientation=4\nwindow/stretch/aspect="expand"\n', encoding='utf-8'
            )
            (project / 'touch.gd').write_text('if event is InputEventScreenTouch:\n    pass\n', encoding='utf-8')
            self.assertEqual(gate.source_gate(root, 'game', False), [])

    def test_placeholder_network_configuration_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'build.gradle').write_text('targetSdk = 36', encoding='utf-8')
            (root / 'config.txt').write_text('YOUR-PRODUCTION-DOMAIN.example', encoding='utf-8')
            errs = gate.source_gate(root, 'app', True)
            self.assertTrue(any('placeholder' in e for e in errs), errs)


if __name__ == '__main__':
    unittest.main()
