#!/usr/bin/env python3
import copy
import json
import unittest
from pathlib import Path

from anti_whale_reward_policy_completion_gate import canonical_sha256, evaluate_policy_completion

BASE = Path(__file__).resolve().parent


def load(name):
    return json.loads((BASE / name).read_text())


class PolicyCompletionTests(unittest.TestCase):
    def setUp(self):
        self.policy = load("policy.json")
        self.treasury = load("treasury_policy.json")
        self.completion = load("anti_whale_reward_policy_completion.json")

    def test_production_state_is_fail_closed_without_invented_caps(self):
        out = evaluate_policy_completion(self.completion, self.policy, self.treasury)
        self.assertFalse(out["authoritatively_completed"])
        self.assertFalse(out["simulation_review_eligible"])
        self.assertFalse(out["execution_authorized"])
        self.assertIn("anti_whale_caps_not_authoritatively_configured", out["blockers"])
        self.assertIn("governance_provenance_incomplete", out["blockers"])
        self.assertIn("production_caps_not_approved", out["blockers"])

    def completed_fixture(self):
        policy = copy.deepcopy(self.policy)
        policy["distribution_controls"]["per_user_cap"] = "1000"
        policy["distribution_controls"]["epoch_budget_cap"] = "100000"
        completion = copy.deepcopy(self.completion)
        completion["authoritative_policy_sha256"] = canonical_sha256(policy)
        completion["status"] = "authoritatively_completed"
        completion["production_caps_configured"] = True
        completion["anti_whale"]["per_user_cap_ui"] = "1000"
        completion["anti_whale"]["epoch_budget_cap_ui"] = "100000"
        completion["reward_epoch"]["epoch_budget_cap_ui"] = "100000"
        completion["governance_provenance"] = {
            "status": "approved",
            "decision_id": "TEST-FIXTURE-NOT-PRODUCTION",
            "approval_record_sha256": "a" * 64,
            "governance_policy_sha256": "b" * 64,
            "approved_at": "2026-09-13T00:00:00Z"
        }
        return completion, policy

    def test_completed_fixture_can_only_complete_with_matching_repo_policy_and_governance(self):
        completion, policy = self.completed_fixture()
        out = evaluate_policy_completion(completion, policy, self.treasury)
        self.assertTrue(out["authoritatively_completed"])
        self.assertEqual(out["blockers"], [])
        self.assertFalse(out["simulation_review_eligible"])
        self.assertFalse(out["execution_authorized"])

    def test_caps_without_repo_policy_binding_stay_blocked(self):
        completion, _ = self.completed_fixture()
        completion["authoritative_policy_sha256"] = canonical_sha256(self.policy)
        completion["status"] = "incomplete"
        out = evaluate_policy_completion(completion, self.policy, self.treasury)
        self.assertFalse(out["authoritatively_completed"])
        self.assertIn("authoritative_repo_policy_caps_incomplete_or_mismatched", out["blockers"])

    def test_per_user_cap_cannot_exceed_epoch_budget(self):
        completion, policy = self.completed_fixture()
        completion["anti_whale"]["per_user_cap_ui"] = "200000"
        with self.assertRaisesRegex(ValueError, "per-user cap"):
            evaluate_policy_completion(completion, policy, self.treasury)

    def test_reward_epoch_cap_must_match_anti_whale_epoch_cap(self):
        completion, policy = self.completed_fixture()
        completion["reward_epoch"]["epoch_budget_cap_ui"] = "99999"
        with self.assertRaisesRegex(ValueError, "reward epoch budget"):
            evaluate_policy_completion(completion, policy, self.treasury)

    def test_exact_35_percent_share_cannot_drift(self):
        completion = copy.deepcopy(self.completion)
        completion["active_user_revenue_share"] = 0.34
        with self.assertRaisesRegex(ValueError, "35%"):
            evaluate_policy_completion(completion, self.policy, self.treasury)

    def test_authoritative_policy_digest_is_required(self):
        completion = copy.deepcopy(self.completion)
        completion["authoritative_policy_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "authoritative policy SHA-256 mismatch"):
            evaluate_policy_completion(completion, self.policy, self.treasury)

    def test_sensitive_material_is_rejected(self):
        completion = copy.deepcopy(self.completion)
        completion["private_key"] = "forbidden"
        with self.assertRaisesRegex(ValueError, "forbidden sensitive"):
            evaluate_policy_completion(completion, self.policy, self.treasury)

    def test_execution_flags_cannot_be_enabled(self):
        completion = copy.deepcopy(self.completion)
        completion["safety"]["transaction_broadcast"] = True
        with self.assertRaisesRegex(ValueError, "unsafe completion state"):
            evaluate_policy_completion(completion, self.policy, self.treasury)


if __name__ == "__main__":
    unittest.main(verbosity=2)
