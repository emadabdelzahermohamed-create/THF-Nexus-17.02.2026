import json
import unittest

from shared_integration_contracts import (
    ContractError,
    HealthRecord,
    contract_snapshot,
    deduplicate_health_records,
    health_permission_plan,
    link_guest_to_identity,
    validate_google_id_token_claims,
    validate_google_oauth_config,
    visible_products,
    assert_operator_route,
)


class SharedIntegrationContractsTest(unittest.TestCase):
    def test_public_user_never_sees_operator_apps(self):
        visible = set(visible_products(["user"]))
        self.assertNotIn("admin", visible)
        self.assertNotIn("publisher", visible)
        self.assertIn("fitness", visible)
        self.assertIn("world", visible)

    def test_admin_role_exposes_admin_and_publisher(self):
        visible = set(visible_products(["admin"]))
        self.assertIn("admin", visible)
        self.assertIn("publisher", visible)

    def test_publisher_cannot_enter_admin(self):
        with self.assertRaisesRegex(ContractError, "operator_role_required"):
            assert_operator_route("admin", ["publisher"])
        assert_operator_route("publisher", ["publisher"])

    def test_mobile_oauth_config_rejects_client_secret(self):
        with self.assertRaisesRegex(ContractError, "client_secret"):
            validate_google_oauth_config({
                "server_client_id": "123456-abc.apps.googleusercontent.com",
                "redirect_scheme": "thf",
                "client_secret": "must-not-ship",
            })

    def test_mobile_oauth_config_accepts_server_client_id_only(self):
        cfg = validate_google_oauth_config({
            "server_client_id": "123456-abc.apps.googleusercontent.com",
            "redirect_scheme": "thf",
        })
        self.assertEqual(cfg["redirect_scheme"], "thf")

    def test_google_claims_fail_closed_and_accept_verified_identity(self):
        expected = "123456-abc.apps.googleusercontent.com"
        base = {
            "iss": "https://accounts.google.com",
            "aud": expected,
            "exp": 2_000_000_000,
            "sub": "google-user-1",
            "email": "User@Example.com",
            "email_verified": True,
        }
        identity = validate_google_id_token_claims(base, expected_audience=expected, now=1_900_000_000)
        self.assertEqual(identity["email"], "user@example.com")
        bad = dict(base, aud="wrong.apps.googleusercontent.com")
        with self.assertRaisesRegex(ContractError, "audience"):
            validate_google_id_token_claims(bad, expected_audience=expected, now=1_900_000_000)
        bad = dict(base, email_verified=False)
        with self.assertRaisesRegex(ContractError, "not_verified"):
            validate_google_id_token_claims(bad, expected_audience=expected, now=1_900_000_000)

    def test_health_records_deduplicate_by_provenance(self):
        one = HealthRecord("health_connect", "hc-1", "steps", 100, 200, {"value": 123})
        duplicate = HealthRecord("health_connect", "hc-1", "steps", 100, 200, {"value": 999})
        samsung = HealthRecord("samsung_health_data_sdk", "sh-1", "steps", 100, 200, {"value": 123})
        rows = deduplicate_health_records([one, duplicate, samsung])
        self.assertEqual(len(rows), 2)
        self.assertNotEqual(one.dedup_key, samsung.dedup_key)

    def test_health_permission_plan_is_consent_first_and_non_authoritative(self):
        plan = health_permission_plan(["steps", "heart_rate_bpm"], provider="health_connect")
        self.assertTrue(plan["consent_required"])
        self.assertTrue(plan["graceful_absence"])
        self.assertFalse(plan["background_read_default"])
        self.assertFalse(plan["historical_read_default"])
        self.assertFalse(plan["reward_authority"])

    def test_guest_link_requires_verified_proof(self):
        with self.assertRaisesRegex(ContractError, "verified_identity_proof_required"):
            link_guest_to_identity(guest_id="guest-1", identity_subject="google-1", proof_verified=False)
        linked = link_guest_to_identity(guest_id="guest-1", identity_subject="google-1", proof_verified=True)
        self.assertEqual(linked["to"], "identity")

    def test_snapshot_preserves_truth_boundaries(self):
        snap = json.loads(contract_snapshot())
        self.assertFalse(snap["truth"]["google_oauth_console_configured"])
        self.assertFalse(snap["truth"]["health_connect_physical_device_verified"])
        self.assertFalse(snap["truth"]["samsung_partner_registration_verified"])
        self.assertFalse(snap["truth"]["final_or_play_ready"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
