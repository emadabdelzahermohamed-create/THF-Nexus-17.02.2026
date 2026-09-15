import unittest
from financial_action_approval import classify, evaluate, RULES

class FinancialApprovalTests(unittest.TestCase):
    def test_every_financial_action_is_never_autonomous(self):
        for action, rule in RULES.items():
            if rule.financial_effect:
                self.assertFalse(classify(action)["allowed_autonomously"], action)

    def test_unknown_action_fails_closed(self):
        r = evaluate("magic_money")
        self.assertFalse(r["allowed_autonomously"])
        self.assertEqual(r["status"], "BLOCKED_UNKNOWN_ACTION")

    def test_burn_requires_governance_multisig_and_simulation(self):
        r = evaluate("burn", {})
        self.assertIn("governance_decision_evidence_sha256", r["missing"])
        self.assertIn("user_controlled_multisig_approval", r["missing"])
        self.assertIn("simulation_evidence_sha256", r["missing"])

    def test_complete_evidence_only_reaches_external_signer_review(self):
        evidence = {
            "source_commit_sha": "a" * 40,
            "policy_sha256": "b" * 64,
            "transaction_manifest_sha256": "c" * 64,
            "simulation_evidence_sha256": "d" * 64,
            "governance_decision_evidence_sha256": "e" * 64,
            "user_controlled_multisig_approval": "approved-outside-automation",
        }
        r = evaluate("burn", evidence)
        self.assertEqual(r["status"], "READY_FOR_EXTERNAL_SIGNER_REVIEW")
        self.assertFalse(r["allowed_autonomously"])
        self.assertFalse(r["broadcast"])
        self.assertFalse(r["private_key_used"])

    def test_read_and_simulation_are_safe_nonfinancial(self):
        self.assertTrue(evaluate("read_chain_state")["allowed_autonomously"])
        self.assertTrue(evaluate("simulate_transaction")["allowed_autonomously"])

if __name__ == "__main__":
    unittest.main()
