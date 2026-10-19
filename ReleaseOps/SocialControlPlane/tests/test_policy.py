import unittest
from ReleaseOps.SocialControlPlane.models import PostIntent
from ReleaseOps.SocialControlPlane.policy import evaluate

class PolicyTests(unittest.TestCase):
    def test_blocks_guaranteed_profit(self):
        d = evaluate(PostIntent("threads", "Guaranteed profit with THF"))
        self.assertFalse(d.allowed)
    def test_requires_evidence_for_supply_claim(self):
        d = evaluate(PostIntent("facebook", "Token supply update"))
        self.assertFalse(d.allowed)
        self.assertIn("token_claim_requires_source_evidence", d.reasons)
    def test_allows_factual_community_question(self):
        d = evaluate(PostIntent("threads", "What sport should the next community challenge focus on?"))
        self.assertTrue(d.allowed)
