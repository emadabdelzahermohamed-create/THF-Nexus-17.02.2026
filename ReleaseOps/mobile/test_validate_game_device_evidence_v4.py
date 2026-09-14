#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("device_evidence_v4", HERE / "validate_game_device_evidence_v4.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)
V3 = MOD.V3


def registry_doc():
    rows=[]
    for i,(app,pkg) in enumerate((
        ('terra','com.topherofit.thf.terra'),('rift','com.topherofit.thf.rift'),
        ('spark','com.topherofit.thf.spark'),('rush','com.topherofit.thf.rush'),
        ('learn_games','com.thf.topherofit.learngames'),('fitness_games','com.thf.topherofit.fitnessgames')),
        start=1):
        rows.append({'app':app,'package':pkg,'apk_sha256':str(i)*64})
    return {'schema':'thf-game-device-candidates-v1','candidates':rows}


def evidence(product, registry_sha, root: Path):
    reg=registry_doc(); row=next(x for x in reg['candidates'] if x['app']==product)
    manual={}
    for key in V3.COMMON_MANUAL + V3.PRODUCT_MANUAL[product]:
        rel=f'evidence/{product}/{key}.bin'; p=root/rel; p.parent.mkdir(parents=True,exist_ok=True)
        data=(product+':'+key).encode(); p.write_bytes(data)
        manual[key]={'pass':True,'observed_at_utc':'2026-09-14T03:00:00Z','evidence_ref':rel,'evidence_sha256':hashlib.sha256(data).hexdigest()}
    return {
        'schema':V3.SCHEMA,'product':product,'registry_sha256':registry_sha,'package':row['package'],
        'exact_candidate_sha256':row['apk_sha256'],
        'device':{'physical_device':True,'emulator_detected':False,'fingerprint_sha256':'a'*64,'model':'Physical Phone','sdk':'36'},
        'objective':{'install_pass':True,'cold_launch_pass':True,'background_resume_pass':True,'crash_free_smoke_pass':True,'total_pss_kb':100000,'framestats_rows':60,'thermal_snapshot_present':True,'fatal_runtime_markers':[]},
        'performance_observation':{'fps_observed':55.0,'ram_mb_observed':300.0,'thermal_status_observed':'nominal','observation_seconds':60},
        'manual_observations':manual,'online_state_not_faked':True,'local_mode_genuinely_local':True,'final_or_play_ready':False,
    }


class DeviceEvidenceV4Tests(unittest.TestCase):
    def test_all_six_require_and_accept_real_hash_bound_files(self):
        reg=registry_doc(); rsha='f'*64
        for product in V3.PRODUCT_MANUAL:
            with self.subTest(product=product), tempfile.TemporaryDirectory() as td:
                root=Path(td); doc=evidence(product,rsha,root)
                self.assertEqual([],MOD.validate_bundle(reg,rsha,doc,root))

    def test_missing_file_fails(self):
        reg=registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rift',rsha,root)
            (root/doc['manual_observations']['combat']['evidence_ref']).unlink()
            self.assertTrue(any('combat: evidence file missing' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_hash_mismatch_fails(self):
        reg=registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rush',rsha,root)
            p=root/doc['manual_observations']['sensor_motion']['evidence_ref']; p.write_bytes(b'tampered')
            self.assertTrue(any('sensor_motion: evidence SHA mismatch' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_path_escape_fails(self):
        reg=registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('terra',rsha,root)
            doc['manual_observations']['touch']['evidence_ref']='../../fake.mp4'
            self.assertTrue(any('touch: unsafe evidence_ref' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_empty_file_fails(self):
        reg=registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('spark',rsha,root)
            p=root/doc['manual_observations']['learning_progression']['evidence_ref']; p.write_bytes(b'')
            self.assertTrue(any('learning_progression: evidence file empty' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))


if __name__=='__main__': unittest.main()
