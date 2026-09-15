#!/usr/bin/env python3
import unittest
from governance_execution_envelope import build_envelope, validate_for_automation

class GateTests(unittest.TestCase):
    def base(self, **kw):
        x=dict(action="burn",source_commit_sha="a"*40,policy_sha256="b"*64,
               transaction_manifest_sha256="c"*64,simulation_sha256="d"*64,
               governance_evidence_sha256="e"*64,treasury_pubkey="TreasuryPublicKey",
               expected_mint="MintPublicKey",expected_supply_atomic=10_000_000_000*100_000_000,
               observed_mint="MintPublicKey",observed_supply_atomic=10_000_000_000*100_000_000)
        x.update(kw); return build_envelope(**x)
    def test_complete_evidence_is_review_only(self):
        e=self.base(); self.assertEqual(e["status"],"READY_FOR_EXTERNAL_SIGNER_REVIEW")
        self.assertFalse(e["sign"]); self.assertFalse(e["broadcast"]); self.assertFalse(e["financial_execution"])
        self.assertTrue(validate_for_automation(e))
    def test_missing_simulation_blocks(self):
        e=self.base(simulation_sha256=None); self.assertEqual(e["status"],"BLOCKED")
        self.assertIn("MISSING_SIMULATION_SHA256",e["blockers"])
    def test_onchain_drift_blocks(self):
        e=self.base(observed_supply_atomic=1); self.assertEqual(e["status"],"BLOCKED")
        self.assertIn("ONCHAIN_SUPPLY_MISMATCH",e["blockers"])
    def test_no_execution_mutation_allowed(self):
        e=self.base(); e["broadcast"]=True; self.assertFalse(validate_for_automation(e))
    def test_all_irreversible_actions_remain_review_only(self):
        for action in ("transfer","burn","authority_change","treasury_migration","vesting_settlement","dao_execution","lock_reward_settlement"):
            e=self.base(action=action); self.assertEqual(e["status"],"READY_FOR_EXTERNAL_SIGNER_REVIEW"); self.assertFalse(e["sign"])

if __name__ == "__main__": unittest.main()
