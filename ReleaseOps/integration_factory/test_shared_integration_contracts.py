import json
import unittest

from shared_integration_contracts import (
    ContractError,
    HealthRecord,
    OneTimeReplayLedger,
    account_deletion_contract,
    assert_operator_route,
    authorize_product_for_session,
    contract_snapshot,
    cross_app_handoff,
    deduplicate_health_records,
    email_code_contract,
    health_permission_plan,
    health_provider_capability,
    link_guest_to_identity,
    motion_evidence_contract,
    password_registration_policy,
    preference_contract,
    session_contract,
    validate_google_id_token_claims,
    validate_google_oauth_config,
    validate_passkey_assertion,
    validate_passkey_registration,
    visible_products,
    visible_products_for_session,
)


class SharedIntegrationContractsTest(unittest.TestCase):
    def test_public_user_never_sees_operator_apps(self):
        visible = set(visible_products(["user"]))
        self.assertNotIn("admin", visible)
        self.assertNotIn("publisher", visible)
        self.assertIn("fitness", visible)
        self.assertIn("world", visible)

    def test_session_visibility_never_trusts_unauthenticated_operator_roles(self):
        visible = set(visible_products_for_session({"state": "guest", "roles": ["admin", "owner"]}))
        self.assertNotIn("admin", visible)
        self.assertNotIn("publisher", visible)
        authenticated = set(visible_products_for_session({"state": "authenticated", "subject": "u:1", "roles": ["admin"]}))
        self.assertIn("admin", authenticated)
        self.assertIn("publisher", authenticated)

    def test_admin_role_exposes_admin_and_publisher_for_compatibility_helper(self):
        visible = set(visible_products(["admin"]))
        self.assertIn("admin", visible)
        self.assertIn("publisher", visible)

    def test_publisher_cannot_enter_admin(self):
        with self.assertRaisesRegex(ContractError, "operator_role_required"):
            assert_operator_route("admin", ["publisher"])
        assert_operator_route("publisher", ["publisher"])

    def test_operator_route_requires_authenticated_server_session(self):
        with self.assertRaisesRegex(ContractError, "authenticated_session"):
            authorize_product_for_session("admin", {"state": "guest", "subject": "g:1", "roles": ["admin"]})
        with self.assertRaisesRegex(ContractError, "operator_role_required"):
            authorize_product_for_session("admin", {"state": "authenticated", "subject": "u:1", "roles": ["publisher"]})
        authorize_product_for_session("admin", {"state": "authenticated", "subject": "u:1", "roles": ["admin"]})

    def test_mobile_oauth_config_rejects_client_secret(self):
        with self.assertRaisesRegex(ContractError, "client_secret"):
            validate_google_oauth_config({"server_client_id": "123456-abc.apps.googleusercontent.com", "redirect_scheme": "thf", "client_secret": "must-not-ship"})

    def test_mobile_oauth_config_accepts_server_client_id_only(self):
        cfg = validate_google_oauth_config({"server_client_id": "123456-abc.apps.googleusercontent.com", "redirect_scheme": "thf"})
        self.assertEqual(cfg["redirect_scheme"], "thf")

    def test_google_claims_require_prior_signature_verification(self):
        expected = "123456-abc.apps.googleusercontent.com"
        base = {"iss": "https://accounts.google.com", "aud": expected, "exp": 2_000_000_000, "sub": "google-user-1", "email": "User@Example.com", "email_verified": True}
        with self.assertRaisesRegex(ContractError, "signature_verification_required"):
            validate_google_id_token_claims(base, expected_audience=expected, signature_verified=False, now=1_900_000_000)
        identity = validate_google_id_token_claims(base, expected_audience=expected, signature_verified=True, now=1_900_000_000)
        self.assertEqual(identity["email"], "user@example.com")

    def test_email_code_is_hashed_short_lived_rate_limited_and_single_use(self):
        out = email_code_contract(email="User@example.com", code_hash="a" * 64, expires_at=1500, now=1000, attempts_remaining=5)
        self.assertEqual(out["email"], "user@example.com")
        self.assertFalse(out["plaintext_code_persisted"])
        self.assertTrue(out["single_use_required"])
        self.assertTrue(out["rate_limit_required"])
        with self.assertRaisesRegex(ContractError, "expiry"):
            email_code_contract(email="u@example.com", code_hash="b" * 64, expires_at=1700, now=1000)

    def test_password_policy_rejects_short_or_compromised_passwords_without_shipping_password(self):
        with self.assertRaisesRegex(ContractError, "length"):
            password_registration_policy(email="u@example.com", password_length=8, compromised_password_check_passed=True)
        with self.assertRaisesRegex(ContractError, "compromised"):
            password_registration_policy(email="u@example.com", password_length=16, compromised_password_check_passed=False)
        out = password_registration_policy(email="u@example.com", password_length=16, compromised_password_check_passed=True)
        self.assertFalse(out["client_password_persistence_allowed"])
        self.assertTrue(out["server_password_hash_required"])

    def test_passkey_requires_server_grade_challenge(self):
        with self.assertRaisesRegex(ContractError, "challenge_too_short"):
            validate_passkey_registration({"rp_id": "thf.example.com", "user_id": "u1", "challenge": "short"})
        out = validate_passkey_registration({"rp_id": "thf.example.com", "user_id": "u1", "challenge": "x" * 32})
        self.assertEqual(out["attestation"], "none")

    def test_passkey_assertion_requires_challenge_user_and_signature_verification(self):
        with self.assertRaisesRegex(ContractError, "challenge_mismatch"):
            validate_passkey_assertion(rp_id="thf.example.com", credential_id="cred-1", challenge_matched=False, user_verified=True, signature_verified=True)
        with self.assertRaisesRegex(ContractError, "signature_verification"):
            validate_passkey_assertion(rp_id="thf.example.com", credential_id="cred-1", challenge_matched=True, user_verified=True, signature_verified=False)
        out = validate_passkey_assertion(rp_id="thf.example.com", credential_id="cred-1", challenge_matched=True, user_verified=True, signature_verified=True)
        self.assertTrue(out["challenge_consume_required"])

    def test_reference_replay_ledger_fails_closed_and_is_explicitly_not_production_durable(self):
        ledger = OneTimeReplayLedger()
        self.assertFalse(ledger.production_durable)
        ledger.consume(namespace="passkey", token="x" * 32, expires_at=1200, now=1000)
        with self.assertRaisesRegex(ContractError, "replay_detected"):
            ledger.consume(namespace="passkey", token="x" * 32, expires_at=1200, now=1001)
        ledger.consume(namespace="handoff", token="y" * 32, expires_at=1200, now=1001)

    def test_session_contract_keeps_operator_roles_authenticated(self):
        auth = session_contract(state="authenticated", auth_method="google", subject="g:1", roles=["admin"])
        self.assertTrue(auth["persist_refresh_token_in_secure_storage_only"])
        self.assertTrue(auth["logout_revokes_server_session"])
        with self.assertRaisesRegex(ContractError, "operator_session"):
            session_contract(state="guest", auth_method="guest", roles=["admin"])

    def test_account_deletion_requires_authenticated_recent_reauth(self):
        session = session_contract(state="authenticated", auth_method="google", subject="g:1", roles=["user"])
        with self.assertRaisesRegex(ContractError, "recent_reauthentication"):
            account_deletion_contract(session=session, confirmation_nonce="z" * 16, reauthenticated_at=600, now=1000)
        out = account_deletion_contract(session=session, confirmation_nonce="z" * 16, reauthenticated_at=900, now=1000)
        self.assertTrue(out["revoke_sessions"])
        self.assertTrue(out["unlink_identity_providers"])
        self.assertFalse(out["client_side_delete_is_authoritative"])

    def test_cross_app_handoff_is_short_lived_single_use_and_no_roles(self):
        out = cross_app_handoff(source="hub", target="fitness", subject="user:1", nonce="n" * 16, expires_at=1120, now=1000)
        self.assertTrue(out["server_signed_required"])
        self.assertTrue(out["single_use_required"])
        self.assertFalse(out["carry_roles"])
        self.assertFalse(out["carry_secrets"])
        with self.assertRaisesRegex(ContractError, "expiry"):
            cross_app_handoff(source="hub", target="fitness", subject="user:1", nonce="n" * 16, expires_at=2000, now=1000)

    def test_health_records_deduplicate_by_provider_provenance_when_no_canonical_id(self):
        one = HealthRecord("health_connect", "hc-1", "steps", 100, 200, {"value": 123})
        duplicate = HealthRecord("health_connect", "hc-1", "steps", 100, 200, {"value": 999})
        samsung = HealthRecord("samsung_health_data_sdk", "sh-1", "steps", 100, 200, {"value": 123})
        rows = deduplicate_health_records([one, duplicate, samsung])
        self.assertEqual(len(rows), 2)
        self.assertNotEqual(one.dedup_key, samsung.dedup_key)

    def test_health_records_can_deduplicate_same_canonical_source_across_providers(self):
        hc = HealthRecord("health_connect", "hc-7", "steps", 100, 200, {"value": 123}, canonical_source_id="watch-record-7", origin_package="com.vendor.watch")
        samsung = HealthRecord("samsung_health_data_sdk", "sh-9", "steps", 100, 200, {"value": 123}, canonical_source_id="watch-record-7", origin_package="com.vendor.watch")
        rows = deduplicate_health_records([hc, samsung])
        self.assertEqual(len(rows), 1)
        self.assertEqual(hc.provenance["origin_package"], "com.vendor.watch")

    def test_health_permission_plan_is_consent_first_and_non_authoritative(self):
        plan = health_permission_plan(["steps", "heart_rate_bpm"], provider="health_connect")
        self.assertTrue(plan["consent_required"])
        self.assertTrue(plan["graceful_absence"])
        self.assertFalse(plan["background_read_default"])
        self.assertFalse(plan["historical_read_default"])
        self.assertFalse(plan["reward_authority"])

    def test_health_provider_capability_degrades_gracefully(self):
        samsung = health_provider_capability(provider="samsung_health_data_sdk", installed=True, permission_granted=True, partner_authorized=False)
        self.assertFalse(samsung["available"])
        self.assertTrue(samsung["absence_is_nonfatal"])
        self.assertEqual(samsung["fallback_provider"], "health_connect")
        hc = health_provider_capability(provider="health_connect", installed=True, permission_granted=True)
        self.assertTrue(hc["available"])

    def test_motion_evidence_never_has_client_reward_authority_and_requires_replay_protection(self):
        out = motion_evidence_contract(source="combined", repetitions=12, confidence=.91, monotonic_ms=5000, sensor_attested=True, evidence_nonce="m" * 16)
        self.assertFalse(out["client_reward_authority"])
        self.assertTrue(out["server_verification_required"])
        self.assertTrue(out["replay_protection_required"])
        with self.assertRaisesRegex(ContractError, "confidence"):
            motion_evidence_contract(source="camera_pose", repetitions=1, confidence=1.1, monotonic_ms=1, sensor_attested=False)

    def test_preferences_bind_rtl_and_accessibility(self):
        ar = preference_contract(locale="ar-EG", data_saver=True, reduce_motion=True, high_contrast=False)
        self.assertEqual(ar["layout_direction"], "rtl")
        en = preference_contract(locale="en-US", data_saver=False, reduce_motion=False, high_contrast=True)
        self.assertEqual(en["layout_direction"], "ltr")

    def test_guest_link_requires_verified_proof(self):
        with self.assertRaisesRegex(ContractError, "verified_identity_proof_required"):
            link_guest_to_identity(guest_id="guest-1", identity_subject="google-1", proof_verified=False)
        linked = link_guest_to_identity(guest_id="guest-1", identity_subject="google-1", proof_verified=True)
        self.assertEqual(linked["to"], "identity")

    def test_snapshot_preserves_truth_boundaries(self):
        snap = json.loads(contract_snapshot())
        self.assertEqual(snap["schema"], "thf.shared.integration.v3")
        self.assertFalse(snap["truth"]["google_oauth_console_configured"])
        self.assertFalse(snap["truth"]["google_server_signature_verifier_bound"])
        self.assertFalse(snap["truth"]["passkey_backend_challenge_store_bound"])
        self.assertFalse(snap["truth"]["durable_replay_store_bound"])
        self.assertFalse(snap["truth"]["email_auth_delivery_backend_bound"])
        self.assertFalse(snap["truth"]["account_deletion_backend_bound"])
        self.assertFalse(snap["truth"]["cross_app_handoff_server_signer_bound"])
        self.assertFalse(snap["truth"]["health_connect_physical_device_verified"])
        self.assertFalse(snap["truth"]["samsung_partner_registration_verified"])
        self.assertFalse(snap["truth"]["final_or_play_ready"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
