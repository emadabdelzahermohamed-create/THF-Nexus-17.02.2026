#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("device_evidence_v7", HERE / "validate_game_device_evidence_v7.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

T6SPEC = importlib.util.spec_from_file_location("device_evidence_v6_tests", HERE / "test_validate_game_device_evidence_v6.py")
T6 = importlib.util.module_from_spec(T6SPEC)
assert T6SPEC and T6SPEC.loader
sys.modules[T6SPEC.name] = T6
T6SPEC.loader.exec_module(T6)
V3 = MOD.V3


def evidence(product: str, registry_sha: str, root: Path):
    doc = T6.evidence(product, registry_sha, root)
    doc['objective'].update({
        'installed_apk_sha256': doc['exact_candidate_sha256'],
        'installed_apk_sha_verified': True,
        'installed_code_paths': ['/data/app/~~abc/base.apk'],
        'installed_apk_hash_method': 'adb-exec-out-cat',
        'package_dump_present': True,
        'installed_apk_session_id': doc['session']['session_id'],
        'installed_apk_observed_at_utc': '2026-09-14T04:13:30Z',
    })
    return doc


class DeviceEvidenceV7Tests(unittest.TestCase):
    def test_all_six_accept_installed_byte_identity(self):
        reg=T6.registry_doc(); rsha='f'*64
        for product in V3.PRODUCT_MANUAL:
            with self.subTest(product=product), tempfile.TemporaryDirectory() as td:
                root=Path(td); doc=evidence(product,rsha,root)
                self.assertEqual([], MOD.validate_bundle(reg,rsha,doc,root))

    def test_installed_sha_mismatch_fails(self):
        reg=T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('terra',rsha,root)
            doc['objective']['installed_apk_sha256']='0'*64
            self.assertTrue(any('installed bytes do not match exact candidate' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_verified_boolean_required(self):
        reg=T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rift',rsha,root)
            doc['objective']['installed_apk_sha_verified']=False
            self.assertTrue(any('installed_apk_sha_verified' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_split_or_multiple_code_paths_fail(self):
        reg=T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('spark',rsha,root)
            doc['objective']['installed_code_paths']=['/data/app/~~abc/base.apk','/data/app/~~abc/split_config.arm64_v8a.apk']
            self.assertTrue(any('exactly one installed base APK required' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_non_physical_code_path_fails(self):
        reg=T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rush',rsha,root)
            doc['objective']['installed_code_paths']=['/sdcard/Download/base.apk']
            self.assertTrue(any('physical /data/app/' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_unapproved_hash_method_fails(self):
        reg=T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('learn_games',rsha,root)
            doc['objective']['installed_apk_hash_method']='typed-json'
            self.assertTrue(any('approved byte-read method' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_package_dump_required(self):
        reg=T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('fitness_games',rsha,root)
            doc['objective']['package_dump_present']=False
            self.assertTrue(any('package_dump_present' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_installed_identity_cross_session_fails(self):
        reg=T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('terra',rsha,root)
            doc['objective']['installed_apk_session_id']='other-phone-session-20260914'
            self.assertTrue(any('installed_apk_session_id: session_id mismatch' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_installed_identity_outside_session_fails(self):
        reg=T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rift',rsha,root)
            doc['objective']['installed_apk_observed_at_utc']='2026-09-14T05:00:00Z'
            self.assertTrue(any('installed_apk_observed_at_utc: observation outside' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))


if __name__=='__main__': unittest.main()
