#!/usr/bin/env python3
import copy
import unittest

from review_manifest_simulation_plan import (
    CANONICAL_MINT,
    CANONICAL_NETWORK,
    build_simulation_plan,
    canonical_sha256,
)


def base_manifest():
    m = {
        "schema": "thf-tokenops-seal-bound-unsigned-tx-review-manifest/v1",
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "request_id": "epoch-001",
        "operation": "reward_epoch",
        "amount_raw": 100000000,
        "intent": {"purpose": "active-user reward review"},
        "seal_bound_admission_sha256": "1" * 64,
        "accounting_policy_seal_sha256": "2" * 64,
        "base_bound_admission_sha256": "3" * 64,
        "lineage_checkpoint_sha256": "4" * 64,
        "policy_source": {},
        "required_external_multisig_approvals": 2,
        "review_ready": False,
        "blockers": ["policy_caps_not_approved"],
        "exact_remaining_signer_action": "none_until_fail_closed_blockers_are_resolved",
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
    m["review_manifest_sha256"] = canonical_sha256(m)
    return m


def base_policy():
    return {
        "version": 1,
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "economics": {
            "active_user_revenue_share": 0.35,
            "approved_supply_floor_target_ui": "8000000000",
        },
        "signer_policy": {"production_policy_status": "not_yet_approved"},
        "distribution_controls": {
            "anti_whale_cap_required": True,
            "per_user_cap": None,
            "epoch_budget_cap": None,
        },
    }


def base_treasury():
    return {
        "version": 1,
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


class SimulationPlanTests(unittest.TestCase):
    def test_current_policy_is_fail_closed(self):
        result = build_simulation_plan(base_manifest(), base_policy(), base_treasury())
        self.assertFalse(result["simulation_eligible"])
        self.assertIn("per_user_cap_not_approved", result["blockers"])
        self.assertIn("epoch_budget_cap_not_approved", result["blockers"])
        self.assertIn("production_signer_policy_not_approved", result["blockers"])
        self.assertFalse(result["execution"]["broadcast_allowed"])
        self.assertFalse(result["execution"]["financial_effect"])

    def test_deterministic_digest(self):
        a = build_simulation_plan(base_manifest(), base_policy(), base_treasury())
        b = build_simulation_plan(base_manifest(), base_policy(), base_treasury())
        self.assertEqual(a["simulation_plan_sha256"], b["simulation_plan_sha256"])

    def test_tampered_manifest_digest_rejected(self):
        m = base_manifest()
        m["amount_raw"] += 1
        with self.assertRaises(ValueError):
            build_simulation_plan(m, base_policy(), base_treasury())

    def test_unsafe_execution_flag_rejected(self):
        m = base_manifest()
        m["execution"]["transaction_signed"] = True
        m["review_manifest_sha256"] = canonical_sha256({k: v for k, v in m.items() if k != "review_manifest_sha256"})
        with self.assertRaises(ValueError):
            build_simulation_plan(m, base_policy(), base_treasury())

    def test_sensitive_material_rejected(self):
        m = base_manifest()
        m["intent"]["private_key"] = "forbidden"
        m["review_manifest_sha256"] = canonical_sha256({k: v for k, v in m.items() if k != "review_manifest_sha256"})
        with self.assertRaises(ValueError):
            build_simulation_plan(m, base_policy(), base_treasury())

    def test_35_percent_policy_drift_rejected(self):
        p = base_policy()
        p["economics"]["active_user_revenue_share"] = 0.34
        with self.assertRaises(ValueError):
            build_simulation_plan(base_manifest(), p, base_treasury())

    def test_8b_floor_policy_drift_rejected(self):
        p = base_policy()
        p["economics"]["approved_supply_floor_target_ui"] = "7900000000"
        with self.assertRaises(ValueError):
            build_simulation_plan(base_manifest(), p, base_treasury())

    def test_multisig_threshold_drift_rejected(self):
        t = base_treasury()
        t["approval_classes"]["reward_epoch"]["minimum_approvals"] = 3
        with self.assertRaises(ValueError):
            build_simulation_plan(base_manifest(), base_policy(), t)

    def test_missing_hard_guard_rejected(self):
        t = base_treasury()
        t["hard_guards"]["broadcast_from_ci_forbidden"] = False
        with self.assertRaises(ValueError):
            build_simulation_plan(base_manifest(), base_policy(), t)

    def test_hypothetical_complete_policy_still_never_authorizes_execution(self):
        m = base_manifest()
        m["review_ready"] = True
        m["blockers"] = []
        m["review_manifest_sha256"] = canonical_sha256({k: v for k, v in m.items() if k != "review_manifest_sha256"})
        p = base_policy()
        p["distribution_controls"]["per_user_cap"] = 1000
        p["distribution_controls"]["epoch_budget_cap"] = 100000
        p["signer_policy"]["production_policy_status"] = "approved"
        result = build_simulation_plan(m, p, base_treasury())
        self.assertTrue(result["simulation_eligible"])
        self.assertFalse(result["execution"]["execution_authorized"])
        self.assertFalse(result["execution"]["transaction_created"])
        self.assertFalse(result["execution"]["broadcast_allowed"])
        self.assertTrue(result["execution"]["user_controlled_approval_required"])


if __name__ == "__main__":
    unittest.main()
