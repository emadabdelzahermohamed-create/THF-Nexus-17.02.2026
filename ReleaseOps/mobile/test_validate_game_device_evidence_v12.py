#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, sys, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location('v12',HERE/'validate_game_device_evidence_v12.py'); M=importlib.util.module_from_spec(S); sys.modules[S.name]=M; S.loader.exec_module(M)
T=importlib.util.spec_from_file_location('t11',HERE/'test_validate_game_device_evidence_v11.py'); T11=importlib.util.module_from_spec(T); sys.modules[T.name]=T11; T.loader.exec_module(T11)
V3=M.V3

def evidence(product,rsha,root):
 d=T11.evidence(product,rsha,root); reg=T11.T10.T9.T8.T7.T6.registry_doc(); row=next(x for x in reg['candidates'] if x['app']==product); sid=d['session']['session_id']; fp=d['device']['fingerprint_sha256']
 raw={}; shas={}; stamps={'offline':'2026-09-14T04:13:22Z','local':'2026-09-14T04:13:29Z','online':'2026-09-14T04:13:36Z'}
 for kind in M.RAW_ORDER:
  txt='\n'.join([M.KIND_MARKERS[kind],f'THF_SESSION_ID={sid}',f"THF_PACKAGE={row['package']}",f"THF_CANDIDATE_SHA256={row['apk_sha256']}",f'THF_REGISTRY_SHA256={rsha}',f'THF_DEVICE_FINGERPRINT_SHA256={fp}',f'THF_CAPTURED_AT_UTC={stamps[kind]}',f'THF_ADB_COMMAND={M.COMMANDS[kind]}','THF_ADB_EXIT_CODE=0',f'PAYLOAD={kind}','']).encode(); p=root/f'raw-{kind}.txt'; p.write_bytes(txt); sha=hashlib.sha256(txt).hexdigest(); shas[kind]=sha; raw[kind]={'command':M.COMMANDS[kind],'captured_at_utc':stamps[kind],'evidence_ref':p.name,'evidence_sha256':sha}
 d['offline_network_observation']['raw_captures']=raw
 p=root/'network-adb.txt'; b=p.read_bytes()+''.join(f'{M.SUMMARY_KEYS[k]}={shas[k]}\n' for k in M.RAW_ORDER).encode(); p.write_bytes(b); d['offline_network_observation']['evidence_sha256']=hashlib.sha256(b).hexdigest(); return d

class V12(unittest.TestCase):
 def setUp(self): self.reg=T11.T10.T9.T8.T7.T6.registry_doc(); self.rsha='f'*64
 def test_all_six_pass(self):
  for product in V3.PRODUCT_MANUAL:
   with self.subTest(product=product), tempfile.TemporaryDirectory() as td:
    root=Path(td); self.assertEqual([],M.validate_bundle(self.reg,self.rsha,evidence(product,self.rsha,root),root))
 def test_missing_raw_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('terra',self.rsha,root); d['offline_network_observation'].pop('raw_captures'); self.assertTrue(any('exactly offline/local/online' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_wrong_command_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('rift',self.rsha,root); d['offline_network_observation']['raw_captures']['local']['command']='adb shell echo fake'; self.assertTrue(any('approved ADB command' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_cross_package_capture_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('spark',self.rsha,root); item=d['offline_network_observation']['raw_captures']['offline']; p=root/item['evidence_ref']; b=p.read_bytes().replace(d['package'].encode(),b'com.invalid.fake'); p.write_bytes(b); item['evidence_sha256']=hashlib.sha256(b).hexdigest(); self.assertTrue(any('THF_PACKAGE' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_failed_adb_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('rush',self.rsha,root); item=d['offline_network_observation']['raw_captures']['online']; p=root/item['evidence_ref']; b=p.read_bytes().replace(b'THF_ADB_EXIT_CODE=0',b'THF_ADB_EXIT_CODE=1'); p.write_bytes(b); item['evidence_sha256']=hashlib.sha256(b).hexdigest(); self.assertTrue(any('successful ADB exit code' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_timestamp_reorder_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('learn_games',self.rsha,root); d['offline_network_observation']['raw_captures']['local']['captured_at_utc']='2026-09-14T04:13:38Z'; self.assertTrue(any('strictly offline < local < online' in x or 'timestamp binding mismatch' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_summary_sha_substitution_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('fitness_games',self.rsha,root); p=root/'network-adb.txt'; b=p.read_bytes().replace(next(iter(d['offline_network_observation']['raw_captures'].values()))['evidence_sha256'].encode(),b'0'*64,1); p.write_bytes(b); d['offline_network_observation']['evidence_sha256']=hashlib.sha256(b).hexdigest(); self.assertTrue(any('summary raw SHA binding mismatch' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))

if __name__=='__main__': unittest.main()
