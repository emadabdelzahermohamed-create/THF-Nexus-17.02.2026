#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, sys, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location('v11',HERE/'validate_game_device_evidence_v11.py'); M=importlib.util.module_from_spec(S); sys.modules[S.name]=M; S.loader.exec_module(M)
T=importlib.util.spec_from_file_location('t10',HERE/'test_validate_game_device_evidence_v10.py'); T10=importlib.util.module_from_spec(T); sys.modules[T.name]=T10; T.loader.exec_module(T10)
V3=M.V3

def evidence(product, rsha, root):
    d=T10.evidence(product,rsha,root); pkg=d['package']; sid=d['session']['session_id']
    text='\n'.join([
        f'THF_PACKAGE={pkg}',f'THF_SESSION_ID={sid}',
        'THF_NETWORK_PID_BEFORE=2222',
        'THF_STAGE=OFFLINE_CONFIRMED','THF_OFFLINE_REACHED=TRUE',
        'THF_STAGE=LOCAL_GAMEPLAY_OBSERVED','THF_LOCAL_MODE_STAYED_LOCAL=TRUE','THF_ONLINE_STATE_FAKED=FALSE',
        'THF_STAGE=ONLINE_RESTORED','THF_ONLINE_RESTORED=TRUE',
        'THF_NETWORK_PID_AFTER=2222','THF_NETWORK_PID_SAME=TRUE','']).encode()
    p=root/'network-adb.txt'; p.write_bytes(text)
    d['offline_network_observation']={
        'session_id':sid,'package':pkg,'method':'adb-shell-connectivity-transition-v1',
        'started_at_utc':'2026-09-14T04:13:20Z','ended_at_utc':'2026-09-14T04:13:39Z',
        'offline_reached':True,'online_restored':True,'process_same_pid':True,
        'local_mode_stayed_local':True,'no_online_state_faked':True,
        'evidence_ref':'network-adb.txt','evidence_sha256':hashlib.sha256(text).hexdigest()}
    return d

def mutate_file(root,d,old,new):
    p=root/'network-adb.txt'; b=p.read_bytes().replace(old,new); p.write_bytes(b)
    d['offline_network_observation']['evidence_sha256']=hashlib.sha256(b).hexdigest()

class V11(unittest.TestCase):
    def setUp(self):
        self.reg=T10.T9.T8.T7.T6.registry_doc(); self.rsha='f'*64
    def test_all_six_pass_ordered_hash_bound_transition(self):
        for product in V3.PRODUCT_MANUAL:
            with self.subTest(product=product), tempfile.TemporaryDirectory() as td:
                root=Path(td); self.assertEqual([],M.validate_bundle(self.reg,self.rsha,evidence(product,self.rsha,root),root))
    def test_missing_record_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('terra',self.rsha,root); d.pop('offline_network_observation')
            self.assertTrue(any('missing record' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
    def test_wrong_package_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('rift',self.rsha,root); d['offline_network_observation']['package']='com.invalid'
            self.assertTrue(any('exact candidate package' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
    def test_cross_session_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('spark',self.rsha,root); d['offline_network_observation']['session_id']='other-session-0001'
            self.assertTrue(any('session_id mismatch' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
    def test_false_local_truth_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('rush',self.rsha,root); d['offline_network_observation']['local_mode_stayed_local']=False
            self.assertTrue(any('local_mode_stayed_local' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
    def test_tamper_fails_sha(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('learn_games',self.rsha,root); (root/'network-adb.txt').write_text('tampered')
            self.assertTrue(any('evidence bytes mismatch' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
    def test_pid_change_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('fitness_games',self.rsha,root); mutate_file(root,d,b'THF_NETWORK_PID_AFTER=2222',b'THF_NETWORK_PID_AFTER=3333')
            self.assertTrue(any('same numeric PID' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
    def test_stage_reorder_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('terra',self.rsha,root)
            p=root/'network-adb.txt'; s=p.read_text(); s=s.replace('THF_STAGE=OFFLINE_CONFIRMED','THF_STAGE=TMP',1).replace('THF_STAGE=ONLINE_RESTORED','THF_STAGE=OFFLINE_CONFIRMED',1).replace('THF_STAGE=TMP','THF_STAGE=ONLINE_RESTORED',1); b=s.encode(); p.write_bytes(b); d['offline_network_observation']['evidence_sha256']=hashlib.sha256(b).hexdigest()
            self.assertTrue(any('strict order' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
    def test_duplicate_truth_marker_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('rift',self.rsha,root); p=root/'network-adb.txt'; b=p.read_bytes()+b'THF_ONLINE_STATE_FAKED=FALSE\n'; p.write_bytes(b); d['offline_network_observation']['evidence_sha256']=hashlib.sha256(b).hexdigest()
            self.assertTrue(any('THF_ONLINE_STATE_FAKED' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
    def test_unapproved_method_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=evidence('spark',self.rsha,root); d['offline_network_observation']['method']='manual-note'
            self.assertTrue(any('approved ADB connectivity method' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))

if __name__=='__main__': unittest.main()
