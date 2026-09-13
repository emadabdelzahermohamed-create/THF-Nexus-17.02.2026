#!/usr/bin/env python3
import copy
import unittest

from seal_bound_tx_review_manifest import build_review_manifest, canonical_sha256

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK = "solana-mainnet-beta"
SOURCE = {
    "policy_file_sha256": "1" * 64,
    "treasury_policy_file_sha256": "2" * 64,
    "lineage_source_sha256": "3" * 64,
    "policy_git_blob_sha": "a" * 40,
    "treasury_policy_git_blob_sha": "b" * 40,
    "source_commit_sha": "c" * 40,
}


def admission(eligible=False):
    doc = {
        "schema": "thf-tokenops-accounting-policy-seal-bound-admission/v1",
        "network": NETWORK,
        "mint": MINT,
        "review_request_id": "review-1",
        "accounting_policy_seal_sha256": "4" * 64,
        "base_bound_admission_sha256": "5" * 64,
        "lineage_checkpoint_sha256": "6" * 64,
        "policy_source": copy.deepcopy(SOURCE),
        "simulation_review_eligible": eligible,
        "blockers": [] if eligible else ["production_signer_policy_not_approved"],
        "execution": {
            "simulation_execution_permitted": False,
            "execution_authorized": False,
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
            "user_controlled_approval_required": True,
            "wave_mawja_untouched": True,
        },
    }
    doc["seal_bound_admission_sha256"] = canonical_sha256(doc)
    return doc


def policy():
    return {
        "network": NETWORK,
        "mint": MINT,
        "control_model": "external_multisig_required",
        "approval_classes": {
            "reward_epoch": {"minimum_approvals": 2, "execution": "external_multisig"},
            "vesting_settlement": {"minimum_approvals": 2, "execution": "external_multisig"},
            "burn": {"minimum_approvals": 3, "execution": "external_multisig"},
            "treasury_transfer": {"minimum_approvals": 3, "execution": "external_multisig"},
        },
    }


def request(op="reward_epoch", required=2):
    a = admission(False)
    return a, {
        "network": NETWORK,
        "mint": MINT,
        "request_id": "tx-review-1",
        "operation": op,
        "amount_raw": 100000000,
        "seal_bound_admission_sha256": a["seal_bound_admission_sha256"],
        "policy_source": copy.deepcopy(SOURCE),
        "required_approvals": required,
        "intent": {"purpose": "deterministic review evidence only"},
    }


class TestSealBoundTxReviewManifest(unittest.TestCase):
    def test_deterministic_and_fail_closed(self):
        a, r = request()
        x = build_review_manifest(a, r, policy())
        y = build_review_manifest(a, r, policy())
        self.assertEqual(x, y)
        self.assertFalse(x["review_ready"])
        self.assertEqual(x["required_external_multisig_approvals"], 2)
        self.assertEqual(x["exact_remaining_signer_action"], "none_until_fail_closed_blockers_are_resolved")
        self.assertFalse(x["execution"]["execution_authorized"])
        self.assertFalse(x["execution"]["transaction_bytes_created"])

    def test_hypothetical_review_ready_still_never_executes(self):
        a = admission(True)
        r = {
            "network": NETWORK, "mint": MINT, "request_id": "ready", "operation": "reward_epoch",
            "amount_raw": 1, "seal_bound_admission_sha256": a["seal_bound_admission_sha256"],
            "policy_source": copy.deepcopy(SOURCE), "required_approvals": 2, "intent": {},
        }
        out = build_review_manifest(a, r, policy())
        self.assertTrue(out["review_ready"])
        self.assertIn("at least 2 external multisig approvals", out["exact_remaining_signer_action"])
        self.assertFalse(out["execution"]["transaction_created"])
        self.assertFalse(out["execution"]["broadcast_allowed"])

    def test_detached_admission_rejected(self):
        a, r = request()
        r["seal_bound_admission_sha256"] = "9" * 64
        with self.assertRaises(ValueError): build_review_manifest(a, r, policy())

    def test_tampered_admission_rejected(self):
        a, r = request()
        a["blockers"].append("tampered")
        with self.assertRaises(ValueError): build_review_manifest(a, r, policy())

    def test_policy_source_replay_rejected(self):
        a, r = request()
        r["policy_source"]["source_commit_sha"] = "d" * 40
        with self.assertRaises(ValueError): build_review_manifest(a, r, policy())

    def test_threshold_mismatch_rejected(self):
        a, r = request("treasury_transfer", 2)
        with self.assertRaises(ValueError): build_review_manifest(a, r, policy())

    def test_sensitive_or_transaction_material_rejected(self):
        a, r = request()
        r["private_key"] = "forbidden"
        with self.assertRaises(ValueError): build_review_manifest(a, r, policy())
        a, r = request(); r["transaction_bytes"] = "00"
        with self.assertRaises(ValueError): build_review_manifest(a, r, policy())

    def test_burn_floor_and_verified_source_enforced(self):
        a, r = request("burn", 3)
        r.update({"current_supply_raw": 1000000000000000000, "supply_floor_raw": 800000000000000000, "source_control": "treasury_verified"})
        out = build_review_manifest(a, r, policy())
        self.assertEqual(out["required_external_multisig_approvals"], 3)
        r["amount_raw"] = 300000000000000000
        with self.assertRaises(ValueError): build_review_manifest(a, r, policy())

    def test_target_and_action_mismatch_rejected(self):
        a, r = request(); r["mint"] = "wrong"
        with self.assertRaises(ValueError): build_review_manifest(a, r, policy())
        a, r = request(); r["operation"] = "mint"
        with self.assertRaises(ValueError): build_review_manifest(a, r, policy())


if __name__ == "__main__":
    unittest.main()
