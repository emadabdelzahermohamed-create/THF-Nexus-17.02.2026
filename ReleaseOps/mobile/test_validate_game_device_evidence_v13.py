#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, sys, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location('v13',HERE/'validate_game_device_evidence_v13.py'); M=importlib.util.module_from_spec(S); sys.modules[S.name]=M; S.loader.exec_module(M)
T=importlib.util.spec_from_file_location('t12',HERE/'test_validate_game_device_evidence_v12.py'); T12=importlib.util.module_from_spec(T); sys.modules[T.name]=T12; T.loader.exec_module(T12)
V12=M.V12; V3=M.V3


def _payload(kind, package):
 if kind=='offline': return 'ConnectivityService\nNetworkAgentInfo [WIFI () - 100] NetworkCapabilities: INTERNET NOT_RESTRICTED'
 if kind=='local': return f'<?xml version="1.0"?><hierarchy><node package="{package}" text="Local gameplay" /></hierarchy>'
 return 'ConnectivityService\nNetworkAgentInfo [WIFI () - 100] NetworkCapabilities: INTERNET VALIDATED NOT_RESTRICTED'


def evidence(product,rsha,root):
 d=T12.evidence(product,rsha,root); reg=T12.T11.T10.T9.T8.T7.T6.registry_doc(); row=next(x for x in reg['candidates'] if x['app']==product)
 for kind in V12.RAW_ORDER:
  item=d['offline_network_observation']['raw_captures'][kind]; p=root/item['evidence_ref']; text=p.read_text(encoding='utf-8'); text += M.STDOUT_BEGIN+'\n'+_payload(kind,row['package'])+'\n'+M.STDOUT_END+'\n'; p.write_text(text,encoding='utf-8'); sha=hashlib.sha256(p.read_bytes()).hexdigest(); old=item['evidence_sha256']; item['evidence_sha256']=sha
  summary=root/'network-adb.txt'; b=summary.read_bytes().replace(old.encode(),sha.encode()); summary.write_bytes(b); d['offline_network_observation']['evidence_sha256']=hashlib.sha256(b).hexdigest()
 return d


def mutate(d,root,kind,payload):
 item=d['offline_network_observation']['raw_captures'][kind]; p=root/item['evidence_ref']; text=p.read_text(encoding='utf-8'); start=text.index(M.STDOUT_BEGIN)+len(M.STDOUT_BEGIN); end=text.index(M.STDOUT_END); text=text[:start]+'\n'+payload+'\n'+text[end:]; p.write_text(text,encoding='utf-8'); old=item['evidence_sha256']; sha=hashlib.sha256(p.read_bytes()).hexdigest(); item['evidence_sha256']=sha; summary=root/'network-adb.txt'; b=summary.read_bytes().replace(old.encode(),sha.encode()); summary.write_bytes(b); d['offline_network_observation']['evidence_sha256']=hashlib.sha256(b).hexdigest()


class V13(unittest.TestCase):
 def setUp(self): self.reg=T12.T11.T10.T9.T8.T7.T6.registry_doc(); self.rsha='f'*64
 def test_all_six_pass(self):
  for product in V3.PRODUCT_MANUAL:
   with self.subTest(product=product), tempfile.TemporaryDirectory() as td:
    root=Path(td); self.assertEqual([],M.validate_bundle(self.reg,self.rsha,evidence(product,self.rsha,root),root))
 def test_offline_validated_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('terra',self.rsha,root); mutate(d,root,'offline','ConnectivityService NetworkCapabilities: INTERNET VALIDATED'); self.assertTrue(any('unexpectedly contains VALIDATED' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_online_without_validated_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('rift',self.rsha,root); mutate(d,root,'online','ConnectivityService NetworkCapabilities: INTERNET NOT_RESTRICTED'); self.assertTrue(any('must contain VALIDATED' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_local_wrong_package_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('spark',self.rsha,root); mutate(d,root,'local','<hierarchy><node package="com.invalid.fake" /></hierarchy>'); self.assertTrue(any('exact game package' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_local_non_hierarchy_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('rush',self.rsha,root); mutate(d,root,'local',f"package='{d['package']}'"); self.assertTrue(any('uiautomator hierarchy' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_missing_stdout_bounds_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('learn_games',self.rsha,root); item=d['offline_network_observation']['raw_captures']['offline']; p=root/item['evidence_ref']; text=p.read_text().replace(M.STDOUT_BEGIN+'\n','').replace('\n'+M.STDOUT_END,''); p.write_text(text); old=item['evidence_sha256']; sha=hashlib.sha256(p.read_bytes()).hexdigest(); item['evidence_sha256']=sha; summary=root/'network-adb.txt'; b=summary.read_bytes().replace(old.encode(),sha.encode()); summary.write_bytes(b); d['offline_network_observation']['evidence_sha256']=hashlib.sha256(b).hexdigest(); self.assertTrue(any('bounded ADB stdout' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))

if __name__=='__main__': unittest.main()
