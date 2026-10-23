import sqlite3
import unittest

from reward_connector import RewardClaimError, RewardClaimReplayGuard, RewardClaimSigner, assert_reward_eligible


class RewardConnectorTests(unittest.TestCase):
    def setUp(self):
        self.signer = RewardClaimSigner(b"k" * 32)
        self.args = dict(
            partner_id="ruinsciv", campaign_id="walk-5k", fitness_user_id="fit-1",
            external_user_id="ruins-9", reward_id="skin-forest", quantity=1,
            evidence_score=92, session_hash="sha256:abc", nonce="nonce-1",
            ttl_seconds=300, now=1000,
        )

    def test_signed_claim_is_partner_bound_and_minimal(self):
        envelope = self.signer.issue(**self.args)
        claim = self.signer.verify(envelope, expected_partner="ruinsciv", now=1100)
        self.assertEqual("ruins-9", claim.external_user_id)
        serialized = str(envelope).lower()
        self.assertNotIn("camera", serialized)
        self.assertNotIn("health_connect_record", serialized)

    def test_wrong_partner_and_expiry_fail_closed(self):
        envelope = self.signer.issue(**self.args)
        with self.assertRaises(RewardClaimError):
            self.signer.verify(envelope, expected_partner="endciv", now=1100)
        with self.assertRaises(RewardClaimError):
            self.signer.verify(envelope, expected_partner="ruinsciv", now=1301)

    def test_tamper_fails_signature(self):
        envelope = self.signer.issue(**self.args)
        envelope["claim"]["quantity"] = 99
        with self.assertRaises(RewardClaimError):
            self.signer.verify(envelope, expected_partner="ruinsciv", now=1100)

    def test_verified_claim_can_be_consumed_only_once(self):
        envelope = self.signer.issue(**self.args)
        claim = self.signer.verify(envelope, expected_partner="ruinsciv", now=1100)
        guard = RewardClaimReplayGuard(sqlite3.connect(":memory:"))
        self.addCleanup(guard.db.close)
        guard.consume(claim, now=1100)
        with self.assertRaises(RewardClaimError):
            guard.consume(claim, now=1101)

    def test_nonce_reuse_is_rejected_even_if_claim_id_changes(self):
        first = self.signer.verify(self.signer.issue(**self.args), expected_partner="ruinsciv", now=1100)
        changed = dict(self.args, reward_id="skin-desert")
        second = self.signer.verify(self.signer.issue(**changed), expected_partner="ruinsciv", now=1100)
        guard = RewardClaimReplayGuard(sqlite3.connect(":memory:"))
        self.addCleanup(guard.db.close)
        guard.consume(first, now=1100)
        with self.assertRaises(RewardClaimError):
            guard.consume(second, now=1101)

    def test_stale_or_future_claim_cannot_be_consumed(self):
        claim = self.signer.verify(self.signer.issue(**self.args), expected_partner="ruinsciv", now=1100)
        guard = RewardClaimReplayGuard(sqlite3.connect(":memory:"))
        self.addCleanup(guard.db.close)
        with self.assertRaises(RewardClaimError):
            guard.consume(claim, now=1301)
        with self.assertRaises(RewardClaimError):
            guard.consume(claim, now=999)

    def test_manual_unverified_revoked_never_eligible(self):
        assert_reward_eligible(verified=True, manual=False, revoked=False,
                               evidence_score=90, minimum_score=80)
        for kwargs in (
            dict(verified=False, manual=False, revoked=False, evidence_score=90),
            dict(verified=True, manual=True, revoked=False, evidence_score=90),
            dict(verified=True, manual=False, revoked=True, evidence_score=90),
            dict(verified=True, manual=False, revoked=False, evidence_score=79),
        ):
            with self.assertRaises(RewardClaimError):
                assert_reward_eligible(minimum_score=80, **kwargs)


if __name__ == "__main__":
    unittest.main()
