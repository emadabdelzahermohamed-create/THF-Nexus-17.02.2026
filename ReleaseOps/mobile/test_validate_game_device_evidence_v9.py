#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("device_evidence_v9", HERE / "validate_game_device_evidence_v9.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

T8SPEC = importlib.util.spec_from_file_location("device_evidence_v8_tests", HERE / "test_validate_game_device_evidence_v8.py")
T8 = importlib.util.module_from_spec(T8SPEC)
assert T8SPEC and T8SPEC.loader
sys.modules[T8SPEC.name] = T8
T8SPEC.loader.exec_module(T8)
V3 = MOD.V3


def evidence(product: str, registry_sha: str, root: Path):
    doc = T8.evidence(product, registry_sha, root)
    package = doc['package']
    data = (
        f"09-14 04:13:35.000 1234 1234 I THFGame: package={package} core_gameplay_started\n"
        f"09-14 04:14:20.000 1234 1234 I THFGame: package={package} core_gameplay_completed\n"
    ).encode()
    path = root / 'crash-logcat.txt'
    path.write_bytes(data)
    doc['crash_observation'] = {
        'session_id': doc['session']['session_id'],
        'package': package,
        'method': 'adb-logcat-pid-filter',
        'started_at_utc': '2026-09-14T04:13:35Z',
        'ended_at_utc': '2026-09-14T04:14:20Z',
        'crash_free': True,
        'process_alive_after_core_gameplay': True,
        'evidence_ref': 'crash-logcat.txt',
        'evidence_sha256': hashlib.sha256(data).hexdigest(),
    }
    return doc


class DeviceEvidenceV9Tests(unittest.TestCase):
    def test_all_six_accept_hash_bound_crash_free_logcat(self):
        reg=T8.T7.T6.registry_doc(); rsha='f'*64
        for product in V3.PRODUCT_MANUAL:
            with self.subTest(product=product), tempfile.TemporaryDirectory() as td:
                root=Path(td); doc=evidence(product,rsha,root)
                self.assertEqual([], MOD.validate_bundle(reg,rsha,doc,root))

    def test_missing_crash_record_fails(self):
        reg=T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('terra',rsha,root); doc.pop('crash_observation')
            self.assertTrue(any('missing record' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_tampered_logcat_fails_sha(self):
        reg=T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rift',rsha,root)
            (root/'crash-logcat.txt').write_text('tampered')
            self.assertTrue(any('evidence bytes mismatch' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_fatal_exception_marker_fails(self):
        reg=T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('spark',rsha,root)
            p=root/'crash-logcat.txt'; data=(p.read_text()+f"FATAL EXCEPTION: main {doc['package']}\n").encode(); p.write_bytes(data)
            doc['crash_observation']['evidence_sha256']=hashlib.sha256(data).hexdigest()
            self.assertTrue(any('fatal marker present: FATAL EXCEPTION' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_anr_marker_fails(self):
        reg=T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rush',rsha,root)
            p=root/'crash-logcat.txt'; data=(p.read_text()+f"ANR in {doc['package']}\n").encode(); p.write_bytes(data)
            doc['crash_observation']['evidence_sha256']=hashlib.sha256(data).hexdigest()
            self.assertTrue(any('fatal marker present: ANR in ' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_wrong_package_fails(self):
        reg=T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('learn_games',rsha,root)
            doc['crash_observation']['package']='com.example.fake'
            self.assertTrue(any('must match exact candidate package' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_package_absent_from_logcat_fails(self):
        reg=T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('fitness_games',rsha,root)
            p=root/'crash-logcat.txt'; data=b'09-14 04:14:00 I THFGame: unrelated process\n'; p.write_bytes(data)
            doc['crash_observation']['evidence_sha256']=hashlib.sha256(data).hexdigest()
            self.assertTrue(any('package identity absent' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_cross_session_fails(self):
        reg=T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('terra',rsha,root)
            doc['crash_observation']['session_id']='other-session'
            self.assertTrue(any('session_id mismatch' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_outside_session_interval_fails(self):
        reg=T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rift',rsha,root)
            doc['crash_observation']['ended_at_utc']='2026-09-14T05:14:20Z'
            self.assertTrue(any('outside declared session' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_process_must_still_be_alive(self):
        reg=T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('spark',rsha,root)
            doc['crash_observation']['process_alive_after_core_gameplay']=False
            self.assertTrue(any('process_alive_after_core_gameplay' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))


if __name__=='__main__': unittest.main()
