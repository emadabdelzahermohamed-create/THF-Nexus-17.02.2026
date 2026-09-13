import copy,json,unittest
from pathlib import Path
from policy_blocker_registry import build_registry
from treasury_risk_envelope import build_risk_envelope
from financial_readiness_attestation import build_attestation

HERE=Path(__file__).resolve().parent
POLICY=json.loads((HERE/"policy.json").read_text())
TREASURY=json.loads((HERE/"treasury_policy.json").read_text())
AUDIT={"network":"solana-mainnet-beta","mint":POLICY["mint"],"rpc_slot":446751573,"account_exists":True,
"program_id":"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA","parsed_account_type":"mint","decimals":8,
"supply_raw":"1000000000000000000","supply_ui":"10000000000","mint_authority":None,"freeze_authority":None,
"is_initialized":True,"largest_accounts_status":"unavailable","largest_accounts":[],"recent_signatures_status":"ok","recent_signature_count":5,"recent_signatures":[]}

class TestFinancialReadinessBatch(unittest.TestCase):
    def test_current_state_fail_closed(self):
        r=build_registry(POLICY,TREASURY,AUDIT)
        self.assertEqual(r["financial_gate_status"],"FAIL_CLOSED")
        codes={x["code"] for x in r["blockers"]}
        for c in ("PER_USER_CAP_UNAPPROVED","EPOCH_BUDGET_CAP_UNAPPROVED","DISTRIBUTION_RESERVE_UNAPPROVED","PRODUCTION_SIGNER_POLICY_UNAPPROVED","VESTING_TERMS_UNAPPROVED","LOCK_REWARD_TERMS_UNAPPROVED","TREASURY_OWNERSHIP_BALANCE_UNVERIFIED"):
            self.assertIn(c,codes)
        self.assertEqual(r["exact_remaining_signer_action"],"none_until_fail_closed_blockers_are_resolved")
        self.assertFalse(r["financial_effect"])
    def test_holder_concentration_is_degraded_optional(self):
        r=build_registry(POLICY,TREASURY,AUDIT); o=[x for x in r["observations"] if x["code"]=="HOLDER_CONCENTRATION_UNAVAILABLE"]
        self.assertEqual(len(o),1); self.assertFalse(o[0]["blocks_binding_financial_action"])
    def test_burn_ceiling_is_2b_at_10b_supply(self):
        r=build_risk_envelope(POLICY,TREASURY,AUDIT)
        self.assertEqual(r["supply"]["theoretical_max_burn_raw"],2_000_000_000*10**8)
        self.assertIsNone(r["burn"]["review_burn_cap_raw"]); self.assertIsNone(r["burn"]["actionable_burn_amount_raw"])
    def test_verified_treasury_balance_only_limits_review_not_execution(self):
        ev={"status":"verified","network":"solana-mainnet-beta","mint":POLICY["mint"],"verified_treasury_owned_balance_raw":250_000_000*10**8}
        r=build_risk_envelope(POLICY,TREASURY,AUDIT,treasury_evidence=ev)
        self.assertEqual(r["burn"]["review_burn_cap_raw"],250_000_000*10**8); self.assertIsNone(r["burn"]["actionable_burn_amount_raw"]); self.assertFalse(r["execution_authorized"])
    def test_35pct_math_but_no_actionable_budget_without_caps(self):
        r=build_risk_envelope(POLICY,TREASURY,AUDIT,epoch_revenue_raw=100_000_000)
        self.assertEqual(r["distribution"]["theoretical_35pct_budget_raw"],35_000_000); self.assertIsNone(r["distribution"]["review_epoch_budget_raw"]); self.assertIsNone(r["distribution"]["actionable_allocation_budget_raw"])
    def test_multisig_thresholds_preserved(self):
        r=build_risk_envelope(POLICY,TREASURY,AUDIT)
        self.assertEqual(r["distribution"]["minimum_approvals"],2); self.assertEqual(r["vesting_locking"]["vesting_minimum_approvals"],2); self.assertEqual(r["burn"]["minimum_approvals"],3); self.assertEqual(r["treasury_transfer"]["minimum_approvals"],3)
    def test_authority_drift_becomes_hard_blocker(self):
        a=copy.deepcopy(AUDIT); a["mint_authority"]="Unexpected"; r=build_registry(POLICY,TREASURY,a)
        self.assertIn("ONCHAIN_CANONICAL_DRIFT",{x["code"] for x in r["blockers"]})
    def test_sensitive_fields_rejected(self):
        p=copy.deepcopy(POLICY); p["private_key"]="never"
        with self.assertRaises(ValueError): build_registry(p,TREASURY,AUDIT)
    def test_attestation_binds_evidence_and_never_claims_complete(self):
        reg=build_registry(POLICY,TREASURY,AUDIT); risk=build_risk_envelope(POLICY,TREASURY,AUDIT); a=build_attestation(POLICY,TREASURY,AUDIT,reg,risk)
        self.assertEqual(a["readiness_status"],"FAIL_CLOSED"); self.assertFalse(a["claims"]["financial_gate_complete"]); self.assertFalse(a["execution"]["broadcast_allowed"]); self.assertFalse(a["execution"]["financial_effect"])
    def test_attestation_rejects_tampering(self):
        reg=build_registry(POLICY,TREASURY,AUDIT); risk=build_risk_envelope(POLICY,TREASURY,AUDIT); bad=copy.deepcopy(reg); bad["policy_sha256"]="0"*64
        with self.assertRaises(ValueError): build_attestation(POLICY,TREASURY,AUDIT,bad,risk)

if __name__=="__main__": unittest.main()
