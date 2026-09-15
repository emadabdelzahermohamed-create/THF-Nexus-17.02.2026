import copy, unittest
from integration_contract import build_integration_contract, verify_integration_contract

H="a"*64
S="b"*40
M="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"

class IntegrationContractTests(unittest.TestCase):
    def valid(self):
        return build_integration_contract(source_commit_sha=S,mint=M,onchain_snapshot_sha256=H,policy_sha256=H,reward_epoch_commitment_sha256=H,signer_handoff_bundle_sha256=H,snapshot_slot=1,supply_base_units=1_000_000_000_000_000_000,decimals=8,mint_authority=None,freeze_authority=None)

    def test_ready_is_read_only_and_deterministic(self):
        a=self.valid(); b=self.valid()
        self.assertEqual(a["status"],"READ_ONLY_CONTRACT_READY")
        self.assertEqual(a["contract_sha256"],b["contract_sha256"])
        self.assertFalse(a["sign"]); self.assertFalse(a["broadcast"]); self.assertFalse(a["financial_execution"])
        self.assertEqual(verify_integration_contract(a)["status"],"VERIFIED_READ_ONLY")

    def test_invalid_evidence_blocks(self):
        a=build_integration_contract(source_commit_sha=S,mint=M,onchain_snapshot_sha256="bad",policy_sha256=H,reward_epoch_commitment_sha256=H,signer_handoff_bundle_sha256=H,snapshot_slot=1,supply_base_units=1,decimals=8,mint_authority=None,freeze_authority=None)
        self.assertEqual(a["status"],"BLOCKED")

    def test_mutation_to_execution_is_detected(self):
        a=self.valid(); a["sign"]=True
        v=verify_integration_contract(a)
        self.assertFalse(v["ok"]); self.assertIn("sign_must_be_false",v["reasons"])

    def test_consumer_scope_cannot_expand_silently(self):
        a=self.valid(); a["consumers"].append("AndroidDirect")
        self.assertEqual(verify_integration_contract(a)["status"],"BLOCKED")

    def test_forbidden_financial_capability_cannot_be_removed(self):
        a=self.valid(); a["forbidden_capabilities"].remove("burn")
        self.assertIn("forbidden_capability_gap",verify_integration_contract(a)["reasons"])

if __name__ == "__main__": unittest.main()
