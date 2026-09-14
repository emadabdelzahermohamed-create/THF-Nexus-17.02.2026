import unittest

from shared_integration_contracts import ContractError
from shared_integration_runtime_v5 import (
    account_recovery_channel,
    guest_upgrade_plan,
    health_provider_capability_plan,
    identity_link_plan,
    normalized_health_record,
    runtime_v5_snapshot,
    user_preference_sync,
)


class SharedIntegrationRuntimeV5Tests(unittest.TestCase):
    def test_identity_link_requires_verified_credential(self):
        with self.assertRaisesRegex(ContractError, "provider_credential_verification_required"):
            identity_link_plan(
                authenticated_subject="u-1", current_provider="password", new_provider="google",
                new_provider_subject="google-sub", provider_credential_verified=False,
            )

    def test_identity_link_rejects_cross_account_collision(self):
        with self.assertRaisesRegex(ContractError, "identity_collision_manual_recovery_required"):
            identity_link_plan(
                authenticated_subject="u-1", current_provider="password", new_provider="google",
                new_provider_subject="google-sub", provider_credential_verified=True,
                existing_owner_subject="u-2",
            )

    def test_guest_upgrade_never_merges_finance_or_ranked_client_side(self):
        p = guest_upgrade_plan(
            guest_session_id="guest-session-1234567890", authenticated_subject="u-1",
            guest_progress_refs=["lesson:1", "workout:2"], server_ownership_verified=True,
        )
        self.assertFalse(p["economy_balance_client_merge_allowed"])
        self.assertFalse(p["ranked_state_client_merge_allowed"])
        self.assertTrue(p["guest_session_revocation_required"])

    def test_missing_samsung_provider_is_graceful(self):
        p = health_provider_capability_plan(
            provider="samsung_health_data_sdk", installed=False, authorized=False,
            available_metrics=[], requested_metrics=["steps", "heart_rate_bpm"],
        )
        self.assertFalse(p["usable"])
        self.assertFalse(p["provider_absence_is_fatal"])
        self.assertFalse(p["fallback_to_manual_health_claims_allowed"])

    def test_health_record_dedup_is_deterministic_and_provenance_bound(self):
        kwargs = dict(
            provider="health_connect", metric="steps", source_app_id="com.health.source",
            source_record_id="record-123", start_ms=1000, end_ms=2000,
            value_fingerprint="a" * 64,
        )
        a = normalized_health_record(**kwargs)
        b = normalized_health_record(**kwargs)
        self.assertEqual(a["dedup_key"], b["dedup_key"])
        self.assertTrue(a["provenance_complete"])
        self.assertFalse(a["reward_authority"])

    def test_rtl_is_derived_from_locale(self):
        self.assertTrue(user_preference_sync(locale="ar-EG", data_saver=True, reduce_motion=False, high_contrast=False)["rtl"])
        self.assertFalse(user_preference_sync(locale="en-US", data_saver=False, reduce_motion=False, high_contrast=True)["rtl"])
        with self.assertRaisesRegex(ContractError, "rtl_override_conflicts_with_locale"):
            user_preference_sync(locale="ar-EG", data_saver=False, reduce_motion=False, high_contrast=False, rtl_override=False)

    def test_operator_recovery_not_single_channel(self):
        p = account_recovery_channel(email="owner@example.com", verified=True, operator_account=True)
        self.assertFalse(p["single_channel_operator_recovery_allowed"])

    def test_snapshot_truth_is_fail_closed(self):
        s = runtime_v5_snapshot()
        self.assertEqual(s["schema"], "thf.shared.integration.runtime.v5")
        self.assertEqual(s["preferences"]["supported_locale_count"], 20)
        self.assertFalse(s["release_truth"]["physical_device_pass"])
        self.assertFalse(s["release_truth"]["final_or_play_ready"])


if __name__ == "__main__":
    unittest.main()
