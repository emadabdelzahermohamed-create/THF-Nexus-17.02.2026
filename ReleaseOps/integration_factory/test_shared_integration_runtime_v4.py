from __future__ import annotations

import unittest

from shared_integration_contracts import ContractError, session_contract
from shared_integration_runtime_v4 import (
    HealthConsentReceipt,
    credential_manager_google_request,
    fresh_operator_authorization,
    health_sync_window,
    package_bound_handoff,
    product_brand_manifest,
    runtime_v4_snapshot,
    session_token_lifecycle,
    validate_google_identity_v4,
    verified_motion_submission,
)


class SharedIntegrationRuntimeV4Tests(unittest.TestCase):
    def test_credential_manager_contract_is_package_bound_and_secret_free(self):
        out = credential_manager_google_request(
            server_client_id="123456-abc.apps.googleusercontent.com",
            nonce="n" * 32,
            package_name="com.topherofit.thf.core",
        )
        self.assertTrue(out["credential_manager"])
        self.assertTrue(out["server_nonce_verification_required"])
        self.assertFalse(out["mobile_client_secret_allowed"])
        with self.assertRaisesRegex(ContractError, "client_secret"):
            credential_manager_google_request(
                server_client_id="123456-abc.apps.googleusercontent.com",
                nonce="n" * 32,
                package_name="com.topherofit.thf.core",
                client_secret_present=True,
            )
        with self.assertRaisesRegex(ContractError, "package_not_registered"):
            credential_manager_google_request(
                server_client_id="123456-abc.apps.googleusercontent.com",
                nonce="n" * 32,
                package_name="com.example.fake",
            )

    def test_google_identity_v4_requires_nonce_match_after_signature_verification(self):
        expected = "123456-abc.apps.googleusercontent.com"
        nonce = "z" * 32
        claims = {
            "iss": "https://accounts.google.com",
            "aud": expected,
            "exp": 2_000_000_000,
            "sub": "g-1",
            "email": "u@example.com",
            "email_verified": True,
            "nonce": nonce,
        }
        with self.assertRaisesRegex(ContractError, "nonce_mismatch"):
            validate_google_identity_v4(
                claims, expected_audience=expected, expected_nonce="q" * 32,
                signature_verified=True, now=1_900_000_000,
            )
        out = validate_google_identity_v4(
            claims, expected_audience=expected, expected_nonce=nonce,
            signature_verified=True, now=1_900_000_000,
        )
        self.assertEqual(out["provider_subject"], "g-1")

    def test_session_refresh_lifecycle_is_short_lived_rotating_and_secure(self):
        s = session_contract(state="authenticated", auth_method="google", subject="u:1", roles=["user"])
        out = session_token_lifecycle(
            session=s, access_expires_at=1500, refresh_token_id="r" * 20,
            device_id="device-123", now=1000,
        )
        self.assertTrue(out["refresh_rotation_required"])
        self.assertTrue(out["reuse_detection_required"])
        self.assertTrue(out["secure_storage_only"])
        self.assertNotIn("r" * 20, str(out))
        with self.assertRaisesRegex(ContractError, "lifetime"):
            session_token_lifecycle(
                session=s, access_expires_at=4000, refresh_token_id="r" * 20,
                device_id="device-123", now=1000,
            )

    def test_operator_access_requires_fresh_server_role_claim(self):
        s = session_contract(state="authenticated", auth_method="passkey", subject="u:1", roles=["admin"])
        with self.assertRaisesRegex(ContractError, "fresh_server_role_claim"):
            fresh_operator_authorization(product="admin", session=s, roles_issued_at=600, now=1000)
        out = fresh_operator_authorization(product="admin", session=s, roles_issued_at=900, now=1000)
        self.assertTrue(out["server_role_claim_fresh"])
        self.assertFalse(out["client_role_override_allowed"])

    def test_cross_app_handoff_is_bound_to_exact_target_package(self):
        with self.assertRaisesRegex(ContractError, "target_package_mismatch"):
            package_bound_handoff(
                source="hub", target="fitness", target_package="com.fake.fitness",
                subject="u:1", nonce="h" * 16, expires_at=1100, now=1000,
            )
        out = package_bound_handoff(
            source="hub", target="fitness", target_package="com.topherofit.thf.pulse",
            subject="u:1", nonce="h" * 16, expires_at=1100, now=1000,
        )
        self.assertTrue(out["audience_bound"])
        self.assertTrue(out["server_signature_must_cover_target_package"])

    def test_health_consent_receipt_and_sync_fail_closed_after_revocation(self):
        receipt = HealthConsentReceipt(
            subject="u:1", provider="health_connect", metrics=("steps", "heart_rate_bpm"),
            granted_at=900, consent_id="c" * 16,
        )
        self.assertTrue(receipt.active)
        self.assertFalse(receipt.audit_view["raw_health_payload_present"])
        sync = health_sync_window(receipt=receipt, metric="steps", start_ms=0, end_ms=1000)
        self.assertTrue(sync["dedup_required"])
        self.assertFalse(sync["client_reward_authority"])
        revoked = HealthConsentReceipt(
            subject="u:1", provider="health_connect", metrics=("steps",),
            granted_at=900, revoked_at=950, consent_id="d" * 16,
        )
        with self.assertRaisesRegex(ContractError, "consent_revoked"):
            health_sync_window(receipt=revoked, metric="steps", start_ms=0, end_ms=1000)

    def test_health_sync_requires_consent_metric_and_bounded_window(self):
        receipt = HealthConsentReceipt(
            subject="u:1", provider="health_connect", metrics=("steps",),
            granted_at=900, consent_id="e" * 16,
        )
        with self.assertRaisesRegex(ContractError, "not_consented"):
            health_sync_window(receipt=receipt, metric="sleep", start_ms=0, end_ms=1000)
        with self.assertRaisesRegex(ContractError, "too_large"):
            health_sync_window(
                receipt=receipt, metric="steps", start_ms=0,
                end_ms=32 * 24 * 60 * 60 * 1000,
            )

    def test_motion_submission_keeps_reward_verdict_server_authoritative(self):
        out = verified_motion_submission(
            subject="u:1", workout_id="squat-1", source="combined", repetitions=15,
            confidence=.93, monotonic_ms=5000, sensor_attested=True,
            evidence_nonce="m" * 16, health_record_refs=["hc:1", "hc:1", "sh:2"],
        )
        self.assertTrue(out["server_verdict_required"])
        self.assertTrue(out["health_data_is_supporting_evidence_only"])
        self.assertFalse(out["manual_reward_override_allowed"])
        self.assertEqual(out["health_record_refs"], ["hc:1", "sh:2"])

    def test_brand_manifest_preserves_packages_and_operator_listing_policy(self):
        hub = product_brand_manifest("hub")
        self.assertEqual(hub["package"], "com.topherofit.thf.core")
        self.assertEqual(hub["display_name_ar"], "مركز THF")
        self.assertTrue(hub["adaptive_icon_required"])
        self.assertFalse(hub["package_id_change_allowed"])
        admin = product_brand_manifest("admin")
        self.assertFalse(admin["operator_listing_public"])

    def test_snapshot_never_claims_external_or_phone_gates(self):
        snap = runtime_v4_snapshot()
        self.assertEqual(snap["schema"], "thf.shared.integration.runtime.v4")
        truth = snap["release_truth"]
        self.assertFalse(truth["google_oauth_console_configured"])
        self.assertFalse(truth["durable_session_refresh_store_bound"])
        self.assertFalse(truth["operator_role_issuer_bound"])
        self.assertFalse(truth["health_consent_store_bound"])
        self.assertFalse(truth["physical_device_pass"])
        self.assertFalse(truth["final_or_play_ready"])


if __name__ == "__main__":
    unittest.main()
