import unittest
from signer_handoff_bundle import build

H="a"*64
MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"

def receipt():
    return {"status":"SIMULATION_EVIDENCE_READY_FOR_EXTERNAL_SIGNER_REVIEW","sign":False,"broadcast":False,
            "financial_execution":False,"mint":MINT,"epoch_id":"e1","reward_epoch_commitment_sha256":H,
            "simulation_receipt_sha256":H,"message_sha256":H}

class TestSignerHandoff(unittest.TestCase):
    def test_transfer_ready_but_never_executes(self):
        r=build(operation="transfer",simulation_receipt=receipt(),expected_mint=MINT,policy_sha256=H,
                transaction_manifest_sha256=H,multisig_policy_sha256=H)
        self.assertEqual(r["status"],"READY_FOR_USER_CONTROLLED_MULTISIG_REVIEW")
        self.assertFalse(r["sign"]); self.assertFalse(r["broadcast"]); self.assertFalse(r["financial_execution"])
    def test_burn_requires_governance(self):
        r=build(operation="burn",simulation_receipt=receipt(),expected_mint=MINT,policy_sha256=H,
                transaction_manifest_sha256=H,multisig_policy_sha256=H)
        self.assertEqual(r["status"],"BLOCKED"); self.assertIn("GOVERNANCE_EVIDENCE_REQUIRED",r["blockers"])
    def test_burn_with_governance_still_not_executable(self):
        r=build(operation="burn",simulation_receipt=receipt(),expected_mint=MINT,policy_sha256=H,
                transaction_manifest_sha256=H,governance_evidence_sha256=H,multisig_policy_sha256=H)
        self.assertEqual(r["status"],"READY_FOR_USER_CONTROLLED_MULTISIG_REVIEW")
        self.assertFalse(r["financial_execution"])
    def test_unsafe_receipt_blocks(self):
        x=receipt(); x["broadcast"]=True
        r=build(operation="transfer",simulation_receipt=x,expected_mint=MINT,policy_sha256=H,
                transaction_manifest_sha256=H,multisig_policy_sha256=H)
        self.assertEqual(r["status"],"BLOCKED"); self.assertIn("UNSAFE_SIMULATION_FLAGS",r["blockers"])
    def test_deterministic(self):
        kw=dict(operation="transfer",simulation_receipt=receipt(),expected_mint=MINT,policy_sha256=H,
                transaction_manifest_sha256=H,multisig_policy_sha256=H)
        self.assertEqual(build(**kw)["signer_handoff_sha256"],build(**kw)["signer_handoff_sha256"])

if __name__=="__main__": unittest.main()
