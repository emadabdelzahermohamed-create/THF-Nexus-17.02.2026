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


def write_device(path: Path, sha: str, *, kind='app', online=True, combat=False, sensor_motion=False):
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
    if combat:
        d['combat_pass'] = True
    if sensor_motion:
        d['sensor_motion_pass'] = True
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

    def test_combat_and_sensor_requirements_are_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'device.json'
            sha = 'd' * 64
            write_device(p, sha, kind='game')
            errs = gate.device_gate(p, 'game', False, sha, require_combat=True, require_sensor_motion=True)
            self.assertIn('combat_pass != true', errs)
            self.assertIn('sensor_motion_pass != true', errs)
            write_device(p, sha, kind='game', combat=True, sensor_motion=True)
            self.assertEqual(gate.device_gate(p, 'game', False, sha, require_combat=True, require_sensor_motion=True), [])

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

    def test_nested_godot_source_requires_sensor_landscape_expand_touch_and_allows_zero_overrides(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'build.gradle').write_text('targetSdk = 36', encoding='utf-8')
            project = root / 'game'
            project.mkdir()
            (project / 'project.godot').write_text(
                '[display]\n'
                'window/handheld/orientation=4\n'
                'window/stretch/aspect="expand"\n'
                'window/size/window_width_override=0\n'
                'window/size/window_height_override=0\n', encoding='utf-8'
            )
            (project / 'touch.gd').write_text('if event is InputEventScreenTouch:\n    pass\n', encoding='utf-8')
            self.assertEqual(gate.source_gate(root, 'game', False), [])

    def test_active_desktop_override_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'build.gradle').write_text('targetSdk = 36', encoding='utf-8')
            project = root / 'game'
            project.mkdir()
            (project / 'project.godot').write_text(
                '[display]\n'
                'window/handheld/orientation=4\n'
                'window/stretch/aspect="expand"\n'
                'window/size/window_width_override=1920\n', encoding='utf-8'
            )
            (project / 'touch.gd').write_text('InputEventScreenTouch', encoding='utf-8')
            errs = gate.source_gate(root, 'game', False)
            self.assertTrue(any('desktop window override is active' in e for e in errs), errs)

    def test_placeholder_network_configuration_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'build.gradle').write_text('targetSdk = 36', encoding='utf-8')
            (root / 'config.txt').write_text('YOUR-PRODUCTION-DOMAIN.example', encoding='utf-8')
            errs = gate.source_gate(root, 'app', True)
            self.assertTrue(any('placeholder' in e for e in errs), errs)


if __name__ == '__main__':
    unittest.main()
