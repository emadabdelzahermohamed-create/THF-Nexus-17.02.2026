import unittest

from shared_integration_contracts import ContractError
from shared_integration_runtime_v7 import device_bound_session, health_consent_transition, provider_failover_plan, privileged_route_guard, runtime_v7_snapshot


class SharedIntegrationV7Tests(unittest.TestCase):
    def test_device_bound_session(self):
        result = device_bound_session(subject="u1", package_id="com.topherofit.thf.core", device_key_thumbprint="key-1", issued_at=1000, expires_at=1600, now=1100)
        self.assertTrue(result["proof_of_possession_required"])
        self.assertFalse(result["client_role_claims_authoritative"])

    def test_device_session_rejects_unregistered_package(self):
        with self.assertRaises(ContractError):
            device_bound_session(subject="u1", package_id="evil.app", device_key_thumbprint="key-1", issued_at=1000, expires_at=1600, now=1100)

    def test_health_consent_revocation_stops_sync(self):
        result = health_consent_transition(provider="health_connect", current_state="granted", action="revoke", now=2000)
        self.assertEqual(result["state"], "revoked")
        self.assertFalse(result["sync_allowed"])
        self.assertEqual(result["granted_metrics"], [])

    def test_health_connect_preferred_and_samsung_optional(self):
        result = provider_failover_plan(health_connect_available=True, samsung_available=True, consented_providers=["health_connect", "samsung_health"])
        self.assertEqual(result["primary"], "health_connect")
        self.assertFalse(result["fabricate_health_data"])

    def test_provider_absence_is_graceful(self):
        result = provider_failover_plan(health_connect_available=False, samsung_available=False, consented_providers=[])
        self.assertTrue(result["graceful_absence"])
        self.assertIsNone(result["primary"])

    def test_admin_requires_server_role_and_device_proof(self):
        session = {"state": "authenticated", "server_roles": ["admin"]}
        self.assertTrue(privileged_route_guard(product="admin", session=session, device_proof_valid=True, step_up_age_seconds=30)["allowed"])
        with self.assertRaises(ContractError):
            privileged_route_guard(product="admin", session=session, device_proof_valid=False, step_up_age_seconds=30)

    def test_ordinary_user_cannot_enter_admin(self):
        with self.assertRaises(ContractError):
            privileged_route_guard(product="admin", session={"state": "authenticated", "server_roles": ["user"]}, device_proof_valid=True, step_up_age_seconds=10)

    def test_release_truth_remains_false(self):
        snap = runtime_v7_snapshot()
        self.assertFalse(snap["release_truth"]["physical_device_pass"])
        self.assertFalse(snap["release_truth"]["final_or_play_ready"])


if __name__ == "__main__":
    unittest.main()
