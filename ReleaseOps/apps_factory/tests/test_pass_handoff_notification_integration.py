import importlib.util
import sqlite3
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]
for name in (
    "notification_lifecycle", "notification_http_contract", "notification_provider_contract",
    "notification_dispatch", "pass_notification_bridge", "pass_handoff_receiver",
):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

life = sys.modules["notification_lifecycle"]
http = sys.modules["notification_http_contract"]
provider = sys.modules["notification_provider_contract"]
dispatch = sys.modules["notification_dispatch"]
bridge_mod = sys.modules["pass_notification_bridge"]
handoff_mod = sys.modules["pass_handoff_receiver"]


class Vault:
    def __init__(self): self.data = {}
    def put(self, key, value): self.data[key] = value
    def get(self, key): return self.data.get(key)
    def delete(self, key): self.data.pop(key, None)


class Adapter:
    provider_name = "test"
    def __init__(self): self.calls = []
    def validate_configuration(self): return True
    def send(self, *, provider_token, request):
        self.calls.append((provider_token, request.token_id))
        return provider.DeliveryResult(True, "msg-1")


class Verifier:
    def verify(self, raw_payload):
        assert raw_payload == "cryptographically-verified-upstream-envelope"
        return handoff_mod.VerifiedHandoff(
            issuer=handoff_mod.TRUSTED_ISSUER,
            subject="user-1",
            source_package="com.topherofit.thf.core",
            target_package="com.topherofit.thf.pulse",
            nonce="integration-nonce-1",
            state="integration-state-1",
            issued_at=1000.0,
            expires_at=1060.0,
            scopes=("openid", "profile", "notifications", "app:pulse"),
            return_route="thf://pulse/home",
            online_authority=True,
        )


class IntegrationTests(unittest.TestCase):
    def test_handoff_session_drives_notification_registration_dispatch_and_revocation(self):
        now = 1010.0
        sessions = handoff_mod.FederatedSessionStore(sqlite3.connect(":memory:"))
        receiver = handoff_mod.PassHandoffReceiver(
            verifier=Verifier(),
            replay_store=handoff_mod.HandoffReplayStore(sqlite3.connect(":memory:")),
            session_store=sessions,
            clock=lambda: now,
        )
        session = receiver.receive(
            raw_payload="cryptographically-verified-upstream-envelope",
            installed_package="com.topherofit.thf.pulse",
            expected_state="integration-state-1",
        )

        registry = life.NotificationTokenRegistry(sqlite3.connect(":memory:"), Vault())
        contract = http.NotificationHttpContract(registry)
        adapter = Adapter()
        guard = bridge_mod.PassSessionDeliveryGuard(authority=sessions, clock=lambda: now)
        dispatcher = dispatch.NotificationDispatcher(registry, {"test": adapter}, session_guard=guard)
        bridge = bridge_mod.PassNotificationBridge(
            authority=sessions, http_contract=contract, dispatcher=dispatcher, clock=lambda: now
        )
        principal = http.SessionPrincipal(
            "user-1", session.session_id, "com.topherofit.thf.pulse", True, None, False
        )

        created = bridge.register(
            principal=principal,
            body={
                "package": "com.topherofit.thf.pulse",
                "provider": "test",
                "provider_token": "provider-token-1",
            },
        )
        token_id = created.body["token_id"]
        request = provider.DeliveryRequest(
            token_id, "title.key", "body.key", "en", "thf://pulse/home", False
        )
        self.assertTrue(bridge.dispatch(principal=principal, request=request).accepted)
        self.assertEqual(len(adapter.calls), 1)

        sessions.revoke_session(session.session_id)
        with self.assertRaisesRegex(PermissionError, "revoked"):
            dispatcher.dispatch(subject="user-1", session_id=session.session_id, request=request)
        self.assertEqual(len(adapter.calls), 1)

    def test_cross_app_session_cannot_be_reused_for_another_package(self):
        now = 1010.0
        sessions = handoff_mod.FederatedSessionStore(sqlite3.connect(":memory:"))
        receiver = handoff_mod.PassHandoffReceiver(
            verifier=Verifier(), replay_store=handoff_mod.HandoffReplayStore(sqlite3.connect(":memory:")),
            session_store=sessions, clock=lambda: now,
        )
        session = receiver.receive(
            raw_payload="cryptographically-verified-upstream-envelope",
            installed_package="com.topherofit.thf.pulse", expected_state="integration-state-1",
        )
        registry = life.NotificationTokenRegistry(sqlite3.connect(":memory:"), Vault())
        contract = http.NotificationHttpContract(registry)
        adapter = Adapter()
        dispatcher = dispatch.NotificationDispatcher(
            registry, {"test": adapter},
            session_guard=bridge_mod.PassSessionDeliveryGuard(authority=sessions, clock=lambda: now),
        )
        bridge = bridge_mod.PassNotificationBridge(
            authority=sessions, http_contract=contract, dispatcher=dispatcher, clock=lambda: now
        )
        forged = http.SessionPrincipal(
            "user-1", session.session_id, "com.topherofit.thf.forge", True, None, False
        )
        with self.assertRaisesRegex(PermissionError, "audience"):
            bridge.register(
                principal=forged,
                body={"package": "com.topherofit.thf.forge", "provider": "test", "provider_token": "x"},
            )


if __name__ == "__main__":
    unittest.main()
