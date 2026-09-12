#!/usr/bin/env python3
import copy
import hashlib
import json
import tempfile
import unittest

import audit_export
import external_anchor_continuity_gate as continuity
import external_ledger_anchor_gate as anchor


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class ExternalAnchorContinuityGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        self.tmp.close()
        event = {
            "event_type": "tokenops_review_replay_token_consumed",
            "network": anchor.NETWORK,
            "mint": anchor.MINT,
            "review_replay_token_sha256": "a" * 64,
            "simulation_review_eligible": True,
            "simulation_execution_permitted": False,
            "transaction_created": False,
            "transaction_serialized": False,
            "transaction_signed": False,
            "transaction_submitted": False,
            "broadcast_allowed": False,
            "financial_effect": False,
            "private_key_used": False,
            "wave_mawja_touched": False,
        }
        audit_export.append_entry(event, self.tmp.name, created_at=1)
        self.source_head = "b" * 40
        self.request = anchor.prepare_anchor_request(self.tmp.name, self.source_head)
        receipt = {
            "provider": "gcp-object-lock",
            "object_id": "projects/thf/locations/global/buckets/tokenops-anchor/objects/ledger-head-001#g1",
            "immutable_retention": True,
            "externally_verified": True,
            "identity_mode": "workload-identity-federation-or-equivalent-short-lived",
            "persistent_service_account_key_used": False,
            "anchor_request_sha256": self.request["anchor_request_sha256"],
            "ledger_head_sha256": self.request["ledger_head_sha256"],
            "ledger_bytes_sha256": self.request["ledger_bytes_sha256"],
            "source_head_sha": self.request["source_head_sha"],
            "anchored_at_utc": "2026-09-12T18:00:00Z",
        }
        receipt["receipt_sha256"] = sha(receipt)
        self.receipt = receipt

    def test_valid_anchor_binds_exact_live_ledger(self):
        out = continuity.verify_continuity(self.request, self.receipt, self.tmp.name, self.source_head)
        self.assertTrue(out["external_immutable_anchor_verified"])
        self.assertTrue(out["ledger_continuity_verified"])
        self.assertTrue(out["replay_guard_prior_head_eligible"])
        self.assertEqual(out["anchored_prior_ledger_head_sha256"], self.request["ledger_head_sha256"])
        self.assertFalse(out["simulation_execution_permitted"])
        self.assertFalse(out["execution_authorized"])
        self.assertFalse(out["financial_effect"])
        self.assertTrue(continuity.verify_record(out)["verified"])

    def test_rejects_ledger_advanced_after_anchor(self):
        audit_export.append_entry({
            "event_type": "later-review-event",
            "network": anchor.NETWORK,
            "mint": anchor.MINT,
            "simulation_execution_permitted": False,
            "transaction_created": False,
            "transaction_signed": False,
            "transaction_submitted": False,
            "broadcast_allowed": False,
            "financial_effect": False,
            "private_key_used": False,
            "wave_mawja_touched": False,
        }, self.tmp.name, created_at=2)
        with self.assertRaises(ValueError):
            continuity.verify_continuity(self.request, self.receipt, self.tmp.name, self.source_head)

    def test_rejects_ledger_bytes_tampering(self):
        with open(self.tmp.name, "a", encoding="utf-8") as f:
            f.write("\n")
        with self.assertRaises(ValueError):
            continuity.verify_continuity(self.request, self.receipt, self.tmp.name, self.source_head)

    def test_rejects_wrong_source_head(self):
        with self.assertRaises(ValueError):
            continuity.verify_continuity(self.request, self.receipt, self.tmp.name, "c" * 40)

    def test_rejects_receipt_tampering(self):
        r = copy.deepcopy(self.receipt)
        r["object_id"] += "-changed"
        with self.assertRaises(ValueError):
            continuity.verify_continuity(self.request, r, self.tmp.name, self.source_head)

    def test_rejects_persistent_service_account_key(self):
        r = copy.deepcopy(self.receipt)
        r["persistent_service_account_key_used"] = True
        core = dict(r); core.pop("receipt_sha256", None); r["receipt_sha256"] = sha(core)
        with self.assertRaises(ValueError):
            continuity.verify_continuity(self.request, r, self.tmp.name, self.source_head)

    def test_rejects_secret_field(self):
        r = copy.deepcopy(self.receipt)
        r["private_key"] = "forbidden"
        with self.assertRaises(ValueError):
            continuity.verify_continuity(self.request, r, self.tmp.name, self.source_head)

    def test_record_digest_is_fail_closed(self):
        out = continuity.verify_continuity(self.request, self.receipt, self.tmp.name, self.source_head)
        out["simulation_execution_permitted"] = True
        with self.assertRaises(ValueError):
            continuity.verify_record(out)


if __name__ == "__main__":
    unittest.main()
