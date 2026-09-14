import importlib.util
import sqlite3
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("pass_handoff_receiver_private_rbac", ROOT / "pass_handoff_receiver.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["pass_handoff_receiver_private_rbac"] = mod
spec.loader.exec_module(mod)


class Verifier:
    def __init__(self, handoff):
        self.handoff = handoff

    def verify(self, raw_payload):
        if raw_payload != "signed-envelope":
            raise PermissionError("unexpected payload")
        return self.handoff


def handoff(target, roles=(), online=True, nonce="n1"):
    slug = mod.PACKAGE_SLUGS[target]
    return mod.VerifiedHandoff(
        issuer=mod.TRUSTED_ISSUER,
        subject="staff-1",
        source_package="com.topherofit.thf.core",
        target_package=target,
        nonce=nonce,
        state="state-1",
        issued_at=1000.0,
        expires_at=1060.0,
        scopes=("openid", "profile", f"app:{slug}"),
        return_route=f"thf://{slug}/home",
        online_authority=online,
        roles=tuple(roles),
    )


def receiver_for(item):
    replay_db = sqlite3.connect(":memory:")
    session_db = sqlite3.connect(":memory:")
    sessions = mod.FederatedSessionStore(session_db)
    return mod.PassHandoffReceiver(
        verifier=Verifier(item),
        replay_store=mod.HandoffReplayStore(replay_db),
        session_store=sessions,
        clock=lambda: 1010.0,
    ), sessions


def receive(receiver, target):
    return receiver.receive(
        raw_payload="signed-envelope",
        installed_package=target,
        expected_state="state-1",
    )


class PrivateAppRbacTests(unittest.TestCase):
    SIGNAL = "com.topherofit.thf.signal"
    COMMAND = "com.topherofit.thf.command"

    def test_signal_rejects_ordinary_user_but_accepts_publisher(self):
        receiver, _ = receiver_for(handoff(self.SIGNAL, roles=("user",)))
        with self.assertRaisesRegex(PermissionError, "role denied"):
            receive(receiver, self.SIGNAL)

        receiver, _ = receiver_for(handoff(self.SIGNAL, roles=("publisher",), nonce="n2"))
        session = receive(receiver, self.SIGNAL)
        self.assertEqual(session.roles, ("publisher",))
        self.assertEqual(
            receiver.authorize_session(
                session_id=session.session_id,
                subject="staff-1",
                package_id=self.SIGNAL,
                required_role="publisher",
            ).session_id,
            session.session_id,
        )

    def test_signal_accepts_admin_as_publisher_superrole(self):
        receiver, _ = receiver_for(handoff(self.SIGNAL, roles=("admin",)))
        session = receive(receiver, self.SIGNAL)
        receiver.authorize_session(
            session_id=session.session_id,
            subject="staff-1",
            package_id=self.SIGNAL,
            required_role="publisher",
        )

    def test_command_requires_explicit_admin(self):
        for roles in ((), ("user",), ("publisher",)):
            with self.subTest(roles=roles):
                receiver, _ = receiver_for(handoff(self.COMMAND, roles=roles))
                with self.assertRaisesRegex(PermissionError, "role denied"):
                    receive(receiver, self.COMMAND)

        receiver, _ = receiver_for(handoff(self.COMMAND, roles=("admin",)))
        session = receive(receiver, self.COMMAND)
        receiver.authorize_session(
            session_id=session.session_id,
            subject="staff-1",
            package_id=self.COMMAND,
            required_role="admin",
        )

    def test_private_apps_require_online_authority(self):
        for target, roles in ((self.SIGNAL, ("publisher",)), (self.COMMAND, ("admin",))):
            receiver, _ = receiver_for(handoff(target, roles=roles, online=False))
            with self.assertRaisesRegex(PermissionError, "online RBAC authority"):
                receive(receiver, target)

    def test_unknown_role_claim_fails_closed(self):
        receiver, _ = receiver_for(handoff(self.SIGNAL, roles=("publisher", "root")))
        with self.assertRaisesRegex(PermissionError, "unknown role"):
            receive(receiver, self.SIGNAL)

    def test_v1_database_migrates_without_granting_private_roles(self):
        db = sqlite3.connect(":memory:")
        db.execute(
            "CREATE TABLE federated_sessions ("
            "session_id TEXT PRIMARY KEY, subject TEXT NOT NULL, package_id TEXT NOT NULL, "
            "source_package TEXT NOT NULL, scopes TEXT NOT NULL, created_at REAL NOT NULL, "
            "expires_at REAL NOT NULL, revoked INTEGER NOT NULL DEFAULT 0)"
        )
        db.execute(
            "INSERT INTO federated_sessions VALUES(?,?,?,?,?,?,?,0)",
            ("legacy", "staff-1", self.COMMAND, "com.topherofit.thf.core", "openid app:command", 900.0, 2000.0),
        )
        db.commit()
        sessions = mod.FederatedSessionStore(db)
        legacy = sessions.resolve("legacy")
        self.assertEqual(legacy.roles, ())
        receiver = mod.PassHandoffReceiver(
            verifier=Verifier(handoff(self.COMMAND, roles=("admin",))),
            replay_store=mod.HandoffReplayStore(sqlite3.connect(":memory:")),
            session_store=sessions,
            clock=lambda: 1010.0,
        )
        with self.assertRaisesRegex(PermissionError, "session role denied"):
            receiver.authorize_session(
                session_id="legacy", subject="staff-1", package_id=self.COMMAND
            )

    def test_required_role_cannot_be_invented_by_call_site(self):
        receiver, _ = receiver_for(handoff(self.SIGNAL, roles=("publisher",)))
        session = receive(receiver, self.SIGNAL)
        with self.assertRaisesRegex(PermissionError, "unknown required"):
            receiver.authorize_session(
                session_id=session.session_id,
                subject="staff-1",
                package_id=self.SIGNAL,
                required_role="superuser",
            )


if __name__ == "__main__":
    unittest.main()
