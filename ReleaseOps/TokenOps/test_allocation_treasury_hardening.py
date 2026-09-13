import copy,unittest
from allocation_epoch_simulator import simulate_epoch
from treasury_inventory_gate import build_inventory
from intent_manifest_gate import build_manifest
from readiness_matrix import build_matrix

MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
POLICY={"version":1,"network":"solana-mainnet-beta","mint":MINT,
"economics":{"active_user_revenue_share":0.35,"approved_supply_floor_target_ui":"8000000000",
"approved_supply_floor_target_raw":"800000000000000000"},
"holder_concentration":{"enforcement_mode":"rpc_if_available","advisory_only_when_rate_limited":True},
"distribution_controls":{"anti_whale_cap_required":True,"anti_sybil_required":True,"activity_evidence_required":True,
"treasury_balance_required":True,"distribution_reserve_account":None,"per_user_cap":None,"epoch_budget_cap":None},
"signer_policy":{"provider_preference":["wif","gcp_short_lived"],"persistent_service_account_keys_allowed":False,
"production_policy_status":"not_yet_approved"},"execution":{"auto_sign":False,"auto_broadcast":False,"user_approval_required":True}}
TREASURY={"version":1,"network":"solana-mainnet-beta","mint":MINT,"control_model":"external_multisig_required",
"approval_classes":{"reward_epoch":{"minimum_approvals":2,"execution":"external_multisig"},
"vesting_settlement":{"minimum_approvals":2,"execution":"external_multisig"},
"burn":{"minimum_approvals":3,"execution":"external_multisig","supply_floor_ui":"8000000000"},
"treasury_transfer":{"minimum_approvals":3,"execution":"external_multisig"}}}
USERS=[{"subject_hash":"a"*64,"activity_weight":3,"activity_evidence_hash":"1"*64},
       {"subject_hash":"b"*64,"activity_weight":1,"activity_evidence_hash":"2"*64}]

class TestHardening(unittest.TestCase):
 def test_current_allocation_fail_closed(self):
  r=simulate_epoch(POLICY,"2026-09-test",100000,USERS)
  self.assertFalse(r["simulation_ready"]);self.assertFalse(r["allocation_authorized"])
  self.assertEqual(r["theoretical_35_percent_budget_raw"],35000)
  self.assertIn("per_user_cap_not_approved",r["blockers"])
  self.assertIn("epoch_budget_cap_not_approved",r["blockers"])
  self.assertIn("distribution_reserve_account_not_configured",r["blockers"])
  self.assertEqual(r["simulated_allocations"],[])

 def test_hypothetical_approved_caps_conserve_budget_but_never_authorize(self):
  p=copy.deepcopy(POLICY); d=p["distribution_controls"]
  d["per_user_cap"]=20000; d["epoch_budget_cap"]=30000; d["distribution_reserve_account"]="R"*44
  p["signer_policy"]["production_policy_status"]="approved"
  r=simulate_epoch(p,"e",100000,USERS)
  self.assertTrue(r["simulation_ready"])
  self.assertTrue(r["conservation"]["assigned_le_budget"])
  self.assertFalse(r["allocation_authorized"]);self.assertFalse(r["financial_effect"])

 def test_duplicate_subject_rejected(self):
  with self.assertRaises(ValueError): simulate_epoch(POLICY,"e",1,[USERS[0],USERS[0]])

 def test_sensitive_allocation_input_rejected(self):
  u=copy.deepcopy(USERS);u[0]["private_key"]="x"
  with self.assertRaises(ValueError): simulate_epoch(POLICY,"e",1,u)

 def test_inventory_missing_is_fail_closed(self):
  r=build_inventory(POLICY,[])
  self.assertFalse(r["inventory_ready"])
  self.assertIn("verified_treasury_inventory_missing",r["blockers"])
  self.assertIn("distribution_reserve_account_not_configured",r["blockers"])

 def test_inventory_hash_only_attestation(self):
  p=copy.deepcopy(POLICY);p["distribution_controls"]["distribution_reserve_account"]="R"*44
  rows=[{"token_account_pubkey":"R"*44,"owner_pubkey":"O"*44,"ownership_attestation_hash":"3"*64,"balance_raw":123}]
  r=build_inventory(p,rows)
  self.assertTrue(r["inventory_ready"]);self.assertEqual(r["total_observed_balance_raw"],123)
  self.assertFalse(r["transfer_authorized"]);self.assertFalse(r["burn_authorized"])

 def test_inventory_secret_rejected(self):
  rows=[{"token_account_pubkey":"R"*44,"owner_pubkey":"O"*44,"ownership_attestation_hash":"3"*64,
         "balance_raw":123,"seed_phrase":"x"}]
  with self.assertRaises(ValueError): build_inventory(POLICY,rows)

 def test_reward_manifest_current_policy_blocked(self):
  i={"class":"reward_epoch","amount_raw":10,"intent_reference":"x","destination_reference_hash":"4"*64}
  r=build_manifest(POLICY,TREASURY,i,{"allocation":"5"*64})
  self.assertFalse(r["review_ready"]);self.assertEqual(r["minimum_multisig_approvals"],2)
  self.assertEqual(r["exact_remaining_signer_action"],"none_until_fail_closed_blockers_are_resolved")
  self.assertFalse(r["execution_authorized"])

 def test_burn_floor_violation_rejected_as_blocker(self):
  i={"class":"burn","amount_raw":1,"intent_reference":"x","post_burn_supply_raw":799999999999999999}
  r=build_manifest(POLICY,TREASURY,i,{"inventory":"5"*64})
  self.assertIn("burn_would_cross_8b_supply_floor",r["blockers"])
  self.assertEqual(r["minimum_multisig_approvals"],3)

 def test_manifest_transaction_material_rejected(self):
  i={"class":"treasury_transfer","amount_raw":10,"transaction_bytes":"deadbeef"}
  with self.assertRaises(ValueError): build_manifest(POLICY,TREASURY,i,{"inventory":"5"*64})

 def test_manifest_bad_prerequisite_hash_rejected(self):
  i={"class":"vesting_settlement","amount_raw":10}
  with self.assertRaises(ValueError): build_manifest(POLICY,TREASURY,i,{"vesting":"bad"})

 def test_readiness_truthful(self):
  fakehash="a"*64
  control={"control_plane_sha256":fakehash,"anti_whale":{"enforcement_ready":False},"blockers":["per_user_cap_not_approved"],
    "vesting_locking":{"locking_policy_status":"planning_only_until_authoritative_terms_approved"},
    "burn":{"verified_treasury_owned_burnable_raw":None}}
  allocation={"simulation_sha256":"b"*64,"simulation_ready":False,"blockers":["per_user_cap_not_approved"]}
  inventory={"receipt_sha256":"c"*64,"inventory_ready":False,"blockers":["verified_treasury_inventory_missing"]}
  monitoring={"monitoring_receipt_sha256":"d"*64,"severity":"degraded"}
  integrations={"integration_contracts_sha256":"e"*64}
  r=build_matrix(control,allocation,inventory,monitoring,integrations)
  self.assertFalse(r["financial_execution_ready"])
  self.assertEqual(r["truthful_readiness"],"control_plane_planning_hardened_execution_not_approved")
  self.assertTrue(r["domains"]["vault_forge_core"]["ready"])

if __name__=="__main__": unittest.main()
