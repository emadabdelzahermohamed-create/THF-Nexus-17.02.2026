#!/usr/bin/env python3
import copy
import datetime as dt
import json
import pathlib
import unittest

from revenue_value_basis import *

HERE = pathlib.Path(__file__).resolve().parent
BASE_POLICY = json.loads((HERE / "policy.json").read_text())
NOW = dt.datetime(2026, 9, 14, 5, 0, tzinfo=dt.timezone.utc)


def external_evidence():
    return {
        "schema": "thf-tokenops-revenue-value-basis/v1",
        "network": NETWORK,
        "mint": MINT,
        "token_program": TOKEN_PROGRAM,
        "source_unit": "USD_MINOR",
        "target_unit": TARGET_UNIT,
        "method": "approved_rational_conversion",
        "thf_raw_numerator": 250000,
        "source_minor_denominator": 100,
        "conversion_source_evidence_sha256": "b" * 64,
        "governance_approval_evidence_sha256": "c" * 64,
        "observed_at_utc": "2026-09-14T04:00:00+00:00",
        "expires_at_utc": "2026-09-14T06:00:00+00:00",
    }


def approved_policy(evidence):
    p = copy.deepcopy(BASE_POLICY)
    p["distribution_controls"]["revenue_value_basis_status"] = "approved"
    p["distribution_controls"]["revenue_value_basis_evidence_sha256"] = sha256(evidence)
    return p


class RevenueValueBasisTests(unittest.TestCase):
    def test_current_policy_fails_closed(self):
        e = external_evidence()
        r = validate_basis_evidence(BASE_POLICY, e, now_utc=NOW)
        self.assertEqual(r["status"], "FAIL_CLOSED")
        self.assertIn("revenue_value_basis_not_approved", r["blockers"])
        self.assertFalse(r["execution_authorized"])

    def test_hash_mismatch_fails_closed(self):
        e = external_evidence()
        p = approved_policy(e)
        p["distribution_controls"]["revenue_value_basis_evidence_sha256"] = "d" * 64
        r = validate_basis_evidence(p, e, now_utc=NOW)
        self.assertIn("value_basis_evidence_hash_mismatch", r["blockers"])

    def test_external_evidence_passes_review_only_when_bound(self):
        e = external_evidence()
        r = validate_basis_evidence(approved_policy(e), e, now_utc=NOW)
        self.assertEqual(r["status"], "PASS_REVIEW_ONLY")
        self.assertFalse(r["broadcast"])
        self.assertFalse(r["financial_effect"])

    def test_expired_evidence_fails_closed(self):
        e = external_evidence()
        e["expires_at_utc"] = "2026-09-14T04:30:00+00:00"
        r = validate_basis_evidence(approved_policy(e), e, now_utc=NOW)
        self.assertIn("value_basis_evidence_expired", r["blockers"])

    def test_future_evidence_fails_closed(self):
        e = external_evidence()
        e["observed_at_utc"] = "2026-09-14T05:30:00+00:00"
        e["expires_at_utc"] = "2026-09-14T06:30:00+00:00"
        r = validate_basis_evidence(approved_policy(e), e, now_utc=NOW)
        self.assertIn("value_basis_not_yet_valid", r["blockers"])

    def test_external_budget_uses_integer_floor(self):
        e = external_evidence()
        p = approved_policy(e)
        r = derive_35pct_thf_budget(p, e, 10001, now_utc=NOW)
        source_share = 10001 * 3500 // 10000
        self.assertEqual(r["share_in_source_minor"], source_share)
        self.assertEqual(r["proposed_thf_budget_raw"], source_share * 250000 // 100)
        self.assertEqual(r["status"], "REVIEW_READY_NOT_EXECUTION_READY")
        self.assertFalse(r["execution_authorized"])

    def test_identity_thf_raw_is_exact(self):
        e = {
            "schema": "thf-tokenops-revenue-value-basis/v1",
            "network": NETWORK,
            "mint": MINT,
            "token_program": TOKEN_PROGRAM,
            "source_unit": TARGET_UNIT,
            "target_unit": TARGET_UNIT,
            "method": "identity_thf_raw",
            "governance_approval_evidence_sha256": "a" * 64,
            "observed_at_utc": "2026-09-14T04:00:00+00:00",
            "expires_at_utc": "2026-09-14T06:00:00+00:00",
        }
        r = derive_35pct_thf_budget(approved_policy(e), e, 10000, now_utc=NOW)
        self.assertEqual(r["proposed_thf_budget_raw"], 3500)
        self.assertEqual(r["conversion_remainder_numerator"], 0)

    def test_external_rate_requires_source_evidence_hash(self):
        e = external_evidence()
        del e["conversion_source_evidence_sha256"]
        r = validate_basis_evidence(approved_policy(e), e, now_utc=NOW)
        self.assertIn("conversion_source_evidence_missing", r["blockers"])

    def test_governance_approval_evidence_required(self):
        e = external_evidence()
        del e["governance_approval_evidence_sha256"]
        r = validate_basis_evidence(approved_policy(e), e, now_utc=NOW)
        self.assertIn("governance_approval_evidence_missing", r["blockers"])

    def test_sensitive_material_is_rejected(self):
        e = external_evidence()
        e["private_key"] = "never"
        with self.assertRaises(ValueError):
            validate_basis_evidence(approved_policy(external_evidence()), e, now_utc=NOW)

    def test_no_transaction_or_signature_material_is_created(self):
        e = external_evidence()
        r = derive_35pct_thf_budget(approved_policy(e), e, 10000, now_utc=NOW)
        self.assertFalse(r["transaction_bytes_created"])
        self.assertFalse(r["signed"])
        self.assertFalse(r["submitted"])
        self.assertFalse(r["broadcast"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
