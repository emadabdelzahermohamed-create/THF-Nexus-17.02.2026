import unittest
from shared_integration_contracts import ContractError
from shared_integration_runtime_v5 import normalized_health_record
from shared_integration_runtime_v6 import consent_minimization_plan, health_export_view, account_deletion_cascade, operator_step_up, cross_app_preference_payload, runtime_v6_snapshot


class SharedIntegrationV6Tests(unittest.TestCase):
    def test_health_permissions_fail_on_excess(self):
        with self.assertRaises(ContractError):
            consent_minimization_plan(provider="health_connect", requested_metrics=["steps", "sleep"], feature_metrics=["steps"])

    def test_health_export_redacts_raw_payload(self):
        r = normalized_health_record(provider="health_connect", metric="steps", source_app_id="hc", source_record_id="record-1", start_ms=1, end_ms=2, value_fingerprint="a"*64)
        out = health_export_view(records=[r], subject="user-1")
        self.assertFalse(out["raw_provider_payload_exported"])
        self.assertNotIn("value_fingerprint", out["records"][0])

    def test_delete_requires_recent_reauth(self):
        with self.assertRaises(ContractError):
            account_deletion_cascade(subject="user-1", recent_reauth=False, linked_providers=["google"], active_sessions=1)

    def test_operator_requires_step_up(self):
        session={"state":"authenticated", "subject":"operator-1", "roles":["admin"]}
        with self.assertRaises(ContractError):
            operator_step_up(product="admin", session=session, roles_issued_at=1000, passkey_uv=True, second_factor_verified=False, now=1100)

    def test_preference_payload_contains_no_sensitive_domains(self):
        out=cross_app_preference_payload(locale="ar-EG", data_saver=True, reduce_motion=False, high_contrast=True)
        self.assertTrue(out["rtl"])
        self.assertFalse(out["identity_fields_in_payload"])
        self.assertFalse(out["health_fields_in_payload"])
        self.assertFalse(out["economy_fields_in_payload"])

    def test_release_truth_remains_false(self):
        self.assertTrue(all(v is False for v in runtime_v6_snapshot()["release_truth"].values()))


if __name__ == "__main__":
    unittest.main()
