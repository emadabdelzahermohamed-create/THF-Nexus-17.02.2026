import copy, unittest
from evidence_dag_financial_control import *

POLICY={"version":1,"network":NETWORK,"mint":MINT,
 "verified":{"token_program":PROGRAM,"decimals":8,"current_supply_ui":"10000000000","mint_authority":None,"freeze_authority":None},
 "economics":{"active_user_revenue_share":0.35,"approved_supply_floor_target_ui":"8000000000","burn_source_policy":"treasury_controlled_balances_only","minting_assumption":"disabled_immutable"},
 "signer_policy":{"production_policy_status":"not_yet_approved"},
 "distribution_controls":{"per_user_cap":None,"epoch_budget_cap":None,"claim_or_push_model":"to_be_selected_after_treasury_design"}}
TREASURY={"version":1,"network":NETWORK,"mint":MINT,"control_model":"external_multisig_required",
 "approval_classes":{"reward_epoch":{"minimum_approvals":2,"execution":"external_multisig"},"vesting_settlement":{"minimum_approvals":2,"execution":"external_multisig"},"burn":{"minimum_approvals":3,"execution":"external_multisig","supply_floor_ui":"8000000000"},"treasury_transfer":{"minimum_approvals":3,"execution":"external_multisig"}}}
AUDIT={"network":NETWORK,"mint":MINT,"rpc_slot":446809227,"program_id":PROGRAM,"decimals":8,
 "supply_raw":"1000000000000000000","supply_ui":"10000000000","mint_authority":None,"freeze_authority":None,
 "largest_accounts_status":"unavailable","recent_signatures_status":"ok","recent_signature_count":5}
CONTRACTS={
 "Vault":{"binding_financial_action":False,"forbidden":["private_keys","signatures","broadcast"]},
 "Forge":{"binding_financial_action":False,"forbidden":["private_keys","signatures","broadcast"]},
 "Core":{"binding_financial_action":False,"forbidden":["private_keys","signatures","broadcast"]}}
FULL_EVIDENCE={k:{"status":"verified_public_hash_only"} for k in ["treasury_registry","treasury_balance_attestation","distribution_reserve","allocation_accounting","vesting_liability","burn_reserve","simulation_receipt","governance_charter","vault_contract","forge_contract","core_contract"]}

class T(unittest.TestCase):
 def test_empty_evidence_fail_closed(self):
  d=build_evidence_dag(POLICY,TREASURY,AUDIT,{})
  self.assertFalse(d["review_ready"]);self.assertGreaterEqual(len(d["blockers"]),11)
 def test_full_evidence_no_dag_blocker(self):
  d=build_evidence_dag(POLICY,TREASURY,AUDIT,FULL_EVIDENCE)
  self.assertEqual(d["blockers"],[]);self.assertFalse(d["execution_authorized"])
 def test_drift_quarantines(self):
  a=copy.deepcopy(AUDIT);a["mint_authority"]="unexpected"
  d=build_evidence_dag(POLICY,TREASURY,a,FULL_EVIDENCE)
  self.assertTrue(d["quarantined"]);self.assertIn("quarantine:mint_authority_reappeared",d["blockers"])
 def test_8b_floor(self):
  a=copy.deepcopy(AUDIT);a["supply_raw"]=str(SUPPLY_FLOOR_RAW-1)
  self.assertIn("supply_below_8b_floor",audit_quarantine_reasons(a))
 def test_double_entry_balanced(self):
  j=build_double_entry_preview("reward_epoch",35000,"0"*64,"1"*64)
  self.assertEqual(j["debits_raw"],j["credits_raw"]);self.assertFalse(j["posting_authorized"])
 def test_negative_journal_rejected(self):
  with self.assertRaises(ValueError): build_double_entry_preview("burn",-1,"0"*64,"1"*64)
 def test_threshold_reward_two(self):
  d=build_evidence_dag(POLICY,TREASURY,AUDIT,FULL_EVIDENCE);j=build_double_entry_preview("reward_epoch",0,"0"*64,"1"*64)
  l=build_intent_lifecycle("reward_epoch",d,j,TREASURY)
  self.assertEqual(l["minimum_external_multisig_approvals"],2);self.assertFalse(l["signing_allowed"])
 def test_threshold_burn_three(self):
  d=build_evidence_dag(POLICY,TREASURY,AUDIT,FULL_EVIDENCE);j=build_double_entry_preview("burn",0,"0"*64,"1"*64)
  l=build_intent_lifecycle("burn",d,j,TREASURY)
  self.assertEqual(l["minimum_external_multisig_approvals"],3);self.assertFalse(l["broadcast_allowed"])
 def test_incident_quarantines_intents(self):
  a=copy.deepcopy(AUDIT);a["program_id"]="bad";q=build_incident_quarantine(a,["a"*64])
  self.assertTrue(q["triggered"]);self.assertEqual(q["intent_hashes"],["a"*64])
 def test_healthy_incident_receipt_no_onchain_action(self):
  q=build_incident_quarantine(AUDIT,["a"*64]);self.assertFalse(q["triggered"]);self.assertFalse(q["automatic_on_chain_action"])
 def test_contract_conformance(self):
  c=build_integration_conformance(CONTRACTS);self.assertTrue(c["conformant"]);self.assertFalse(c["key_material_allowed"])
 def test_contract_nonconformance(self):
  c=copy.deepcopy(CONTRACTS);c["Forge"]["binding_financial_action"]=True
  self.assertFalse(build_integration_conformance(c)["conformant"])
 def test_secret_rejected(self):
  e=copy.deepcopy(FULL_EVIDENCE);e["treasury_registry"]["private_key"]="x"
  with self.assertRaises(ValueError): build_evidence_dag(POLICY,TREASURY,AUDIT,e)
 def test_policy_35pct_drift_rejected(self):
  p=copy.deepcopy(POLICY);p["economics"]["active_user_revenue_share"]=0.34
  with self.assertRaises(ValueError): validate_authority(p,TREASURY)
 def test_compile_current_missing_evidence_failclosed(self):
  r=compile_batch(POLICY,TREASURY,AUDIT,{},CONTRACTS,"reward_epoch",35000)
  self.assertEqual(r["readiness"],"FAIL_CLOSED");self.assertFalse(r["financial_effect"])
  self.assertFalse(r["transaction_created"]);self.assertTrue(r["wave_mawja_untouched"])
 def test_hash_determinism(self):
  self.assertEqual(sha256({"b":1,"a":2}),sha256({"a":2,"b":1}))

if __name__=="__main__": unittest.main()
