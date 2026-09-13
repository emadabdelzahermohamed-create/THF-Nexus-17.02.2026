import copy
import unittest

from anti_whale_reward_policy_completion_gate import canonical_sha256 as policy_sha256, evaluate_policy_completion
from policy_completion_bound_unsigned_admission import evaluate_policy_completion_bound_admission
from unsigned_simulation_admission_gate import canonical_sha256 as admission_sha256

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK = "solana-mainnet-beta"
POLICY_BLOB = "a" * 40
TREASURY_BLOB = "b" * 40


def authoritative_policy(configured=True):
    return {
        "network": NETWORK,
        "mint": MINT,
        "economics": {"active_user_revenue_share": 0.35, "approved_supply_floor_target_ui": "8000000000"},
        "distribution_controls": {
            "anti_whale_cap_required": True,
            "activity_evidence_required": True,
            "anti_sybil_required": True,
            "per_user_cap": "100" if configured else None,
            "epoch_budget_cap": "1000" if configured else None,
        },
    }


def treasury_policy():
    return {
        "network": NETWORK,
        "mint": MINT,
        "hard_guards": {
            "wave_mawja_untouched": True,
            "private_key_forbidden": True,
            "seed_phrase_forbidden": True,
        },
    }


def completion(policy, treasury, configured=True):
    return {
        "network": NETWORK,
        "mint": MINT,
        "source_head_prior_verified": "c" * 40,
        "authoritative_policy_blob_sha": POLICY_BLOB,
        "authoritative_policy_sha256": policy_sha256(policy),
        "treasury_policy_blob_sha": TREASURY_BLOB,
        "treasury_policy_sha256": policy_sha256(treasury),
        "status": "authoritatively_completed" if configured else "incomplete",
        "active_user_revenue_share": 0.35,
        "anti_whale": {
            "per_user_cap_ui": "100" if configured else None,
            "epoch_budget_cap_ui": "1000" if configured else None,
        },
        "reward_epoch": {"epoch_budget_cap_ui": "1000" if configured else None},
        "governance_provenance": {
            "status": "approved" if configured else "pending",
            "decision_id": "fixture-decision" if configured else None,
            "approval_record_sha256": "d" * 64 if configured else None,
            "governance_policy_sha256": "e" * 64 if configured else None,
            "approved_at": "2026-09-13T00:00:00Z" if configured else None,
        },
        "production_caps_configured": configured,
        "safety": {
            "simulation_review_eligible": False,
            "execution_authorized": False,
            "transaction_signing": False,
            "transaction_broadcast": False,
            "private_key_material_allowed": False,
            "wave_mawja_untouched": True,
        },
    }


def snapshot(configured=True):
    return {
        "network": NETWORK,
        "mint": MINT,
        "authoritative_policy_blob_sha": POLICY_BLOB,
        "treasury_policy_blob_sha": TREASURY_BLOB,
        "economics": {"active_user_revenue_share": 0.35, "approved_supply_floor_target_ui": "8000000000"},
        "distribution_controls": {
            "anti_whale_cap_required": True,
            "per_user_cap": "100" if configured else None,
            "epoch_budget_cap": "1000" if configured else None,
            "production_caps_configured": configured,
        },
        "safety": {
            "production_signer_policy_approved": False,
            "simulation_execution_permitted": False,
            "execution_authorized": False,
            "transaction_signing": False,
            "transaction_broadcast": False,
            "wave_mawja_untouched": True,
        },
    }


def provenance():
    return {"gate": "THF_TOKENOPS_UNIFIED_REVIEW_PROVENANCE_V1", "manifest_sha256": "1" * 64, "source_head": "2" * 40, "review_only": True}


def plan(snapshot_value, provenance_value, completion_result):
    return {
        "network": NETWORK,
        "mint": MINT,
        "intent": "reward_epoch",
        "unsigned": True,
        "active_user_revenue_share": 0.35,
        "unified_review_provenance_sha256": admission_sha256(provenance_value),
        "policy_snapshot_sha256": admission_sha256(snapshot_value),
        "policy_completion_evidence_sha256": completion_result["completion_sha256"],
        "sign": False,
        "submit": False,
        "broadcast": False,
        "financial_effect": False,
    }


class PolicyCompletionBoundAdmissionTests(unittest.TestCase):
    def test_completed_fixture_can_reach_review_only(self):
        p, t, s, prov = authoritative_policy(True), treasury_policy(), snapshot(True), provenance()
        c = completion(p, t, True)
        pc = evaluate_policy_completion(c, p, t)
        out = evaluate_policy_completion_bound_admission(c, p, t, prov, plan(s, prov, pc), s)
        self.assertTrue(out["simulation_review_eligible"])
        self.assertFalse(out["execution_authorized"])
        self.assertFalse(out["financial_effect"])

    def test_incomplete_policy_fails_closed(self):
        p, t, s, prov = authoritative_policy(False), treasury_policy(), snapshot(False), provenance()
        c = completion(p, t, False)
        pc = evaluate_policy_completion(c, p, t)
        out = evaluate_policy_completion_bound_admission(c, p, t, prov, plan(s, prov, pc), s)
        self.assertFalse(out["simulation_review_eligible"])
        self.assertIn("policy_completion_not_authoritatively_completed", out["blockers"])

    def test_completion_digest_tampering_rejected(self):
        p, t, s, prov = authoritative_policy(True), treasury_policy(), snapshot(True), provenance()
        c = completion(p, t, True)
        pc = evaluate_policy_completion(c, p, t)
        candidate = plan(s, prov, pc)
        candidate["policy_completion_evidence_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            evaluate_policy_completion_bound_admission(c, p, t, prov, candidate, s)

    def test_policy_blob_replay_mismatch_rejected(self):
        p, t, s, prov = authoritative_policy(True), treasury_policy(), snapshot(True), provenance()
        c = completion(p, t, True)
        pc = evaluate_policy_completion(c, p, t)
        candidate = plan(s, prov, pc)
        s["authoritative_policy_blob_sha"] = "9" * 40
        candidate["policy_snapshot_sha256"] = admission_sha256(s)
        with self.assertRaises(ValueError):
            evaluate_policy_completion_bound_admission(c, p, t, prov, candidate, s)

    def test_governance_downgrade_stays_fail_closed(self):
        p, t, s, prov = authoritative_policy(True), treasury_policy(), snapshot(True), provenance()
        c = completion(p, t, True)
        c["status"] = "incomplete"
        c["governance_provenance"] = {"status": "pending", "decision_id": None, "approval_record_sha256": None, "governance_policy_sha256": None, "approved_at": None}
        c["production_caps_configured"] = False
        pc = evaluate_policy_completion(c, p, t)
        out = evaluate_policy_completion_bound_admission(c, p, t, prov, plan(s, prov, pc), s)
        self.assertFalse(out["simulation_review_eligible"])
        self.assertTrue(any("governance_provenance_incomplete" in x for x in out["blockers"]))

    def test_execution_request_rejected(self):
        p, t, s, prov = authoritative_policy(True), treasury_policy(), snapshot(True), provenance()
        c = completion(p, t, True)
        pc = evaluate_policy_completion(c, p, t)
        candidate = plan(s, prov, pc)
        candidate["broadcast"] = True
        with self.assertRaises(ValueError):
            evaluate_policy_completion_bound_admission(c, p, t, prov, candidate, s)

    def test_sensitive_field_rejected(self):
        p, t, s, prov = authoritative_policy(True), treasury_policy(), snapshot(True), provenance()
        c = completion(p, t, True)
        pc = evaluate_policy_completion(c, p, t)
        candidate = plan(s, prov, pc)
        candidate["private_key"] = "forbidden"
        with self.assertRaises(ValueError):
            evaluate_policy_completion_bound_admission(c, p, t, prov, candidate, s)


if __name__ == "__main__":
    unittest.main()
