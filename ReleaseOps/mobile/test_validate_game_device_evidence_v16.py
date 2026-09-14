#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = importlib.util.spec_from_file_location('v16', HERE / 'validate_game_device_evidence_v16.py')
M = importlib.util.module_from_spec(S); sys.modules[S.name] = M; S.loader.exec_module(M)
T = importlib.util.spec_from_file_location('t15', HERE / 'test_validate_game_device_evidence_v15.py')
T15 = importlib.util.module_from_spec(T); sys.modules[T.name] = T15; T.loader.exec_module(T)
V3 = M.V3


def evidence(product, rsha, root):
    d = T15.evidence(product, rsha, root)
    req = dict(T15.T14.M.BASE); req.update(T15.T14.M.PRODUCT.get(product, {}))
    for key in req:
        row = d['process_provenance'][key]
        p = root / row['evidence_ref']
        gameplay = d['manual_observations'][key]
        extra = '\n'.join([
            'THF_DEVICE_FINGERPRINT_SHA256=' + d['device']['fingerprint_sha256'],
            'THF_EXACT_APK_SHA256=' + d['exact_candidate_sha256'],
            'THF_REGISTRY_SHA256=' + rsha,
            'THF_OBSERVED_AT_UTC=' + gameplay['observed_at_utc'],
            'THF_ACTIVITY_DUMPSYS_EXIT_CODE=0',
            'THF_PIDOF_EXIT_CODE=0',
            '',
        ])
        p.write_text(p.read_text(encoding='utf-8') + extra, encoding='utf-8')
        row['evidence_sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()
    return d


def mutate(d, root, key, old, new):
    row = d['process_provenance'][key]
    p = root / row['evidence_ref']
    p.write_text(p.read_text(encoding='utf-8').replace(old, new), encoding='utf-8')
    row['evidence_sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()


class V16(unittest.TestCase):
    def setUp(self):
        self.reg = T15.T14.T13.T12.T11.T10.T9.T8.T7.T6.registry_doc()
        self.rsha = 'f' * 64

    def test_all_six_pass(self):
        for product in V3.PRODUCT_MANUAL:
            with self.subTest(product=product), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                self.assertEqual([], M.validate_bundle(self.reg, self.rsha, evidence(product, self.rsha, root), root))

    def test_device_fingerprint_substitution_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d = evidence('terra', self.rsha, root); key = 'gameplay_interaction'
            good = d['device']['fingerprint_sha256']
            mutate(d, root, key, 'THF_DEVICE_FINGERPRINT_SHA256=' + good, 'THF_DEVICE_FINGERPRINT_SHA256=' + '0' * 64)
            self.assertTrue(any('THF_DEVICE_FINGERPRINT_SHA256 mismatch' in x for x in M.validate_bundle(self.reg, self.rsha, d, root)))

    def test_exact_apk_substitution_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d = evidence('rift', self.rsha, root); key = 'combat'
            good = d['exact_candidate_sha256']
            mutate(d, root, key, 'THF_EXACT_APK_SHA256=' + good, 'THF_EXACT_APK_SHA256=' + '0' * 64)
            self.assertTrue(any('THF_EXACT_APK_SHA256 mismatch' in x for x in M.validate_bundle(self.reg, self.rsha, d, root)))

    def test_registry_substitution_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d = evidence('spark', self.rsha, root); key = 'learning_progression'
            mutate(d, root, key, 'THF_REGISTRY_SHA256=' + self.rsha, 'THF_REGISTRY_SHA256=' + '0' * 64)
            self.assertTrue(any('THF_REGISTRY_SHA256 mismatch' in x for x in M.validate_bundle(self.reg, self.rsha, d, root)))

    def test_observation_time_substitution_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d = evidence('rush', self.rsha, root); key = 'sensor_motion'
            good = d['manual_observations'][key]['observed_at_utc']
            mutate(d, root, key, 'THF_OBSERVED_AT_UTC=' + good, 'THF_OBSERVED_AT_UTC=2026-09-14T00:00:00Z')
            errors = M.validate_bundle(self.reg, self.rsha, d, root)
            self.assertTrue(any('THF_OBSERVED_AT_UTC mismatch' in x for x in errors))

    def test_failed_dumpsys_capture_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d = evidence('learn_games', self.rsha, root); key = 'learning_progression'
            mutate(d, root, key, 'THF_ACTIVITY_DUMPSYS_EXIT_CODE=0', 'THF_ACTIVITY_DUMPSYS_EXIT_CODE=1')
            self.assertTrue(any('THF_ACTIVITY_DUMPSYS_EXIT_CODE mismatch' in x for x in M.validate_bundle(self.reg, self.rsha, d, root)))

    def test_failed_pidof_capture_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d = evidence('fitness_games', self.rsha, root); key = 'repetition_counting'
            mutate(d, root, key, 'THF_PIDOF_EXIT_CODE=0', 'THF_PIDOF_EXIT_CODE=1')
            self.assertTrue(any('THF_PIDOF_EXIT_CODE mismatch' in x for x in M.validate_bundle(self.reg, self.rsha, d, root)))


if __name__ == '__main__':
    unittest.main()
