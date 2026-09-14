#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, sys, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location('v15',HERE/'validate_game_device_evidence_v15.py'); M=importlib.util.module_from_spec(S); sys.modules[S.name]=M; S.loader.exec_module(M)
T=importlib.util.spec_from_file_location('t14',HERE/'test_validate_game_device_evidence_v14.py'); T14=importlib.util.module_from_spec(T); sys.modules[T.name]=T14; T.loader.exec_module(T)
V3=M.V3

def evidence(product,rsha,root):
 d=T14.evidence(product,rsha,root); d['process_provenance']={}
 req=dict(T14.M.BASE); req.update(T14.M.PRODUCT.get(product,{}))
 for i,key in enumerate(req):
  gameplay_sha=d['manual_observations'][key]['evidence_sha256']; rel=f'process_{key}.txt'; p=root/rel; pid=str(4100+i)
  p.write_text('\n'.join([
   'THF_SESSION_ID='+d['session']['session_id'],'THF_PACKAGE='+d['package'],'THF_CAPABILITY='+key,
   'THF_FOREGROUND_PACKAGE='+d['package'],'THF_FOREGROUND_PID='+pid,'THF_RESUMED_PID='+pid,
   'THF_ACTIVITY_RESUMED=TRUE','THF_PROCESS_ALIVE_AFTER=TRUE','THF_PROCESS_CAPTURE_METHOD='+M.METHOD,
   'THF_GAMEPLAY_EVIDENCE_SHA256='+gameplay_sha,'']),encoding='utf-8')
  d['process_provenance'][key]={'evidence_ref':rel,'evidence_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 return d

def mutate(d,root,key,old,new):
 row=d['process_provenance'][key]; p=root/row['evidence_ref']; p.write_text(p.read_text().replace(old,new)); row['evidence_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()

class V15(unittest.TestCase):
 def setUp(self): self.reg=T14.T13.T12.T11.T10.T9.T8.T7.T6.registry_doc(); self.rsha='f'*64
 def test_all_six_pass(self):
  for product in V3.PRODUCT_MANUAL:
   with self.subTest(product=product), tempfile.TemporaryDirectory() as td:
    root=Path(td); self.assertEqual([],M.validate_bundle(self.reg,self.rsha,evidence(product,self.rsha,root),root))
 def test_wrong_foreground_package_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('terra',self.rsha,root); mutate(d,root,'gameplay_interaction','THF_FOREGROUND_PACKAGE='+d['package'],'THF_FOREGROUND_PACKAGE=com.fake.wrapper'); self.assertTrue(any('THF_FOREGROUND_PACKAGE mismatch' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_pid_must_match_resumed_pid(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('rift',self.rsha,root); mutate(d,root,'combat','THF_RESUMED_PID=4107','THF_RESUMED_PID=9999'); self.assertTrue(any('resumed PID must equal' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_dead_process_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('spark',self.rsha,root); mutate(d,root,'learning_progression','THF_PROCESS_ALIVE_AFTER=TRUE','THF_PROCESS_ALIVE_AFTER=FALSE'); self.assertTrue(any('THF_PROCESS_ALIVE_AFTER mismatch' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_gameplay_sha_substitution_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('rush',self.rsha,root); key='sensor_motion'; good=d['manual_observations'][key]['evidence_sha256']; mutate(d,root,key,'THF_GAMEPLAY_EVIDENCE_SHA256='+good,'THF_GAMEPLAY_EVIDENCE_SHA256='+'0'*64); self.assertTrue(any('THF_GAMEPLAY_EVIDENCE_SHA256 mismatch' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_tampered_provenance_hash_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('fitness_games',self.rsha,root); d['process_provenance']['sensor_motion']['evidence_sha256']='0'*64; self.assertTrue(any('process provenance SHA mismatch' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
if __name__=='__main__': unittest.main()
