import json,unittest,copy
from control_plane_guardrails import build_control_plane
from integration_contracts import build_contracts
from incident_monitoring import build_monitoring_receipt

MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
POLICY={"version":1,"network":"solana-mainnet-beta","mint":MINT,
"economics":{"active_user_revenue_share":0.35,"approved_supply_floor_target_ui":"8000000000"},
"signer_policy":{"production_policy_status":"not_yet_approved"},
"distribution_controls":{"anti_sybil_required":True,"activity_evidence_required":True,
"anti_whale_cap_required":True,"per_user_cap":None,"epoch_budget_cap":None}}
TREASURY={"version":1,"network":"solana-mainnet-beta","mint":MINT,"control_model":"external_multisig_required",
"approval_classes":{"reward_epoch":{"minimum_approvals":2,"execution":"external_multisig"},
"vesting_settlement":{"minimum_approvals":2,"execution":"external_multisig"},
"burn":{"minimum_approvals":3,"execution":"external_multisig","supply_floor_ui":"8000000000"},
"treasury_transfer":{"minimum_approvals":3,"execution":"external_multisig"}}}
AUDIT={"network":"solana-mainnet-beta","mint":MINT,"rpc_slot":446720517,
"program_id":"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA","decimals":8,
"supply_raw":"1000000000000000000","supply_ui":"10000000000","mint_authority":None,
"freeze_authority":None,"largest_accounts_status":"unavailable","recent_signatures_status":"ok",
"recent_signature_count":5}

class TestLargeBatch(unittest.TestCase):
 def test_current_policy_is_fail_closed(self):
  r=build_control_plane(POLICY,TREASURY,AUDIT,100000)
  self.assertFalse(r["active_user_distribution"]["allocation_authorized"])
  self.assertIn("per_user_cap_not_approved",r["blockers"])
  self.assertIn("epoch_budget_cap_not_approved",r["blockers"])
  self.assertIn("production_signer_policy_not_approved",r["blockers"])
  self.assertEqual(r["active_user_distribution"]["theoretical_35_percent_budget_raw"],35000)
  self.assertFalse(r["execution"]["financial_effect"])

 def test_burn_math_respects_8b_floor(self):
  r=build_control_plane(POLICY,TREASURY,AUDIT,0,treasury_owned_burnable_raw=300_000_000*10**8)
  self.assertEqual(r["burn"]["theoretical_max_burn_raw"],2_000_000_000*10**8)
  self.assertEqual(r["burn"]["plan_cap_raw"],300_000_000*10**8)
  self.assertFalse(r["burn"]["execution_authorized"])

 def test_no_burn_source_means_no_plan_cap(self):
  r=build_control_plane(POLICY,TREASURY,AUDIT)
  self.assertIsNone(r["burn"]["plan_cap_raw"])

 def test_authority_drift_blocks(self):
  a=copy.deepcopy(AUDIT);a["mint_authority"]="UnexpectedAuthority"
  r=build_control_plane(POLICY,TREASURY,a)
  self.assertIn("mint_authority_reappeared",r["blockers"])

 def test_supply_below_floor_blocks(self):
  a=copy.deepcopy(AUDIT);a["supply_raw"]=str(7_999_999_999*10**8);a["supply_ui"]="7999999999"
  r=build_control_plane(POLICY,TREASURY,a)
  self.assertIn("supply_below_approved_floor",r["blockers"])

 def test_secret_field_rejected(self):
  p=copy.deepcopy(POLICY);p["private_key"]="x"
  with self.assertRaises(ValueError): build_control_plane(p,TREASURY,AUDIT)

 def test_integration_contracts_are_non_custodial(self):
  r=build_contracts(POLICY,TREASURY)
  self.assertFalse(r["financial_effect"]);self.assertFalse(r["broadcast_allowed"])
  self.assertIn("Vault",r["contracts"]);self.assertIn("Forge",r["contracts"]);self.assertIn("Core",r["contracts"])

 def test_integration_contract_rejects_signature(self):
  t=copy.deepcopy(TREASURY);t["signature"]="x"
  with self.assertRaises(ValueError): build_contracts(POLICY,t)

 def test_monitoring_degraded_on_holder_rpc_limit(self):
  cp=build_control_plane(POLICY,TREASURY,AUDIT)
  r=build_monitoring_receipt(AUDIT,cp["policy_sha256"],cp["treasury_policy_sha256"])
  self.assertEqual(r["severity"],"degraded")
  self.assertIn("degraded:holder_concentration_unavailable",r["alerts"])
  self.assertFalse(r["rollback"]["automatic_on_chain_action"])

 def test_monitoring_critical_on_program_drift(self):
  a=copy.deepcopy(AUDIT);a["program_id"]="bad"
  r=build_monitoring_receipt(a,"a"*64,"b"*64)
  self.assertEqual(r["severity"],"critical")
  self.assertEqual(r["recommended_control_plane_action"],"freeze_all_tokenops_planning_and_require_human_review")

 def test_thresholds(self):
  r=build_control_plane(POLICY,TREASURY,AUDIT)
  self.assertEqual(r["approval_thresholds"]["reward_epoch"],2)
  self.assertEqual(r["approval_thresholds"]["vesting_settlement"],2)
  self.assertEqual(r["approval_thresholds"]["burn"],3)
  self.assertEqual(r["approval_thresholds"]["treasury_transfer"],3)

if __name__=="__main__": unittest.main()
