import copy,unittest
from holder_concentration_evidence import build_holder_evidence
from public_treasury_registry import validate_registry
from financial_evidence_reconciliation import reconcile
from financial_evidence_lineage import build_lineage
MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
POLICY={"version":1,"network":"solana-mainnet-beta","mint":MINT,"economics":{"active_user_revenue_share":0.35,"approved_supply_floor_target_ui":"8000000000"},"signer_policy":{"production_policy_status":"not_yet_approved"},"distribution_controls":{"anti_sybil_required":True,"activity_evidence_required":True,"anti_whale_cap_required":True,"per_user_cap":None,"epoch_budget_cap":None,"claim_or_push_model":"to_be_selected_after_treasury_design"}}
TREASURY={"version":1,"network":"solana-mainnet-beta","mint":MINT,"control_model":"external_multisig_required","approval_classes":{"reward_epoch":{"minimum_approvals":2},"vesting_settlement":{"minimum_approvals":2},"burn":{"minimum_approvals":3},"treasury_transfer":{"minimum_approvals":3}}}
AUDIT={"network":"solana-mainnet-beta","mint":MINT,"rpc_slot":446762972,"program_id":"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA","decimals":8,"supply_raw":"1000000000000000000","supply_ui":"10000000000","mint_authority":None,"freeze_authority":None,"largest_accounts_status":"unavailable","largest_accounts":[],"recent_signatures_status":"ok","recent_signature_count":5}
EMPTY={"schema":"thf-tokenops-public-treasury-registry/v1","network":"solana-mainnet-beta","mint":MINT,"accounts":[]}
class T(unittest.TestCase):
 def test_holder_degraded_is_nonfatal(self):
  r=build_holder_evidence(AUDIT); self.assertFalse(r["holder_concentration_available"]);self.assertIsNone(r["top1_percent"])
 def test_holder_rows_require_ok_status(self):
  a=copy.deepcopy(AUDIT);a["largest_accounts"]=[{"address":"1"*32,"amount":"1"}]
  with self.assertRaises(ValueError):build_holder_evidence(a)
 def test_holder_percentages(self):
  a=copy.deepcopy(AUDIT);a["largest_accounts_status"]="ok";a["largest_accounts"]=[{"address":"2"*32,"amount":str(2*10**17)},{"address":"3"*32,"amount":str(10**17)}]
  r=build_holder_evidence(a);self.assertEqual(r["top1_percent"],20.0);self.assertEqual(r["top5_percent"],30.0)
 def test_empty_registry_fail_closed(self):
  r=validate_registry(EMPTY);self.assertFalse(r["authoritative_inventory_ready"]);self.assertIn("authoritative_public_treasury_registry_empty",r["blockers"])
 def test_registry_rejects_secret(self):
  x=copy.deepcopy(EMPTY);x["private_key"]="x"
  with self.assertRaises(ValueError): validate_registry(x)
 def test_current_state_reconciliation_fail_closed(self):
  h=build_holder_evidence(AUDIT);reg=validate_registry(EMPTY);r=reconcile(POLICY,TREASURY,AUDIT,h,reg,100000)
  self.assertEqual(r["readiness"],"FAIL_CLOSED");self.assertEqual(r["distribution"]["theoretical_35_percent_budget_raw"],35000);self.assertIsNone(r["distribution"]["actionable_budget_raw"]);self.assertIsNone(r["distribution"]["delivery_model"]);self.assertFalse(r["financial_effect"])
 def test_burn_headroom_is_2b(self):
  r=reconcile(POLICY,TREASURY,AUDIT,build_holder_evidence(AUDIT),validate_registry(EMPTY));self.assertEqual(r["burn"]["theoretical_headroom_raw"],2_000_000_000*10**8);self.assertIsNone(r["burn"]["review_cap_raw"])
 def test_policy_drift_rejected(self):
  p=copy.deepcopy(POLICY);p["economics"]["active_user_revenue_share"]=0.34
  with self.assertRaises(ValueError):reconcile(p,TREASURY,AUDIT,build_holder_evidence(AUDIT),validate_registry(EMPTY))
 def test_detached_holder_evidence_rejected(self):
  h=build_holder_evidence(AUDIT);h["audit_sha256"]="0"*64
  with self.assertRaises(ValueError):reconcile(POLICY,TREASURY,AUDIT,h,validate_registry(EMPTY))
 def test_thresholds_preserved(self):
  r=reconcile(POLICY,TREASURY,AUDIT,build_holder_evidence(AUDIT),validate_registry(EMPTY));self.assertEqual(r["approval_thresholds"],{"reward_epoch":2,"vesting_settlement":2,"burn":3,"treasury_transfer":3})
 def test_lineage_detects_tamper(self):
  r=reconcile(POLICY,TREASURY,AUDIT,build_holder_evidence(AUDIT),validate_registry(EMPTY));r["readiness"]="READY_FOR_OFFLINE_APPROVAL_REVIEW"
  with self.assertRaises(ValueError): build_lineage(r,"f"*40)
 def test_lineage_nonbinding(self):
  r=reconcile(POLICY,TREASURY,AUDIT,build_holder_evidence(AUDIT),validate_registry(EMPTY));l=build_lineage(r,"f"*40);self.assertFalse(l["execution_authorized"]);self.assertFalse(l["financial_effect"])
 def test_fully_populated_registry_still_never_authorizes(self):
  token="4"*32;owner="5"*32;reg={"schema":"thf-tokenops-public-treasury-registry/v1","network":"solana-mainnet-beta","mint":MINT,"accounts":[{"token_account_pubkey":token,"owner_pubkey":owner,"roles":["distribution_reserve","burn_reserve"],"governance_approval_hash":"a"*64,"balance_observation_hash":"b"*64,"observed_balance_raw":10**15}]}
  rr=validate_registry(reg);self.assertTrue(rr["authoritative_inventory_ready"]);p=copy.deepcopy(POLICY);p["distribution_controls"].update({"per_user_cap":1000,"epoch_budget_cap":5000,"distribution_reserve_account":token,"claim_or_push_model":"claim"});p["signer_policy"]["production_policy_status"]="approved";r=reconcile(p,TREASURY,AUDIT,build_holder_evidence(AUDIT),rr,100000);self.assertEqual(r["distribution"]["actionable_budget_raw"],5000);self.assertEqual(r["distribution"]["delivery_model"],"claim");self.assertFalse(r["distribution"]["allocation_authorized"]);self.assertFalse(r["burn"]["execution_authorized"])
 def test_legacy_delivery_alias_remains_compatible(self):
  token="4"*32;owner="5"*32;reg={"schema":"thf-tokenops-public-treasury-registry/v1","network":"solana-mainnet-beta","mint":MINT,"accounts":[{"token_account_pubkey":token,"owner_pubkey":owner,"roles":["distribution_reserve"],"governance_approval_hash":"a"*64,"balance_observation_hash":"b"*64,"observed_balance_raw":10**15}]};rr=validate_registry(reg);p=copy.deepcopy(POLICY);p["distribution_controls"].pop("claim_or_push_model",None);p["distribution_controls"].update({"per_user_cap":1000,"epoch_budget_cap":5000,"distribution_reserve_account":token,"distribution_delivery_model":"push"});p["signer_policy"]["production_policy_status"]="approved";r=reconcile(p,TREASURY,AUDIT,build_holder_evidence(AUDIT),rr,100000);self.assertEqual(r["distribution"]["delivery_model"],"push")
if __name__=="__main__":unittest.main()
