import copy,unittest
from reward_allocation_accounting import build_allocation_accounting
from burn_program_planner import build_burn_program
from approval_evidence_chain import build_approval_packet

MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"; NET="solana-mainnet-beta"; H="a"*64
FAIL={"network":NET,"mint":MINT,"readiness":"FAIL_CLOSED","reconciliation_sha256":"b"*64,
 "binding_blockers":["per_user_cap_not_approved","epoch_budget_cap_not_approved"],
 "distribution":{"actionable_budget_raw":None,"per_user_cap":None},
 "burn":{"current_supply_raw":1_000_000_000_000_000_000,"theoretical_headroom_raw":200_000_000_000_000_000,
 "verified_burn_reserve_raw":None,"review_cap_raw":None},
 "approval_thresholds":{"reward_epoch":2,"vesting_settlement":2,"burn":3,"treasury_transfer":3}}
READY={"network":NET,"mint":MINT,"readiness":"READY_FOR_OFFLINE_APPROVAL_REVIEW","reconciliation_sha256":"c"*64,"binding_blockers":[],
 "distribution":{"actionable_budget_raw":1000,"per_user_cap":700},
 "burn":{"current_supply_raw":1_000_000_000_000_000_000,"theoretical_headroom_raw":200_000_000_000_000_000,
 "verified_burn_reserve_raw":100_000_000_000_000_000,"review_cap_raw":100_000_000_000_000_000},
 "approval_thresholds":{"reward_epoch":2,"vesting_settlement":2,"burn":3,"treasury_transfer":3}}
ELIG={"schema":"thf-tokenops-eligibility-evidence/v1","network":NET,"mint":MINT,"epoch_id":"2026-W37",
 "activity_evidence_set_sha256":H,"participants":[
 {"reward_account_pubkey":"11111111111111111111111111111111","weight":1,"eligibility_sha256":"1"*64},
 {"reward_account_pubkey":"SysvarRent111111111111111111111111111111111","weight":3,"eligibility_sha256":"2"*64}]}
BURN={"schema":"thf-tokenops-burn-program-proposal/v1","governance_proposal_sha256":"3"*64,
 "requested_total_burn_raw":50_000_000_000_000_000,"epochs":10}

class T(unittest.TestCase):
 def test_current_allocation_fail_closed(self):
  r=build_allocation_accounting(FAIL,ELIG); self.assertFalse(r["simulation_performed"]); self.assertIsNone(r["simulated_distributed_raw"]); self.assertFalse(r["settlement_authorized"])
 def test_ready_allocation_conserves(self):
  r=build_allocation_accounting(READY,ELIG); self.assertTrue(r["simulation_performed"]); self.assertTrue(r["conservation_proven"]); self.assertEqual(r["simulated_distributed_raw"]+r["simulated_remainder_raw"],1000); self.assertLessEqual(max(x["simulated_allocation_raw"] for x in r["simulated_rows"]),700)
 def test_duplicate_reward_account_rejected(self):
  e=copy.deepcopy(ELIG); e["participants"].append(copy.deepcopy(e["participants"][0]));
  with self.assertRaises(ValueError): build_allocation_accounting(READY,e)
 def test_secret_rejected(self):
  e=copy.deepcopy(ELIG); e["private_key"]="x";
  with self.assertRaises(ValueError): build_allocation_accounting(READY,e)
 def test_current_burn_fail_closed(self):
  r=build_burn_program(FAIL,BURN); self.assertFalse(r["review_ready"]); self.assertIsNone(r["reviewable_total_burn_raw"]); self.assertFalse(r["execution_authorized"])
 def test_ready_burn_respects_reserve_and_floor(self):
  r=build_burn_program(READY,BURN); self.assertTrue(r["review_ready"]); self.assertEqual(r["reviewable_total_burn_raw"],50_000_000_000_000_000); self.assertGreaterEqual(r["projected_supply_raw"],800_000_000_000_000_000)
 def test_burn_capped_by_verified_reserve(self):
  b=copy.deepcopy(BURN); b["requested_total_burn_raw"]=150_000_000_000_000_000; r=build_burn_program(READY,b); self.assertEqual(r["reviewable_total_burn_raw"],100_000_000_000_000_000)
 def test_burn_threshold_drift_blocks(self):
  q=copy.deepcopy(READY); q["approval_thresholds"]["burn"]=2; r=build_burn_program(q,BURN); self.assertFalse(r["review_ready"]); self.assertIn("burn_multisig_threshold_not_3",r["blockers"])
 def test_approval_packet_current_fail_closed(self):
  r=build_approval_packet("reward_epoch","4"*64,FAIL,"5"*64); self.assertFalse(r["ready_to_request_user_controlled_offline_approvals"]); self.assertEqual(r["required_approvals"],2); self.assertFalse(r["cryptographic_signatures_collected"])
 def test_approval_packet_ready_but_not_execution(self):
  r=build_approval_packet("burn","4"*64,READY,"5"*64); self.assertTrue(r["ready_to_request_user_controlled_offline_approvals"]); self.assertEqual(r["required_approvals"],3); self.assertFalse(r["execution_authorized"]); self.assertFalse(r["transaction_signed"])
 def test_approval_threshold_drift_raises(self):
  q=copy.deepcopy(READY); q["approval_thresholds"]["burn"]=2
  with self.assertRaises(ValueError): build_approval_packet("burn","4"*64,q)
 def test_approval_forbidden_signature_field(self):
  q=copy.deepcopy(READY); q["signature"]="x"
  with self.assertRaises(ValueError): build_approval_packet("reward_epoch","4"*64,q)

if __name__=="__main__": unittest.main()
