#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("device_evidence_v8", HERE / "validate_game_device_evidence_v8.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

T7SPEC = importlib.util.spec_from_file_location("device_evidence_v7_tests", HERE / "test_validate_game_device_evidence_v7.py")
T7 = importlib.util.module_from_spec(T7SPEC)
assert T7SPEC and T7SPEC.loader
sys.modules[T7SPEC.name] = T7
T7SPEC.loader.exec_module(T7)
V3 = MOD.V3


def _rewrite_performance_capture(doc: dict, root: Path) -> None:
    perf = doc['performance_observation']
    objective = doc['objective']
    text = "\n".join((
        f"THF_FPS_OBSERVED={perf['fps_observed']}",
        f"THF_RAM_MB_OBSERVED={perf['ram_mb_observed']}",
        f"THF_THERMAL_STATUS_OBSERVED={perf['thermal_status_observed']}",
        f"THF_OBSERVATION_SECONDS={perf['observation_seconds']}",
        f"THF_OBJECTIVE_EVIDENCE_SHA256={objective['evidence_sha256']}",
        f"THF_SESSION_ID={doc['session']['session_id']}",
        "",
    )).encode()
    path = root / perf['evidence_ref']
    path.write_bytes(text)
    perf['evidence_sha256'] = hashlib.sha256(text).hexdigest()


def evidence(product: str, registry_sha: str, root: Path):
    doc = T7.evidence(product, registry_sha, root)
    pss = doc['objective']['total_pss_kb']
    frames = doc['objective']['framestats_rows']
    doc['performance_observation']['ram_mb_observed'] = round(pss / 1024.0, 2)
    doc['performance_observation']['provenance'] = {
        'objective_evidence_sha256': doc['objective']['evidence_sha256'],
        'fps_method': 'dumpsys-gfxinfo-framestats',
        'fps_source_framestats_rows': frames,
        'ram_method': 'dumpsys-meminfo-total-pss',
        'ram_source_total_pss_kb': pss,
        'thermal_method': 'dumpsys-thermalservice',
        'thermal_source_snapshot_present': True,
        'session_id': doc['session']['session_id'],
    }
    _rewrite_performance_capture(doc, root)
    return doc


class DeviceEvidenceV8Tests(unittest.TestCase):
    def test_all_six_accept_performance_provenance(self):
        reg=T7.T6.registry_doc(); rsha='f'*64
        for product in V3.PRODUCT_MANUAL:
            with self.subTest(product=product), tempfile.TemporaryDirectory() as td:
                root=Path(td); doc=evidence(product,rsha,root)
                self.assertEqual([], MOD.validate_bundle(reg,rsha,doc,root))

    def test_missing_provenance_fails(self):
        reg=T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('terra',rsha,root)
            doc['performance_observation'].pop('provenance')
            self.assertTrue(any('provenance: missing record' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_wrong_objective_capture_sha_fails(self):
        reg=T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rift',rsha,root)
            doc['performance_observation']['provenance']['objective_evidence_sha256']='0'*64
            self.assertTrue(any('must match objective capture SHA' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_typed_ram_not_derived_from_pss_fails(self):
        reg=T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('spark',rsha,root)
            doc['performance_observation']['ram_mb_observed']=9999.0
            self.assertTrue(any('must be derived from objective TOTAL PSS' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_ram_source_mismatch_fails(self):
        reg=T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rush',rsha,root)
            doc['performance_observation']['provenance']['ram_source_total_pss_kb'] += 1
            self.assertTrue(any('must equal objective total_pss_kb' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_framestats_source_mismatch_fails(self):
        reg=T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('learn_games',rsha,root)
            doc['performance_observation']['provenance']['fps_source_framestats_rows'] += 1
            self.assertTrue(any('must equal objective framestats_rows' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_unapproved_fps_method_fails(self):
        reg=T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('fitness_games',rsha,root)
            doc['performance_observation']['provenance']['fps_method']='typed-json'
            self.assertTrue(any('approved runtime method required' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_thermal_source_required(self):
        reg=T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('terra',rsha,root)
            doc['performance_observation']['provenance']['thermal_source_snapshot_present']=False
            self.assertTrue(any('objective thermal snapshot required' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_performance_provenance_cross_session_fails(self):
        reg=T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rift',rsha,root)
            doc['performance_observation']['provenance']['session_id']='other-phone-session-20260914'
            self.assertTrue(any('provenance.session_id: session_id mismatch' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_hash_bound_capture_fps_mismatch_fails(self):
        reg=T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('spark',rsha,root)
            doc['performance_observation']['fps_observed']=123.0
            self.assertTrue(any('fps_observed: JSON does not match hash-bound performance capture' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_hash_bound_capture_thermal_mismatch_fails(self):
        reg=T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rush',rsha,root)
            doc['performance_observation']['thermal_status_observed']='critical'
            self.assertTrue(any('thermal_status_observed: JSON does not match hash-bound performance capture' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_capture_objective_sha_mismatch_fails(self):
        reg=T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('learn_games',rsha,root)
            path=root/doc['performance_observation']['evidence_ref']
            data=path.read_text().replace(doc['objective']['evidence_sha256'], '0'*64).encode()
            path.write_bytes(data)
            doc['performance_observation']['evidence_sha256']=hashlib.sha256(data).hexdigest()
            self.assertTrue(any('performance capture is not bound to objective evidence SHA' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_duplicate_metric_fails(self):
        reg=T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('fitness_games',rsha,root)
            path=root/doc['performance_observation']['evidence_ref']
            data=path.read_bytes()+b'THF_FPS_OBSERVED=55.0\n'
            path.write_bytes(data)
            doc['performance_observation']['evidence_sha256']=hashlib.sha256(data).hexdigest()
            self.assertTrue(any('duplicate canonical metric THF_FPS_OBSERVED' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))


if __name__=='__main__': unittest.main()
