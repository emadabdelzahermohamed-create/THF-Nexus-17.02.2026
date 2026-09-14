#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("device_evidence_v5", HERE / "validate_game_device_evidence_v5.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)
V4 = MOD.V4
V3 = MOD.V3
SID = "phone-session-20260914-0712-a1b2c3"


def registry_doc():
    rows=[]
    for i,(app,pkg) in enumerate((
        ('terra','com.topherofit.thf.terra'),('rift','com.topherofit.thf.rift'),
        ('spark','com.topherofit.thf.spark'),('rush','com.topherofit.thf.rush'),
        ('learn_games','com.thf.topherofit.learngames'),('fitness_games','com.thf.topherofit.fitnessgames')),
        start=1):
        rows.append({'app':app,'package':pkg,'apk_sha256':str(i)*64})
    return {'schema':'thf-game-device-candidates-v1','candidates':rows}


def _record(product: str, key: str, root: Path, namespace: str):
    rel=f'evidence/{product}/{namespace}-{key}.bin'; p=root/rel; p.parent.mkdir(parents=True,exist_ok=True)
    data=(product+':'+namespace+':'+key).encode(); p.write_bytes(data)
    return {'pass':True,'session_id':SID,'observed_at_utc':'2026-09-14T04:12:30Z','evidence_ref':rel,'evidence_sha256':hashlib.sha256(data).hexdigest()}


def evidence(product, registry_sha, root: Path):
    reg=registry_doc(); row=next(x for x in reg['candidates'] if x['app']==product)
    manual={key:_record(product,key,root,'manual') for key in V3.COMMON_MANUAL + V3.PRODUCT_MANUAL[product]}
    authority={key:_record(product,key,root,'authority') for key in V4.AUTHORITY_OBSERVATIONS}
    return {
        'schema':V3.SCHEMA,'product':product,'registry_sha256':registry_sha,'package':row['package'],
        'exact_candidate_sha256':row['apk_sha256'],
        'session':{'session_id':SID,'started_at_utc':'2026-09-14T04:12:00Z','ended_at_utc':'2026-09-14T04:14:00Z'},
        'device':{'physical_device':True,'emulator_detected':False,'fingerprint_sha256':'a'*64,'model':'Physical Phone','sdk':'36'},
        'objective':{'session_id':SID,'captured_at_utc':'2026-09-14T04:12:45Z','install_pass':True,'cold_launch_pass':True,'background_resume_pass':True,'crash_free_smoke_pass':True,'total_pss_kb':100000,'framestats_rows':60,'thermal_snapshot_present':True,'fatal_runtime_markers':[]},
        'performance_observation':{'session_id':SID,'captured_at_utc':'2026-09-14T04:13:00Z','fps_observed':55.0,'ram_mb_observed':300.0,'thermal_status_observed':'nominal','observation_seconds':60},
        'manual_observations':manual,'authority_observations':authority,
        'online_state_not_faked':True,'local_mode_genuinely_local':True,'final_or_play_ready':False,
    }


class DeviceEvidenceV5Tests(unittest.TestCase):
    def test_all_six_accept_one_session_hash_bound_evidence(self):
        reg=registry_doc(); rsha='f'*64
        for product in V3.PRODUCT_MANUAL:
            with self.subTest(product=product), tempfile.TemporaryDirectory() as td:
                root=Path(td); doc=evidence(product,rsha,root)
                self.assertEqual([], MOD.validate_bundle(reg,rsha,doc,root))

    def test_manual_cross_session_mix_fails(self):
        reg=registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rift',rsha,root)
            doc['manual_observations']['combat']['session_id']='other-session-20260914-deadbeef'
            self.assertTrue(any('combat: session_id mismatch' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_authority_cross_session_mix_fails(self):
        reg=registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('terra',rsha,root)
            doc['authority_observations']['online_authority_behavior']['session_id']='other-session-20260914-deadbeef'
            self.assertTrue(any('online_authority_behavior: session_id mismatch' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_observation_outside_session_fails(self):
        reg=registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rush',rsha,root)
            doc['manual_observations']['sensor_motion']['observed_at_utc']='2026-09-14T05:00:00Z'
            self.assertTrue(any('sensor_motion: observation outside' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_objective_and_performance_must_share_session(self):
        reg=registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('fitness_games',rsha,root)
            doc['objective']['session_id']='other-session-20260914-deadbeef'
            doc['performance_observation']['captured_at_utc']='2026-09-14T06:00:00Z'
            errs=MOD.validate_bundle(reg,rsha,doc,root)
            self.assertTrue(any('objective.session_id mismatch' in x for x in errs))
            self.assertTrue(any('performance observation outside' in x for x in errs))


if __name__=='__main__': unittest.main()
