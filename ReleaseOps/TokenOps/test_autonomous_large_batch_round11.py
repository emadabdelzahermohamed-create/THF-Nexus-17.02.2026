import copy, unittest
from governance_authority_requirements import build_requirements
from treasury_evidence_bundle import build_bundle
from tokenops_readiness_compiler import compile_readiness

MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
POLICY={"version":1,"network":"solana-mainnet-beta","mint":MINT,
"verified":{"token_program":"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA","decimals":8,"current_supply_ui":"10000000000","mint_authority":None,"freeze_authority":None},
"economics":{"active_user_revenue_share":0.35,"approved_supply_floor_target_ui":"8000000000","burn_source_policy":"treasury_controlled_balances_only","minting_assumption":"disabled_immutable"},
"signer_policy":{"production_policy_status":"not_yet_approved"},
"distribution_controls":{"anti_sybil_required":True,"activity_evidence_required":True,"anti_whale_cap_required":True,"per_user_cap":None,"epoch_budget_cap":None,"claim_or_push_model":"to_be_selected_after_treasury_design"},
"isolation":{"wave_mawja":"must_not_be_touched"}}
TREASURY={"version":1,"network":"solana-mainnet-beta","mint":MINT,"control_model":"external_multisig_required",
"approval_classes":{"reward_epoch":{"minimum_approvals":2},"vesting_settlement":{"minimum_approvals":2},"burn":{"minimum_approvals":3,"supply_floor_ui":"8000000000"},"treasury_transfer":{"minimum_approvals":3}},
"hard_guards":{"wave_mawja_untouched":True}}
AUDIT={"network":"solana-mainnet-beta","mint":MINT,"rpc_slot":446797672,
"program_id":"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA","decimals":8,
"supply_raw":"1000000000000000000","supply_ui":"10000000000","mint_authority":None,"freeze_authority":None,
"largest_accounts_status":"unavailable","recent_signature_count":5}
VALID_ACCOUNT="7YttLkHDoPW7rBZMTEQHHXFfRxmLM6yMtk6h1cMTzZQh"
VALID_OWNER="11111111111111111111111111111111"
H="a"*64

class Round11(unittest.TestCase):
    def test_missing_governance_charter_fail_closed(self):
        g=build_requirements(POLICY,TREASURY)
        self.assertFalse(g["policy_mutation_ready_for_human_review"])
        self.assertIn("POLICY_MUTATION_GOVERNANCE_CHARTER_NOT_APPROVED",g["blockers"])
        self.assertFalse(g["policy_mutation_authorized"])

    def test_explicit_approved_charter_is_review_only(self):
        charter={"network":"solana-mainnet-beta","mint":MINT,"status":"approved",
                 "policy_mutation_scope":"tokenops_policy_parameters","minimum_approvals":3,
                 "decision_process":"dao_then_external_multisig","approval_evidence_sha256":H}
        g=build_requirements(POLICY,TREASURY,charter)
        self.assertTrue(g["policy_mutation_ready_for_human_review"])
        self.assertFalse(g["policy_mutation_authorized"])
        self.assertFalse(g["financial_effect"])

    def test_governance_threshold_never_inferred_from_treasury_actions(self):
        g=build_requirements(POLICY,TREASURY)
        self.assertNotIn("minimum_approvals",g)
        self.assertFalse(g["policy_mutation_authorized"])

    def test_treasury_empty_bundle_missing(self):
        b=build_bundle([],AUDIT)
        self.assertEqual(b["status"],"missing")
        self.assertIsNone(b["verified_treasury_owned_balance_raw"])
        self.assertFalse(b["authoritative_for_financial_execution"])

    def test_verified_public_treasury_evidence_is_still_nonexecuting(self):
        e={"network":"solana-mainnet-beta","mint":MINT,"token_account":VALID_ACCOUNT,"owner":VALID_OWNER,
           "role":"distribution_reserve","balance_raw":123456,"observed_slot":446797000,
           "ownership_evidence_sha256":H,"balance_evidence_sha256":"b"*64,
           "canonical_mint_verified":True,"owner_control_verified":True}
        b=build_bundle([e],AUDIT)
        self.assertEqual(b["status"],"verified")
        self.assertEqual(b["verified_treasury_owned_balance_raw"],123456)
        self.assertFalse(b["execution_authorized"])

    def test_stale_treasury_evidence_rejected(self):
        e={"network":"solana-mainnet-beta","mint":MINT,"token_account":VALID_ACCOUNT,"owner":VALID_OWNER,
           "role":"distribution_reserve","balance_raw":1,"observed_slot":446790000,
           "ownership_evidence_sha256":H,"balance_evidence_sha256":"b"*64,
           "canonical_mint_verified":True,"owner_control_verified":True}
        b=build_bundle([e],AUDIT,max_slot_lag=1500)
        self.assertEqual(b["status"],"incomplete")
        self.assertIn("stale_observation",b["rejected_entries"][0]["errors"])

    def test_current_readiness_has_nine_blockers(self):
        g=build_requirements(POLICY,TREASURY)
        b=build_bundle([],AUDIT)
        r=compile_readiness(POLICY,TREASURY,AUDIT,g,b)
        self.assertEqual(r["financial_gate_status"],"FAIL_CLOSED")
        self.assertEqual(r["blocker_count"],9)
        self.assertIn("POLICY_MUTATION_GOVERNANCE_UNAPPROVED",r["blockers"])
        self.assertEqual(r["exact_remaining_signer_action"],"none_until_fail_closed_blockers_are_resolved")

    def test_theoretical_burn_headroom_is_2b_not_authorization(self):
        g=build_requirements(POLICY,TREASURY); b=build_bundle([],AUDIT)
        r=compile_readiness(POLICY,TREASURY,AUDIT,g,b)
        self.assertEqual(r["economic_constraints"]["theoretical_burn_headroom_ui"],"2000000000")
        self.assertFalse(r["execution_authorized"])

    def test_onchain_drift_blocks(self):
        a=copy.deepcopy(AUDIT); a["mint_authority"]="unexpected"
        g=build_requirements(POLICY,TREASURY); b=build_bundle([],a)
        r=compile_readiness(POLICY,TREASURY,a,g,b)
        self.assertIn("ONCHAIN_CANONICAL_DRIFT",r["blockers"])
        self.assertEqual(r["onchain_core"]["status"],"DRIFT")

    def test_35_percent_drift_rejected(self):
        p=copy.deepcopy(POLICY); p["economics"]["active_user_revenue_share"]=0.34
        with self.assertRaises(ValueError): build_requirements(p,TREASURY)

    def test_sensitive_key_rejected(self):
        charter={"network":"solana-mainnet-beta","mint":MINT,"private_key":"x"}
        with self.assertRaises(ValueError): build_requirements(POLICY,TREASURY,charter)

if __name__=="__main__": unittest.main()
