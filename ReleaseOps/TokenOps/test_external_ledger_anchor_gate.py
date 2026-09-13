#!/usr/bin/env python3
import copy
import hashlib
import json
import tempfile
import unittest

import audit_export
import external_ledger_anchor_gate as gate


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class ExternalLedgerAnchorGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        self.tmp.close()
        event = {
            "event_type": "tokenops_review_replay_token_consumed",
            "network": gate.NETWORK,
            "mint": gate.MINT,
            "review_replay_token_sha256": "a" * 64,
            "simulation_review_eligible": True,
            "simulation_execution_permitted": False,
            "transaction_created": False,
            "transaction_signed": False,
            "transaction_submitted": False,
            "broadcast_allowed": False,
            "financial_effect": False,
            "private_key_used": False,
            "wave_mawja_touched": False,
        }
        audit_export.append_entry(event, self.tmp.name, created_at=1)
        self.request = gate.prepare_anchor_request(self.tmp.name, "b" * 40)
        core = {
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
            "anchored_at_utc": "2026-09-12T17:00:00Z",
        }
        core["receipt_sha256"] = sha(core)
        self.receipt = core

    def test_request_is_non_execution(self):
        self.assertFalse(self.request["simulation_review_eligible"])
        self.assertFalse(self.request["execution_authorized"])
        self.assertFalse(self.request["financial_effect"])

    def test_valid_receipt_only_opens_review_eligibility(self):
        out = gate.verify_anchor_receipt(self.request, self.receipt)
        self.assertTrue(out["external_immutable_anchor_verified"])
        self.assertTrue(out["simulation_review_eligible"])
        self.assertFalse(out["simulation_execution_permitted"])
        self.assertFalse(out["execution_authorized"])
        self.assertFalse(out["transaction_signed"])
        self.assertFalse(out["broadcast_allowed"])

    def _resign(self, receipt):
        core = dict(receipt); core.pop("receipt_sha256", None)
        receipt["receipt_sha256"] = sha(core)
        return receipt

    def test_rejects_wrong_head(self):
        r = copy.deepcopy(self.receipt); r["ledger_head_sha256"] = "c" * 64; self._resign(r)
        with self.assertRaises(ValueError): gate.verify_anchor_receipt(self.request, r)

    def test_rejects_non_immutable_receipt(self):
        r = copy.deepcopy(self.receipt); r["immutable_retention"] = False; self._resign(r)
        with self.assertRaises(ValueError): gate.verify_anchor_receipt(self.request, r)

    def test_rejects_persistent_service_account_key(self):
        r = copy.deepcopy(self.receipt); r["persistent_service_account_key_used"] = True; self._resign(r)
        with self.assertRaises(ValueError): gate.verify_anchor_receipt(self.request, r)

    def test_rejects_wrong_provider(self):
        r = copy.deepcopy(self.receipt); r["provider"] = "github-branch"; self._resign(r)
        with self.assertRaises(ValueError): gate.verify_anchor_receipt(self.request, r)

    def test_rejects_secret_field(self):
        r = copy.deepcopy(self.receipt); r["private_key"] = "forbidden"; self._resign(r)
        with self.assertRaises(ValueError): gate.verify_anchor_receipt(self.request, r)

    def test_rejects_tampered_receipt_digest(self):
        r = copy.deepcopy(self.receipt); r["object_id"] += "-tampered"
        with self.assertRaises(ValueError): gate.verify_anchor_receipt(self.request, r)

    def test_empty_ledger_fails_closed(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            empty = f.name
        with self.assertRaises(ValueError): gate.prepare_anchor_request(empty, "b" * 40)


if __name__ == "__main__":
    unittest.main()
