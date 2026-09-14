#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('capture_installed_identity',HERE/'capture_installed_apk_identity_v1.py')
MOD=importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name]=MOD
SPEC.loader.exec_module(MOD)

SERIAL='RF8N1234ABCD'
PROPS={
    'ro.build.fingerprint':'vendor/device/build:16/ABC/123:user/release-keys',
    'ro.product.model':'THF Physical Test Phone',
    'ro.product.manufacturer':'Vendor',
}
APK=b'not-a-real-apk-but-byte-identity-test'
APK_SHA=hashlib.sha256(APK).hexdigest()
PATH='/data/app/~~AbCdEf/com.topherofit.thf.terra-XyZ/base.apk'


def fingerprint():
    raw='\n'.join((SERIAL,PROPS['ro.build.fingerprint'],PROPS['ro.product.model'],PROPS['ro.product.manufacturer']))
    return hashlib.sha256(raw.encode()).hexdigest()


def make_bundle(root: Path):
    cap=root/'evidence/terra/objective.txt'; cap.parent.mkdir(parents=True,exist_ok=True); cap.write_text('initial objective capture\n')
    doc={
        'package':'com.topherofit.thf.terra','exact_candidate_sha256':APK_SHA,
        'device':{'fingerprint_sha256':fingerprint()},
        'session':{'session_id':'phone-session-20260914-v7-test'},
        'objective':{'evidence_ref':'evidence/terra/objective.txt','evidence_sha256':hashlib.sha256(cap.read_bytes()).hexdigest(),'package_dump_present':True},
        'final_or_play_ready':False,
    }
    ep=root/'evidence.json'; ep.write_text(json.dumps(doc))
    return ep,cap


class CaptureInstalledIdentityTests(unittest.TestCase):
    def test_parse_pm_paths(self):
        self.assertEqual(['/data/app/a/base.apk','/data/app/a/split.apk'],MOD.parse_pm_paths('package:/data/app/a/base.apk\npackage:/data/app/a/split.apk\n'))

    def test_success_binds_installed_bytes_and_rehashes_objective_capture(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); ep,cap=make_bundle(root)
            pm=types.SimpleNamespace(returncode=0,stdout='package:'+PATH+'\n')
            with patch.object(MOD.V3CAP,'one_device',return_value=SERIAL), \
                 patch.object(MOD.V3CAP,'detect_emulator',return_value=(False,PROPS)), \
                 patch.object(MOD.V3CAP,'shell',return_value=pm), \
                 patch.object(MOD,'binary_exec',return_value=APK):
                result=MOD.bind_identity(ep,root,'adb')
            doc=json.loads(ep.read_text())
            self.assertEqual(APK_SHA,result['installed_apk_sha256'])
            self.assertTrue(doc['objective']['installed_apk_sha_verified'])
            self.assertEqual(APK_SHA,doc['objective']['installed_apk_sha256'])
            self.assertEqual([PATH],doc['objective']['installed_code_paths'])
            self.assertEqual('adb-exec-out-cat',doc['objective']['installed_apk_hash_method'])
            self.assertEqual(hashlib.sha256(cap.read_bytes()).hexdigest(),doc['objective']['evidence_sha256'])
            self.assertFalse(result['final_or_play_ready'])

    def test_wrong_connected_phone_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); ep,_=make_bundle(root)
            with patch.object(MOD.V3CAP,'one_device',return_value='OTHERDEVICE'), \
                 patch.object(MOD.V3CAP,'detect_emulator',return_value=(False,PROPS)):
                with self.assertRaisesRegex(RuntimeError,'does not match evidence device fingerprint'):
                    MOD.bind_identity(ep,root,'adb')

    def test_split_install_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); ep,_=make_bundle(root)
            pm=types.SimpleNamespace(returncode=0,stdout='package:'+PATH+'\npackage:/data/app/~~AbCdEf/split_config.arm64_v8a.apk\n')
            with patch.object(MOD.V3CAP,'one_device',return_value=SERIAL), \
                 patch.object(MOD.V3CAP,'detect_emulator',return_value=(False,PROPS)), \
                 patch.object(MOD.V3CAP,'shell',return_value=pm):
                with self.assertRaisesRegex(RuntimeError,'exactly one installed base APK required'):
                    MOD.bind_identity(ep,root,'adb')

    def test_installed_byte_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); ep,_=make_bundle(root)
            pm=types.SimpleNamespace(returncode=0,stdout='package:'+PATH+'\n')
            with patch.object(MOD.V3CAP,'one_device',return_value=SERIAL), \
                 patch.object(MOD.V3CAP,'detect_emulator',return_value=(False,PROPS)), \
                 patch.object(MOD.V3CAP,'shell',return_value=pm), \
                 patch.object(MOD,'binary_exec',return_value=b'different-installed-bytes'):
                with self.assertRaisesRegex(RuntimeError,'installed APK SHA mismatch'):
                    MOD.bind_identity(ep,root,'adb')


if __name__=='__main__': unittest.main()
