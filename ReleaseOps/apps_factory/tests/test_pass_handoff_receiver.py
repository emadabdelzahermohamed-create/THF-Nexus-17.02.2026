import importlib.util
import sqlite3
import sys
from dataclasses import replace
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("pass_handoff_receiver", ROOT / "pass_handoff_receiver.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["pass_handoff_receiver"] = mod
spec.loader.exec_module(mod)


class Verifier:
    def __init__(self, handoff):
        self.handoff = handoff
        self.calls = []

    def verify(self, raw_payload):
        self.calls.append(raw_payload)
        return self.handoff


def valid_handoff(**changes):
    base = mod.VerifiedHandoff(
        issuer=mod.TRUSTED_ISSUER,
        subject="user-1",
        source_package="com.topherofit.thf.core",
        target_package="com.topherofit.thf.pulse",
        nonce="nonce-1",
        state="state-1",
        issued_at=1000.0,
        expires_at=1060.0,
        scopes=("openid", "profile", "app:pulse"),
        return_route="thf://pulse/home",
        online_authority=True,
    )
    return replace(base, **changes)


class ReceiverTests(unittest.TestCase):
    def setup_receiver(self, handoff=None, now=1010.0):
        handoff = handoff or valid_handoff()
        verifier = Verifier(handoff)
        replay_db = sqlite3.connect(":memory:")
        session_db = sqlite3.connect(":memory:")
        replays = mod.HandoffReplayStore(replay_db)
        sessions = mod.FederatedSessionStore(session_db)
        receiver = mod.PassHandoffReceiver(
            verifier=verifier, replay_store=replays, session_store=sessions, clock=lambda: now
        )
        return receiver, verifier, replays, sessions

    def receive(self, receiver):
        return receiver.receive(
            raw_payload="signed-envelope",
            installed_package="com.topherofit.thf.pulse",
            expected_state="state-1",
        )

    def test_valid_verified_handoff_creates_package_bound_session(self):
        receiver, verifier, _, sessions = self.setup_receiver()
        session = self.receive(receiver)
        self.assertEqual(verifier.calls, ["signed-envelope"])
        self.assertEqual(session.subject, "user-1")
        self.assertEqual(session.package_id, "com.topherofit.thf.pulse")
        self.assertEqual(session.source_package, "com.topherofit.thf.core")
        self.assertEqual(set(session.scopes), {"openid", "profile", "app:pulse"})
        resolved = sessions.resolve(session.session_id)
        self.assertEqual(resolved.package_id, "com.topherofit.thf.pulse")
        self.assertEqual(receiver.authorize_session(
            session_id=session.session_id, subject="user-1", package_id="com.topherofit.thf.pulse"
        ).session_id, session.session_id)

    def test_nonce_is_single_use_even_with_identical_verified_payload(self):
        receiver, _, _, _ = self.setup_receiver()
        self.receive(receiver)
        with self.assertRaisesRegex(PermissionError, "replayed"):
            self.receive(receiver)

    def test_issuer_audience_state_and_route_are_fail_closed(self):
        cases = [
            (valid_handoff(issuer="https://evil.example"), "issuer"),
            (valid_handoff(target_package="com.topherofit.thf.forge"), "audience"),
            (valid_handoff(state="wrong"), "state"),
            (valid_handoff(return_route="thf://forge/home"), "return route"),
            (valid_handoff(return_route="https://pulse.topherofit.com/home"), "return route"),
        ]
        for handoff, message in cases:
            with self.subTest(message=message):
                receiver, _, _, _ = self.setup_receiver(handoff)
                with self.assertRaisesRegex(PermissionError, message):
                    self.receive(receiver)

    def test_expiry_future_issue_and_long_ttl_are_rejected(self):
        cases = [
            valid_handoff(expires_at=1009.0),
            valid_handoff(issued_at=1041.0, expires_at=1060.0),
            valid_handoff(issued_at=900.0, expires_at=1060.0),
        ]
        for handoff in cases:
            receiver, _, _, _ = self.setup_receiver(handoff)
            with self.assertRaises(PermissionError):
                self.receive(receiver)

    def test_unknown_packages_self_handoff_and_scope_escalation_are_rejected(self):
        cases = [
            valid_handoff(source_package="com.example.fake"),
            valid_handoff(source_package="com.topherofit.thf.pulse"),
            valid_handoff(scopes=("openid", "economy:write")),
            valid_handoff(scopes=("openid", "app:forge")),
            valid_handoff(scopes=()),
        ]
        for handoff in cases:
            receiver, _, _, _ = self.setup_receiver(handoff)
            with self.assertRaises(PermissionError):
                self.receive(receiver)

    def test_failed_semantic_validation_does_not_consume_nonce(self):
        bad = valid_handoff(state="wrong")
        receiver, verifier, _, _ = self.setup_receiver(bad)
        with self.assertRaises(PermissionError):
            self.receive(receiver)
        verifier.handoff = valid_handoff()
        session = self.receive(receiver)
        self.assertTrue(session.session_id)

    def test_federated_session_revocation_expiry_and_binding_are_enforced(self):
        receiver, _, _, sessions = self.setup_receiver()
        session = self.receive(receiver)
        with self.assertRaisesRegex(PermissionError, "binding"):
            receiver.authorize_session(
                session_id=session.session_id, subject="user-2", package_id="com.topherofit.thf.pulse"
            )
        sessions.revoke_session(session.session_id)
        with self.assertRaisesRegex(PermissionError, "revoked"):
            receiver.authorize_session(
                session_id=session.session_id, subject="user-1", package_id="com.topherofit.thf.pulse"
            )

    def test_raw_payload_and_expected_state_are_mandatory(self):
        receiver, _, _, _ = self.setup_receiver()
        with self.assertRaises(PermissionError):
            receiver.receive(raw_payload="", installed_package="com.topherofit.thf.pulse", expected_state="state-1")
        with self.assertRaises(PermissionError):
            receiver.receive(raw_payload="signed", installed_package="com.topherofit.thf.pulse", expected_state="")


if __name__ == "__main__":
    unittest.main()
