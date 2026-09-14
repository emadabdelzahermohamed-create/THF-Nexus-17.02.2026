#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, sys, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location('v10',HERE/'validate_game_device_evidence_v10.py'); M=importlib.util.module_from_spec(S); sys.modules[S.name]=M; S.loader.exec_module(M)
T=importlib.util.spec_from_file_location('t9',HERE/'test_validate_game_device_evidence_v9.py'); T9=importlib.util.module_from_spec(T); sys.modules[T.name]=T9; T.loader.exec_module(T9)
V3=M.V3

def evidence(product, rsha, root):
    d=T9.evidence(product,rsha,root); pkg=d['package']; sid=d['session']['session_id']
    text='\n'.join([f'THF_PACKAGE={pkg}',f'THF_SESSION_ID={sid}','THF_TOUCH_OBSERVED=TRUE','THF_SENSOR_LANDSCAPE_OBSERVED=TRUE','THF_EXPANDABLE_ASPECT_OBSERVED=TRUE','THF_SAFE_AREA_OBSERVED=TRUE','THF_BACKGROUND_PID_BEFORE=2222','THF_BACKGROUND_PID_AFTER=2222','THF_BACKGROUND_RESUME_SAME_PID=TRUE','']).encode()
    p=root/'lifecycle-adb.txt'; p.write_bytes(text)
    d['lifecycle_touch_orientation_observation']={'session_id':sid,'package':pkg,'method':'adb-shell-lifecycle-transcript-v1','started_at_utc':'2026-09-14T04:13:40Z','ended_at_utc':'2026-09-14T04:14:10Z','touch_observed':True,'sensor_landscape_observed':True,'expandable_aspect_observed':True,'safe_area_observed':True,'background_resume_same_pid':True,'evidence_ref':'lifecycle-adb.txt','evidence_sha256':hashlib.sha256(text).hexdigest()}
    return d

class V10(unittest.TestCase):
    def test_all_six_pass_bound_transcript(self):
        reg=T9.T8.T7.T6.registry_doc(); rsha='f'*64
        for product in V3.PRODUCT_MANUAL:
            with self.subTest(product=product), tempfile.TemporaryDirectory() as td:
                root=Path(td); self.assertEqual([],M.validate_bundle(reg,rsha,evidence(product,rsha,root),root))
    def test_missing_record_fails(self):
        reg=T9.T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('terra',rsha,root); d.pop('lifecycle_touch_orientation_observation'); self.assertTrue(any('missing record' in x for x in M.validate_bundle(reg,rsha,d,root)))
    def test_changed_pid_fails(self):
        reg=T9.T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('rift',rsha,root); p=root/'lifecycle-adb.txt'; b=p.read_bytes().replace(b'THF_BACKGROUND_PID_AFTER=2222',b'THF_BACKGROUND_PID_AFTER=3333'); p.write_bytes(b); d['lifecycle_touch_orientation_observation']['evidence_sha256']=hashlib.sha256(b).hexdigest(); self.assertTrue(any('same numeric PID' in x for x in M.validate_bundle(reg,rsha,d,root)))
    def test_tamper_fails_sha(self):
        reg=T9.T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('spark',rsha,root); (root/'lifecycle-adb.txt').write_text('tampered'); self.assertTrue(any('evidence bytes mismatch' in x for x in M.validate_bundle(reg,rsha,d,root)))
    def test_false_touch_fails(self):
        reg=T9.T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('rush',rsha,root); d['lifecycle_touch_orientation_observation']['touch_observed']=False; self.assertTrue(any('touch_observed' in x for x in M.validate_bundle(reg,rsha,d,root)))
    def test_missing_safe_area_marker_fails(self):
        reg=T9.T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('learn_games',rsha,root); p=root/'lifecycle-adb.txt'; b=p.read_bytes().replace(b'THF_SAFE_AREA_OBSERVED=TRUE\n',b''); p.write_bytes(b); d['lifecycle_touch_orientation_observation']['evidence_sha256']=hashlib.sha256(b).hexdigest(); self.assertTrue(any('THF_SAFE_AREA_OBSERVED=TRUE' in x for x in M.validate_bundle(reg,rsha,d,root)))
    def test_cross_session_fails(self):
        reg=T9.T8.T7.T6.registry_doc(); rsha='f'*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('fitness_games',rsha,root); d['lifecycle_touch_orientation_observation']['session_id']='other'; self.assertTrue(any('session_id mismatch' in x for x in M.validate_bundle(reg,rsha,d,root)))

if __name__=='__main__': unittest.main()
