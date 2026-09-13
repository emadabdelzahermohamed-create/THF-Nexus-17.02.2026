import copy
import json
import unittest

from unsigned_simulation_admission_gate import canonical_sha256, evaluate_unsigned_simulation_admission

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK = "solana-mainnet-beta"


def fixture_snapshot(configured=True):
    return {
        "version": 1,
        "network": NETWORK,
        "mint": MINT,
        "economics": {
            "active_user_revenue_share": 0.35,
            "approved_supply_floor_target_ui": "8000000000",
            "burn_source_policy": "treasury_controlled_balances_only",
        },
        "distribution_controls": {
            "anti_sybil_required": True,
            "activity_evidence_required": True,
            "anti_whale_cap_required": True,
            "per_user_cap": "fixture-only-cap" if configured else None,
            "epoch_budget_cap": "fixture-only-budget" if configured else None,
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


def fixture_provenance():
    return {
        "gate": "THF_TOKENOPS_UNIFIED_REVIEW_PROVENANCE_V1",
        "manifest_sha256": "1" * 64,
        "source_head": "2" * 40,
        "review_only": True,
    }


def fixture_plan(snapshot, provenance, intent="reward_epoch"):
    plan = {
        "network": NETWORK,
        "mint": MINT,
        "intent": intent,
        "unsigned": True,
        "unified_review_provenance_sha256": canonical_sha256(provenance),
        "policy_snapshot_sha256": canonical_sha256(snapshot),
        "sign": False,
        "submit": False,
        "broadcast": False,
        "financial_effect": False,
    }
    if intent == "reward_epoch":
        plan["active_user_revenue_share"] = 0.35
    if intent == "burn_plan":
        plan.update({
            "current_supply_ui": "10000000000",
            "planned_burn_ui": "1000000000",
            "burn_source_policy": "treasury_controlled_balances_only",
        })
    return plan


class UnsignedSimulationAdmissionTests(unittest.TestCase):
    def test_configured_fixture_can_reach_review_eligibility_only(self):
        snapshot = fixture_snapshot(True)
        provenance = fixture_provenance()
        result = evaluate_unsigned_simulation_admission(provenance, fixture_plan(snapshot, provenance), snapshot)
        self.assertTrue(result["simulation_review_eligible"])
        self.assertFalse(result["simulation_execution_permitted"])
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["financial_effect"])

    def test_production_style_missing_caps_fails_closed_without_inventing_values(self):
        snapshot = fixture_snapshot(False)
        provenance = fixture_provenance()
        result = evaluate_unsigned_simulation_admission(provenance, fixture_plan(snapshot, provenance), snapshot)
        self.assertFalse(result["simulation_review_eligible"])
        self.assertIn("anti_whale_caps_not_authoritatively_configured", result["blockers"])

    def test_wrong_35_percent_binding_rejected(self):
        snapshot = fixture_snapshot(True)
        provenance = fixture_provenance()
        plan = fixture_plan(snapshot, provenance)
        plan["active_user_revenue_share"] = 0.34
        with self.assertRaises(ValueError):
            evaluate_unsigned_simulation_admission(provenance, plan, snapshot)

    def test_burn_below_8b_floor_rejected(self):
        snapshot = fixture_snapshot(True)
        provenance = fixture_provenance()
        plan = fixture_plan(snapshot, provenance, "burn_plan")
        plan["planned_burn_ui"] = "2000000001"
        with self.assertRaises(ValueError):
            evaluate_unsigned_simulation_admission(provenance, plan, snapshot)

    def test_provenance_tampering_rejected(self):
        snapshot = fixture_snapshot(True)
        provenance = fixture_provenance()
        plan = fixture_plan(snapshot, provenance)
        tampered = copy.deepcopy(provenance)
        tampered["source_head"] = "3" * 40
        with self.assertRaises(ValueError):
            evaluate_unsigned_simulation_admission(tampered, plan, snapshot)

    def test_snapshot_tampering_rejected(self):
        snapshot = fixture_snapshot(True)
        provenance = fixture_provenance()
        plan = fixture_plan(snapshot, provenance)
        snapshot["economics"]["active_user_revenue_share"] = 0.36
        with self.assertRaises(ValueError):
            evaluate_unsigned_simulation_admission(provenance, plan, snapshot)

    def test_sign_or_broadcast_request_rejected(self):
        snapshot = fixture_snapshot(True)
        provenance = fixture_provenance()
        for field in ("sign", "submit", "broadcast", "financial_effect"):
            plan = fixture_plan(snapshot, provenance)
            plan[field] = True
            with self.assertRaises(ValueError):
                evaluate_unsigned_simulation_admission(provenance, plan, snapshot)

    def test_sensitive_or_signature_field_rejected(self):
        snapshot = fixture_snapshot(True)
        provenance = fixture_provenance()
        plan = fixture_plan(snapshot, provenance)
        plan["signature"] = "forbidden"
        with self.assertRaises(ValueError):
            evaluate_unsigned_simulation_admission(provenance, plan, snapshot)


if __name__ == "__main__":
    unittest.main()
