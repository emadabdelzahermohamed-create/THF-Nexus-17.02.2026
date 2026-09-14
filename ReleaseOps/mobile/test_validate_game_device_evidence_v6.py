#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("device_evidence_v6", HERE / "validate_game_device_evidence_v6.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)
V5 = MOD.V5
V4 = MOD.V4
V3 = MOD.V3
SID = "phone-session-20260914-0727-v6a1b2"


def registry_doc():
    rows=[]
    for i,(app,pkg) in enumerate((
        ('terra','com.topherofit.thf.terra'),('rift','com.topherofit.thf.rift'),
        ('spark','com.topherofit.thf.spark'),('rush','com.topherofit.thf.rush'),
        ('learn_games','com.thf.topherofit.learngames'),('fitness_games','com.thf.topherofit.fitnessgames')),
        start=1):
        rows.append({'app':app,'package':pkg,'apk_sha256':str(i)*64})
    return {'schema':'thf-game-device-candidates-v1','candidates':rows}


def _file(root: Path, rel: str, data: bytes):
    p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
    return rel, hashlib.sha256(data).hexdigest()


def _record(product: str, key: str, root: Path, namespace: str):
    rel,sha=_file(root,f'evidence/{product}/{namespace}-{key}.bin',(product+':'+namespace+':'+key).encode())
    return {'pass':True,'session_id':SID,'observed_at_utc':'2026-09-14T04:12:30Z','evidence_ref':rel,'evidence_sha256':sha}


def evidence(product, registry_sha, root: Path):
    reg=registry_doc(); row=next(x for x in reg['candidates'] if x['app']==product)
    manual={key:_record(product,key,root,'manual') for key in V3.COMMON_MANUAL + V3.PRODUCT_MANUAL[product]}
    authority={key:_record(product,key,root,'authority') for key in V4.AUTHORITY_OBSERVATIONS}
    oref,osha=_file(root,f'evidence/{product}/objective-adb.txt',b'adb install launch pss framestats thermal')
    pref,psha=_file(root,f'evidence/{product}/performance.txt',b'fps ram thermal 60 seconds')
    return {
        'schema':V3.SCHEMA,'product':product,'registry_sha256':registry_sha,'package':row['package'],
        'exact_candidate_sha256':row['apk_sha256'],
        'session':{'session_id':SID,'started_at_utc':'2026-09-14T04:12:00Z','ended_at_utc':'2026-09-14T04:14:00Z'},
        'device':{'physical_device':True,'emulator_detected':False,'fingerprint_sha256':'a'*64,'model':'Physical Phone','sdk':'36'},
        'objective':{'session_id':SID,'captured_at_utc':'2026-09-14T04:12:45Z','install_pass':True,'cold_launch_pass':True,'background_resume_pass':True,'crash_free_smoke_pass':True,'total_pss_kb':100000,'framestats_rows':60,'thermal_snapshot_present':True,'fatal_runtime_markers':[],'evidence_ref':oref,'evidence_sha256':osha},
        'performance_observation':{'session_id':SID,'captured_at_utc':'2026-09-14T04:13:00Z','fps_observed':55.0,'ram_mb_observed':300.0,'thermal_status_observed':'nominal','observation_seconds':60,'evidence_ref':pref,'evidence_sha256':psha},
        'manual_observations':manual,'authority_observations':authority,
        'online_state_not_faked':True,'local_mode_genuinely_local':True,'final_or_play_ready':False,
    }


class DeviceEvidenceV6Tests(unittest.TestCase):
    def test_all_six_accept_file_bound_objective_and_performance(self):
        reg=registry_doc(); rsha='f'*64
        for product in V3.PRODUCT_MANUAL:
            with self.subTest(product=product), tempfile.TemporaryDirectory() as td:
                root=Path(td); doc=evidence(product,rsha,root)
                self.assertEqual([], MOD.validate_bundle(reg,rsha,doc,root))

    def test_objective_missing_file_fails(self):
        reg=registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('terra',rsha,root)
            (root/doc['objective']['evidence_ref']).unlink()
            self.assertTrue(any('objective: evidence file missing' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_performance_sha_mismatch_fails(self):
        reg=registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rift',rsha,root)
            doc['performance_observation']['evidence_sha256']='0'*64
            self.assertTrue(any('performance_observation: evidence SHA mismatch' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_missing_objective_hash_fails(self):
        reg=registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('rush',rsha,root)
            doc['objective'].pop('evidence_sha256')
            self.assertTrue(any('objective: evidence_sha256 required' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))

    def test_unsafe_performance_ref_fails(self):
        reg=registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); doc=evidence('fitness_games',rsha,root)
            doc['performance_observation']['evidence_ref']='../../outside.txt'
            self.assertTrue(any('performance_observation: unsafe evidence_ref' in x for x in MOD.validate_bundle(reg,rsha,doc,root)))


if __name__=='__main__': unittest.main()
