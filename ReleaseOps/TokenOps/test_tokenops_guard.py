#!/usr/bin/env python3
import copy
import importlib.util
import json
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("tokenops_guard", HERE / "tokenops_guard.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

POLICY = json.loads((HERE / "policy.json").read_text())
TREASURY = json.loads((HERE / "treasury_policy.json").read_text())
AUDIT = {
    "schema": M.SCHEMA,
    "network": M.NETWORK,
    "mint": M.MINT,
    "slot": 1,
    "program_id": M.TOKEN_PROGRAM,
    "decimals": 8,
    "supply_raw": str(10_000_000_000 * 10**8),
    "supply_ui": "10000000000",
    "mint_authority": None,
    "freeze_authority": None,
    "recent_address_activity": {"status": "ok", "count": 0, "entries": []},
    "holder_concentration": {"status": "unavailable", "reason": "rate limited"},
    "execution": {
        "read_only": True,
        "transaction_created": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "broadcast": False,
        "financial_effect": False,
        "private_key_used": False,
        "wave_touched": False,
    },
}
AUDIT["audit_sha256"] = M.sha256(AUDIT)


class TokenOpsGuardTests(unittest.TestCase):
    def test_canonical_gate_passes(self):
        self.assertEqual(M.invariant_gate(AUDIT)["status"], "PASS")

    def test_program_drift_fails_closed(self):
        a = copy.deepcopy(AUDIT)
        a["program_id"] = "bad"
        self.assertIn("program_id", M.invariant_gate(a)["failed"])

    def test_mint_authority_reappearing_fails_closed(self):
        a = copy.deepcopy(AUDIT)
        a["mint_authority"] = "unexpected"
        self.assertIn("mint_authority_disabled", M.invariant_gate(a)["failed"])

    def test_freeze_authority_reappearing_fails_closed(self):
        a = copy.deepcopy(AUDIT)
        a["freeze_authority"] = "unexpected"
        self.assertIn("freeze_authority_disabled", M.invariant_gate(a)["failed"])

    def test_supply_below_8b_fails_closed(self):
        a = copy.deepcopy(AUDIT)
        a["supply_raw"] = str(7_999_999_999 * 10**8)
        self.assertIn("supply_floor", M.invariant_gate(a)["failed"])

    def test_supply_above_10b_fails_closed(self):
        a = copy.deepcopy(AUDIT)
        a["supply_raw"] = str(10_000_000_001 * 10**8)
        self.assertIn("supply_ceiling", M.invariant_gate(a)["failed"])

    def test_holder_rpc_unavailable_does_not_fail_core_gate(self):
        self.assertEqual(AUDIT["holder_concentration"]["status"], "unavailable")
        self.assertEqual(M.invariant_gate(AUDIT)["status"], "PASS")

    def test_current_policy_is_fail_closed(self):
        r = M.readiness(POLICY, TREASURY, AUDIT)
        self.assertEqual(r["status"], "FAIL_CLOSED")
        self.assertIn("per_user_cap_not_approved", r["blockers"])
        self.assertIn("treasury_accounts_and_evidence_missing", r["blockers"])
        self.assertFalse(r["execution"]["financial_effect"])
        self.assertFalse(r["execution"]["broadcast"])

    def test_burn_headroom_is_exactly_2b_from_10b(self):
        r = M.readiness(POLICY, TREASURY, AUDIT)
        self.assertEqual(int(r["burn"]["theoretical_headroom_raw"]), 2_000_000_000 * 10**8)
        self.assertIsNone(r["burn"]["review_cap_raw"])
        self.assertFalse(r["burn"]["execution_authorized"])

    def test_35_percent_is_policy_constant(self):
        r = M.readiness(POLICY, TREASURY, AUDIT)
        self.assertEqual(r["distribution"]["approved_revenue_share_bps"], 3500)
        self.assertIsNone(r["distribution"]["actionable_budget_raw"])

    def test_sensitive_field_is_rejected(self):
        p = copy.deepcopy(POLICY)
        p["private_key"] = "never"
        with self.assertRaises(ValueError):
            M.readiness(p, TREASURY, AUDIT)

    def test_multisig_thresholds_are_policy_bound(self):
        self.assertEqual(TREASURY["approval_classes"]["reward_epoch"]["minimum_approvals"], 2)
        self.assertEqual(TREASURY["approval_classes"]["vesting_settlement"]["minimum_approvals"], 2)
        self.assertEqual(TREASURY["approval_classes"]["burn"]["minimum_approvals"], 3)
        self.assertEqual(TREASURY["approval_classes"]["treasury_transfer"]["minimum_approvals"], 3)

    def test_no_execution_paths_exist_in_policy(self):
        ep = POLICY["execution_policy"]
        self.assertTrue(all(v is False for v in ep.values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
