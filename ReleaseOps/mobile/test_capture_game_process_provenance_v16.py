#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, sys, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
S = importlib.util.spec_from_file_location('capturev16', HERE / 'capture_game_process_provenance_v16.py')
M = importlib.util.module_from_spec(S); sys.modules[S.name] = M; S.loader.exec_module(M)
T = importlib.util.spec_from_file_location('t16', HERE / 'test_validate_game_device_evidence_v16.py')
T16 = importlib.util.module_from_spec(T); sys.modules[T.name] = T16; T.loader.exec_module(T16)

SERIAL = 'PHONE123456'
PROPS = {
    'ro.build.fingerprint': 'vendor/device/product:16/BUILD/123:user/release-keys',
    'ro.product.model': 'THF Test Phone',
    'ro.product.manufacturer': 'THF Vendor',
    'ro.kernel.qemu': '0',
    'ro.boot.qemu': '0',
    'ro.hardware': 'physical-arm64',
}


def expected_fp():
    identity = '\n'.join((SERIAL, PROPS['ro.build.fingerprint'], PROPS['ro.product.model'], PROPS['ro.product.manufacturer']))
    return hashlib.sha256(identity.encode()).hexdigest()


def cp(code=0, out=''):
    return SimpleNamespace(returncode=code, stdout=out)


def fake_run_factory(package, foreground=True, pid_code=0):
    def fake(cmd, timeout=30):
        if cmd[-1] == 'devices':
            return cp(0, 'List of devices attached\n' + SERIAL + '\tdevice\n')
        if 'getprop' in cmd:
            return cp(0, PROPS[cmd[-1]] + '\n')
        if cmd[-3:] == ['dumpsys', 'activity', 'activities']:
            shown = package if foreground else 'com.other.app'
            return cp(0, 'mResumedActivity: ActivityRecord{abc u0 ' + shown + '/.MainActivity t42}\n')
        if len(cmd) >= 2 and cmd[-2] == 'pidof':
            return cp(pid_code, '4321\n' if pid_code == 0 else '')
        return cp(1, 'unexpected command')
    return fake


def make_evidence(root: Path, product='terra'):
    rsha = 'f' * 64
    d = T16.evidence(product, rsha, root)
    d['device']['fingerprint_sha256'] = expected_fp()
    path = root / 'evidence.json'
    path.write_text(json.dumps(d, indent=2), encoding='utf-8')
    return d, path


class CaptureV16(unittest.TestCase):
    def test_capture_passes_and_emits_exact_bindings(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d, evidence_path = make_evidence(root)
            old = M.run; M.run = fake_run_factory(d['package'])
            try:
                out = root / 'captured_process.txt'
                result = M.capture(evidence_path, 'gameplay_interaction', root, out, 'adb')
            finally:
                M.run = old
            text = out.read_text()
            self.assertEqual('CAPTURED_V16_PROCESS_PROVENANCE', result['status'])
            self.assertIn('THF_DEVICE_FINGERPRINT_SHA256=' + expected_fp(), text)
            self.assertIn('THF_EXACT_APK_SHA256=' + d['exact_candidate_sha256'], text)
            self.assertIn('THF_REGISTRY_SHA256=' + d['registry_sha256'], text)
            self.assertIn('THF_FOREGROUND_PID=4321', text)
            self.assertFalse(result['final_or_play_ready'])

    def test_wrong_physical_device_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d, evidence_path = make_evidence(root); d['device']['fingerprint_sha256'] = '0' * 64; evidence_path.write_text(json.dumps(d))
            old = M.run; M.run = fake_run_factory(d['package'])
            try:
                with self.assertRaisesRegex(RuntimeError, 'fingerprint does not match'):
                    M.capture(evidence_path, 'gameplay_interaction', root, root / 'out.txt', 'adb')
            finally: M.run = old

    def test_background_package_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d, evidence_path = make_evidence(root)
            old = M.run; M.run = fake_run_factory(d['package'], foreground=False)
            try:
                with self.assertRaisesRegex(RuntimeError, 'not the resumed foreground'):
                    M.capture(evidence_path, 'gameplay_interaction', root, root / 'out.txt', 'adb')
            finally: M.run = old

    def test_pidof_failure_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d, evidence_path = make_evidence(root)
            old = M.run; M.run = fake_run_factory(d['package'], pid_code=1)
            try:
                with self.assertRaisesRegex(RuntimeError, 'pidof failed'):
                    M.capture(evidence_path, 'gameplay_interaction', root, root / 'out.txt', 'adb')
            finally: M.run = old

    def test_tampered_gameplay_evidence_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d, evidence_path = make_evidence(root)
            gameplay = root / d['manual_observations']['gameplay_interaction']['evidence_ref']
            gameplay.write_text(gameplay.read_text() + 'tamper\n')
            old = M.run; M.run = fake_run_factory(d['package'])
            try:
                with self.assertRaisesRegex(RuntimeError, 'gameplay evidence SHA mismatch'):
                    M.capture(evidence_path, 'gameplay_interaction', root, root / 'out.txt', 'adb')
            finally: M.run = old


if __name__ == '__main__':
    unittest.main()
