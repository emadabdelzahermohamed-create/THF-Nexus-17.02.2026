#!/usr/bin/env python3
import hashlib, json, tempfile, unittest
import audit_export, evidence_freshness_gate, github_evidence_metadata
import external_ledger_anchor_gate as anchor
import anchored_review_replay_guard as mod

HEAD='b'*40; MINT=evidence_freshness_gate.CANONICAL_MINT; BRANCH=github_evidence_metadata.TOKENOPS_BRANCH

def sha(o): return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def fresh():
 c={'version':1,'network':evidence_freshness_gate.NETWORK,'mint':MINT,'source_head_sha':HEAD,'manifest_sha256':'b'*64,'evidence_binding_sha256':'c'*64,'evidence_bound_simulation_gate_sha256':'d'*64,'review_at_utc':'2026-09-12T15:00:00Z','readonly_audit':{'workflow_run_id':101,'artifact_id':201,'head_sha':HEAD,'completed_at':'2026-09-12T14:30:00Z','age_seconds':1800,'max_age_seconds':7200,'fresh':True},'registry_compiler_gate':{'workflow_run_id':102,'artifact_id':202,'head_sha':HEAD,'completed_at':'2026-09-12T13:00:00Z','age_seconds':7200,'max_age_seconds':86400,'fresh':True},'evidence_fresh':True,'simulation_review_eligible':True,'simulation_execution_permitted':False,'transaction_created':False,'transaction_serialized':False,'transaction_signed':False,'transaction_submitted':False,'broadcast_allowed':False,'financial_effect':False,'external_signer_required_for_execution':True,'user_controlled_approval_required_for_execution':True,'private_key_used':False,'wave_mawja_touched':False}; c['evidence_freshness_gate_sha256']=sha(c); return c

def meta(r,a,n):
 run={'id':r,'name':n,'path':f'.github/workflows/{n}.yml','head_branch':BRANCH,'head_sha':HEAD,'event':'push','status':'completed','conclusion':'success','run_attempt':1,'created_at':'2026-09-12T14:00:00Z','run_started_at':'2026-09-12T14:01:00Z','updated_at':'2026-09-12T14:10:00Z'}
 art={'id':a,'name':n,'size_in_bytes':1234,'digest':'sha256:'+('%064x'%a)[-64:],'expired':False,'created_at':'2026-09-12T14:11:00Z','updated_at':'2026-09-12T14:11:00Z','expires_at':'2026-12-11T14:11:00Z','workflow_run':{'id':r,'head_branch':BRANCH,'head_sha':HEAD}}
 return github_evidence_metadata.build(run,art,n,HEAD,'2026-09-12T14:20:00Z')

class T(unittest.TestCase):
 def fixture(self):
  t=tempfile.NamedTemporaryFile(mode='w+',delete=False); t.close(); audit_export.append_entry({'event_type':'prior-review','network':anchor.NETWORK,'mint':anchor.MINT,'simulation_execution_permitted':False,'transaction_created':False,'transaction_signed':False,'transaction_submitted':False,'broadcast_allowed':False,'financial_effect':False,'private_key_used':False,'wave_mawja_touched':False},t.name,created_at=1)
  req=anchor.prepare_anchor_request(t.name,HEAD); rec={'provider':'gcp-object-lock','object_id':'projects/thf/buckets/tokenops/objects/head#g1','immutable_retention':True,'externally_verified':True,'identity_mode':'workload-identity-federation-or-equivalent-short-lived','persistent_service_account_key_used':False,'anchor_request_sha256':req['anchor_request_sha256'],'ledger_head_sha256':req['ledger_head_sha256'],'ledger_bytes_sha256':req['ledger_bytes_sha256'],'source_head_sha':req['source_head_sha'],'anchored_at_utc':'2026-09-12T18:00:00Z'}; rec['receipt_sha256']=sha(rec); return t.name,req,rec
 def snaps(self): return [meta(101,201,'readonly'),meta(102,202,'control')]
 def test_prepare_consume(self):
  p,r,c=self.fixture(); g=mod.prepare(fresh(),self.snaps(),r,c,p,HEAD); self.assertTrue(g['external_immutable_anchor_verified']); out=mod.consume(g,r,c,p,HEAD,created_at=2); self.assertTrue(out['consumed']); self.assertFalse(out['execution_authorized'])
 def test_replay_fails(self):
  p,r,c=self.fixture(); g=mod.prepare(fresh(),self.snaps(),r,c,p,HEAD); mod.consume(g,r,c,p,HEAD,created_at=2)
  with self.assertRaises(ValueError): mod.consume(g,r,c,p,HEAD,created_at=3)
 def test_anchor_tamper_fails(self):
  p,r,c=self.fixture(); c['object_id']+='x'
  with self.assertRaises(ValueError): mod.prepare(fresh(),self.snaps(),r,c,p,HEAD)
 def test_source_head_mismatch_fails(self):
  p,r,c=self.fixture()
  with self.assertRaises(ValueError): mod.prepare(fresh(),self.snaps(),r,c,p,'c'*40)

if __name__=='__main__': unittest.main()
