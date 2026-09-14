#!/usr/bin/env python3
import importlib.util
import json
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import activity_planning as A
import tokenops_guard as G

TREASURY = json.loads((HERE / "treasury_policy.json").read_text())
POLICY = json.loads((HERE / "policy.json").read_text())


class ActivityPlanningTests(unittest.TestCase):
    def test_budget_is_exactly_35_percent(self):
        self.assertEqual(A.distribution_budget(1_000_000), 350_000)

    def test_epoch_cap_is_enforced(self):
        self.assertEqual(A.distribution_budget(1_000_000, 100_000), 100_000)

    def test_allocation_conservation(self):
        r = A.simulate_allocation(1_000_000, {"u1": 1, "u2": 2, "u3": 3}, 200_000, 350_000)
        self.assertTrue(r["conservation_pass"])
        self.assertEqual(r["allocated_raw"] + r["unallocated_raw"], r["budget_raw"])
        self.assertFalse(r["execution_authorized"])

    def test_per_user_cap_is_enforced(self):
        r = A.simulate_allocation(10_000_000, {"u1": 100, "u2": 1}, 100_000, 3_500_000)
        self.assertLessEqual(max(r["allocations_raw"].values()), 100_000)

    def test_empty_eligible_set_rejected(self):
        with self.assertRaises(ValueError):
            A.simulate_allocation(100, {}, 10, 35)

    def test_reward_intent_is_nonbroadcast_and_threshold_bound(self):
        r = A.build_intent_manifest("reward_epoch", 123, ["a" * 64], TREASURY)
        self.assertEqual(r["required_multisig_approvals"], 2)
        self.assertFalse(r["broadcast"])
        self.assertFalse(r["transaction_bytes_created"])

    def test_burn_intent_uses_three_approvals(self):
        r = A.build_intent_manifest("burn", 123, ["b" * 64], TREASURY)
        self.assertEqual(r["required_multisig_approvals"], 3)
        self.assertFalse(r["execution_authorized"])

    def test_invalid_evidence_hash_rejected(self):
        with self.assertRaises(ValueError):
            A.build_intent_manifest("burn", 1, ["not-a-hash"], TREASURY)

    def test_integration_contracts_are_non_custodial(self):
        r = A.integration_contracts(POLICY, TREASURY)
        self.assertFalse(r["private_key_input_allowed"])
        self.assertFalse(r["signature_input_allowed"])
        self.assertFalse(r["transaction_bytes_allowed"])
        self.assertFalse(r["broadcast_allowed"])
        self.assertIn("Vault", r["contracts"])
        self.assertIn("Forge", r["contracts"])
        self.assertIn("Core", r["contracts"])

    def test_parsed_mint_to_event_classifies(self):
        ix = {"program": "spl-token", "parsed": {"type": "mintTo", "info": {"mint": G.MINT, "amount": "100"}}}
        e = A._canonical_event(ix)
        self.assertEqual(e["type"], "mintTo")
        self.assertEqual(e["amount_raw"], "100")

    def test_unrelated_mint_event_ignored(self):
        ix = {"program": "spl-token", "parsed": {"type": "mintTo", "info": {"mint": "OtherMint", "amount": "100"}}}
        self.assertIsNone(A._canonical_event(ix))

    def test_set_authority_on_canonical_mint_classifies(self):
        ix = {"program": "spl-token", "parsed": {"type": "setAuthority", "info": {"account": G.MINT, "authorityType": "mintTokens", "newAuthority": None}}}
        e = A._canonical_event(ix)
        self.assertEqual(e["type"], "setAuthority")
        self.assertEqual(e["authority_type"], "mintTokens")


if __name__ == "__main__":
    unittest.main(verbosity=2)
