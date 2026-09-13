#!/usr/bin/env python3
import copy
import unittest

from simulation_review_receipt import build_simulation_review_receipt, canonical_sha256

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"


def make_plan(*, eligible=False, blockers=None):
    if blockers is None:
        blockers = [] if eligible else ["per_user_cap_not_approved"]
    plan = {
        "schema": "thf-tokenops-review-manifest-bound-simulation-plan/v1",
        "network": "solana-mainnet-beta",
        "mint": MINT,
        "operation": "reward_epoch",
        "amount_raw": 100000000,
        "review_manifest_sha256": "1" * 64,
        "seal_bound_admission_sha256": "2" * 64,
        "accounting_policy_seal_sha256": "3" * 64,
        "lineage_checkpoint_sha256": "4" * 64,
        "required_external_multisig_approvals": 2,
        "policy_sha256": "5" * 64,
        "treasury_policy_sha256": "6" * 64,
        "simulation_eligible": eligible,
        "blockers": blockers,
        "exact_remaining_signer_action": (
            "user_controlled_approval_then_external_multisig_simulation_review"
            if eligible else "none_until_fail_closed_blockers_are_resolved"
        ),
        "simulation_intent": {
            "mode": "non_executable_review_only",
            "construct_solana_instructions": False,
            "construct_transaction_bytes": False,
            "rpc_simulation_submitted": False,
        },
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
    plan["simulation_plan_sha256"] = canonical_sha256(plan)
    return plan


def good_summary():
    return {
        "source": "sanitized_external_simulation_summary",
        "slot": 446700000,
        "commitment": "confirmed",
        "ok": True,
        "err_code": None,
        "units_consumed": 42000,
        "logs_sha256": "a" * 64,
        "accounts_data_sha256": "b" * 64,
        "return_data_sha256": None,
    }


class SimulationReviewReceiptTests(unittest.TestCase):
    def test_ineligible_plan_builds_not_run_receipt(self):
        receipt = build_simulation_review_receipt(make_plan())
        self.assertFalse(receipt["simulation_attempted"])
        self.assertFalse(receipt["simulation_review_passed"])
        self.assertEqual(receipt["outcome"], "not_run_fail_closed")
        self.assertFalse(receipt["execution"]["execution_authorized"])
        self.assertFalse(receipt["execution"]["broadcast_allowed"])

    def test_summary_rejected_when_plan_ineligible(self):
        with self.assertRaises(ValueError):
            build_simulation_review_receipt(make_plan(), good_summary())

    def test_eligible_success_is_review_only(self):
        receipt = build_simulation_review_receipt(make_plan(eligible=True), good_summary())
        self.assertTrue(receipt["simulation_attempted"])
        self.assertTrue(receipt["simulation_review_passed"])
        self.assertEqual(receipt["outcome"], "simulation_passed_review_only")
        self.assertFalse(receipt["execution"]["execution_authorized"])
        self.assertFalse(receipt["execution"]["transaction_signed"])
        self.assertFalse(receipt["execution"]["transaction_submitted"])

    def test_failed_simulation_never_authorizes_execution(self):
        summary = good_summary()
        summary["ok"] = False
        summary["err_code"] = "InstructionError"
        receipt = build_simulation_review_receipt(make_plan(eligible=True), summary)
        self.assertFalse(receipt["simulation_review_passed"])
        self.assertEqual(receipt["outcome"], "simulation_failed_review_only")
        self.assertFalse(receipt["execution"]["execution_authorized"])

    def test_tampered_plan_digest_rejected(self):
        plan = make_plan()
        plan["amount_raw"] += 1
        with self.assertRaises(ValueError):
            build_simulation_review_receipt(plan)

    def test_raw_logs_rejected(self):
        summary = good_summary()
        summary["logs"] = ["Program log: forbidden raw content"]
        with self.assertRaises(ValueError):
            build_simulation_review_receipt(make_plan(eligible=True), summary)

    def test_transaction_bytes_rejected(self):
        summary = good_summary()
        summary["transaction_bytes"] = "deadbeef"
        with self.assertRaises(ValueError):
            build_simulation_review_receipt(make_plan(eligible=True), summary)

    def test_private_key_rejected_anywhere(self):
        plan = make_plan()
        plan["metadata"] = {"private_key": "never"}
        plan["simulation_plan_sha256"] = canonical_sha256({k: v for k, v in plan.items() if k != "simulation_plan_sha256"})
        with self.assertRaises(ValueError):
            build_simulation_review_receipt(plan)

    def test_summary_digest_is_deterministic(self):
        plan = make_plan(eligible=True)
        r1 = build_simulation_review_receipt(plan, good_summary())
        r2 = build_simulation_review_receipt(copy.deepcopy(plan), copy.deepcopy(good_summary()))
        self.assertEqual(r1["sanitized_summary_sha256"], r2["sanitized_summary_sha256"])
        self.assertEqual(r1["simulation_review_receipt_sha256"], r2["simulation_review_receipt_sha256"])

    def test_success_with_err_code_rejected(self):
        summary = good_summary()
        summary["err_code"] = "unexpected"
        with self.assertRaises(ValueError):
            build_simulation_review_receipt(make_plan(eligible=True), summary)


if __name__ == "__main__":
    unittest.main()
