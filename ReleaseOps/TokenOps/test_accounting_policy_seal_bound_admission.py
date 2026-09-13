#!/usr/bin/env python3
import copy
import unittest

from accounting_policy_seal_bound_admission import (
    CANONICAL_MINT,
    CANONICAL_NETWORK,
    canonical_sha256,
    evaluate_accounting_policy_seal_bound_admission,
)

H64A = "a" * 64
H64B = "b" * 64
H64C = "c" * 64
H40A = "a" * 40
H40B = "b" * 40
H40C = "c" * 40


def base_admission(eligible=False):
    doc = {
        "gate": "THF_TOKENOPS_POLICY_COMPLETION_BOUND_UNSIGNED_ADMISSION_V1",
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "intent": "reward_epoch_review",
        "simulation_review_eligible": eligible,
        "blockers": [] if eligible else ["policy_completion_not_authoritatively_completed"],
        "simulation_execution_permitted": False,
        "execution_authorized": False,
        "transaction_created": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "broadcast_allowed": False,
        "financial_effect": False,
        "private_key_used": False,
        "wave_mawja_untouched": True,
    }
    doc["bound_admission_sha256"] = canonical_sha256(doc)
    return doc


def accounting_seal(eligible=False):
    doc = {
        "schema": "thf-tokenops-accounting-policy-source-seal/v1",
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "request_id": "seal-test",
        "lineage_checkpoint_sha256": H64C,
        "policy_source": {
            "policy_file_sha256": H64A,
            "policy_git_blob_sha": H40A,
            "treasury_policy_file_sha256": H64B,
            "treasury_policy_git_blob_sha": H40B,
            "lineage_source_sha256": H64C,
            "source_commit_sha": H40C,
        },
        "policy_invariants": {
            "active_user_revenue_share": "35%",
            "approved_supply_floor_target_ui": "8000000000",
            "external_multisig_required": True,
        },
        "seal_review_eligible": eligible,
        "blockers": [] if eligible else ["anti_whale_caps_not_authoritatively_configured"],
        "execution": {
            "transaction_created": False,
            "transaction_signed": False,
            "transaction_submitted": False,
            "broadcast_allowed": False,
            "financial_effect": False,
            "settlement_executed": False,
            "burn_executed": False,
            "treasury_migrated": False,
            "dao_decision_executed": False,
            "private_key_used": False,
            "external_multisig_required": True,
            "wave_mawja_untouched": True,
        },
    }
    doc["accounting_policy_seal_sha256"] = canonical_sha256(doc)
    return doc


def request(base, seal):
    return {
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "review_request_id": "review-001",
        "accounting_policy_seal_sha256": seal["accounting_policy_seal_sha256"],
        "base_bound_admission_sha256": base["bound_admission_sha256"],
        "policy_source": copy.deepcopy(seal["policy_source"]),
    }


class SealBoundAdmissionTests(unittest.TestCase):
    def test_current_policy_remains_fail_closed(self):
        base = base_admission(False)
        seal = accounting_seal(False)
        result = evaluate_accounting_policy_seal_bound_admission(base, seal, request(base, seal))
        self.assertFalse(result["simulation_review_eligible"])
        self.assertIn("accounting_policy_seal_not_review_eligible", result["blockers"])
        self.assertIn("base_unsigned_admission_not_review_eligible", result["blockers"])
        self.assertFalse(result["execution"]["financial_effect"])
        self.assertFalse(result["execution"]["transaction_signed"])
        self.assertTrue(result["execution"]["user_controlled_approval_required"])
        self.assertTrue(result["execution"]["wave_mawja_untouched"])

    def test_completed_review_can_only_be_review_eligible_not_execution_authorized(self):
        base = base_admission(True)
        seal = accounting_seal(True)
        result = evaluate_accounting_policy_seal_bound_admission(base, seal, request(base, seal))
        self.assertTrue(result["simulation_review_eligible"])
        self.assertFalse(result["execution"]["execution_authorized"])
        self.assertFalse(result["execution"]["simulation_execution_permitted"])
        self.assertTrue(result["execution"]["external_multisig_required"])
        self.assertTrue(result["execution"]["user_controlled_approval_required"])

    def test_tampered_seal_digest_rejected(self):
        base = base_admission(False)
        seal = accounting_seal(False)
        req = request(base, seal)
        seal["blockers"].append("tampered")
        with self.assertRaisesRegex(ValueError, "accounting policy seal SHA-256 mismatch"):
            evaluate_accounting_policy_seal_bound_admission(base, seal, req)

    def test_tampered_base_admission_rejected(self):
        base = base_admission(False)
        seal = accounting_seal(False)
        req = request(base, seal)
        base["blockers"].append("tampered")
        with self.assertRaisesRegex(ValueError, "base admission SHA-256 mismatch"):
            evaluate_accounting_policy_seal_bound_admission(base, seal, req)

    def test_policy_source_replay_rejected(self):
        base = base_admission(False)
        seal = accounting_seal(False)
        req = request(base, seal)
        req["policy_source"]["source_commit_sha"] = "d" * 40
        with self.assertRaisesRegex(ValueError, "policy/source replay mismatch"):
            evaluate_accounting_policy_seal_bound_admission(base, seal, req)

    def test_detached_seal_rejected(self):
        base = base_admission(False)
        seal = accounting_seal(False)
        req = request(base, seal)
        req["accounting_policy_seal_sha256"] = "d" * 64
        with self.assertRaisesRegex(ValueError, "detached from accounting policy seal"):
            evaluate_accounting_policy_seal_bound_admission(base, seal, req)

    def test_sensitive_material_rejected(self):
        base = base_admission(False)
        seal = accounting_seal(False)
        req = request(base, seal)
        req["private_key"] = "forbidden"
        with self.assertRaisesRegex(ValueError, "forbidden sensitive/signature field"):
            evaluate_accounting_policy_seal_bound_admission(base, seal, req)

    def test_unsafe_execution_claim_rejected(self):
        base = base_admission(False)
        seal = accounting_seal(False)
        req = request(base, seal)
        base["transaction_signed"] = True
        base["bound_admission_sha256"] = canonical_sha256({k: v for k, v in base.items() if k != "bound_admission_sha256"})
        with self.assertRaisesRegex(ValueError, "unsafe base admission execution flag"):
            evaluate_accounting_policy_seal_bound_admission(base, seal, req)


if __name__ == "__main__":
    unittest.main()
