import unittest

from simulation_receipt_approval_readiness import (
    CANONICAL_MINT,
    CANONICAL_NETWORK,
    RECEIPT_SCHEMA,
    build_approval_readiness,
    canonical_sha256,
)


def receipt(passed=False, blockers=None, operation="reward_epoch"):
    blockers = blockers or []
    body = {
        "schema": RECEIPT_SCHEMA,
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "operation": operation,
        "amount_raw": 1000,
        "simulation_plan_sha256": "1" * 64,
        "review_manifest_sha256": "2" * 64,
        "policy_sha256": "3" * 64,
        "treasury_policy_sha256": "4" * 64,
        "simulation_eligible": passed,
        "simulation_attempted": passed,
        "simulation_review_passed": passed,
        "outcome": "simulation_passed_review_only" if passed else "not_run_fail_closed",
        "blockers": blockers,
        "sanitized_summary_sha256": "5" * 64 if passed else None,
        "simulation_observation": {
            "slot": 1 if passed else None,
            "commitment": "finalized" if passed else None,
            "err_code": None,
            "units_consumed": 10 if passed else None,
            "raw_logs_stored": False,
            "raw_account_data_stored": False,
            "raw_rpc_response_stored": False,
        },
        "exact_remaining_signer_action": "review",
        "execution": {
            "transaction_instructions_created": False,
            "transaction_bytes_created": False,
            "transaction_created": False,
            "transaction_signed": False,
            "transaction_submitted": False,
            "broadcast_allowed": False,
            "execution_authorized": False,
            "financial_effect": False,
            "private_key_used": False,
            "external_multisig_required": True,
            "user_controlled_approval_required": True,
            "wave_mawja_untouched": True,
        },
    }
    body["simulation_review_receipt_sha256"] = canonical_sha256(body)
    return body


def policy(complete=False):
    return {
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "economics": {
            "active_user_revenue_share": 0.35,
            "approved_supply_floor_target_ui": "8000000000",
        },
        "signer_policy": {"production_policy_status": "approved" if complete else "not_yet_approved"},
        "distribution_controls": {
            "anti_whale_cap_required": True,
            "per_user_cap": 100 if complete else None,
            "epoch_budget_cap": 10000 if complete else None,
        },
    }


def treasury():
    return {
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "control_model": "external_multisig_required",
        "approval_classes": {
            "reward_epoch": {"minimum_approvals": 2, "execution": "external_multisig"},
            "vesting_settlement": {"minimum_approvals": 2, "execution": "external_multisig"},
            "burn": {"minimum_approvals": 3, "execution": "external_multisig"},
            "treasury_transfer": {"minimum_approvals": 3, "execution": "external_multisig"},
        },
        "hard_guards": {
            "seed_phrase_forbidden": True,
            "private_key_forbidden": True,
            "persistent_hot_wallet_forbidden": True,
            "broadcast_from_ci_forbidden": True,
            "authority_change_forbidden": True,
            "minting_forbidden": True,
            "third_party_balance_burn_forbidden": True,
            "wave_mawja_untouched": True,
        },
    }


class GateTests(unittest.TestCase):
    def test_current_policy_fails_closed(self):
        out = build_approval_readiness(receipt(False), policy(False), treasury())
        self.assertFalse(out["approval_readiness"])
        self.assertIn("per_user_cap_not_approved", out["blockers"])
        self.assertIn("epoch_budget_cap_not_approved", out["blockers"])
        self.assertIn("production_signer_policy_not_approved", out["blockers"])
        self.assertIn("simulation_review_not_passed", out["blockers"])
        self.assertEqual(out["exact_remaining_signer_action"], "none_until_fail_closed_blockers_are_resolved")
        self.assertFalse(out["execution"]["execution_authorized"])

    def test_hypothetical_complete_policy_is_review_ready_only(self):
        out = build_approval_readiness(receipt(True), policy(True), treasury())
        self.assertTrue(out["approval_readiness"])
        self.assertEqual(out["required_external_multisig_approvals"], 2)
        self.assertEqual(out["approval_collection"]["approvals_collected"], 0)
        self.assertEqual(out["approval_collection"]["signatures_collected"], 0)
        self.assertFalse(out["execution"]["execution_authorized"])
        self.assertFalse(out["execution"]["broadcast_allowed"])

    def test_burn_threshold_is_three(self):
        out = build_approval_readiness(receipt(True, operation="burn"), policy(True), treasury())
        self.assertEqual(out["required_external_multisig_approvals"], 3)
        self.assertIn("collect_3_external_multisig_approvals_offline", out["exact_remaining_signer_action"])

    def test_tampered_receipt_rejected(self):
        r = receipt(False)
        r["amount_raw"] = 999
        with self.assertRaises(ValueError):
            build_approval_readiness(r, policy(False), treasury())

    def test_sensitive_material_rejected(self):
        r = receipt(False)
        r["private_key"] = "forbidden"
        r["simulation_review_receipt_sha256"] = canonical_sha256({k: v for k, v in r.items() if k != "simulation_review_receipt_sha256"})
        with self.assertRaises(ValueError):
            build_approval_readiness(r, policy(False), treasury())

    def test_policy_drift_rejected(self):
        p = policy(False)
        p["economics"]["active_user_revenue_share"] = 0.34
        with self.assertRaises(ValueError):
            build_approval_readiness(receipt(False), p, treasury())

    def test_wave_guard_missing_rejected(self):
        t = treasury()
        t["hard_guards"]["wave_mawja_untouched"] = False
        with self.assertRaises(ValueError):
            build_approval_readiness(receipt(False), policy(False), t)


if __name__ == "__main__":
    unittest.main()
