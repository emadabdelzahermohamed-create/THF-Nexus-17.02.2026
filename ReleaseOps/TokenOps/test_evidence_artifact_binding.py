#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

from audit_export import append_entry, verify as verify_audit
from evidence_artifact_binding import build, verify

HEAD = "32485bff4c6a07f869793160e5e3318f3a940f8d"
REGISTRY_BINDING = "1" * 64
READONLY_DIGEST = "a52d171227b1c2edef369537e82926532f3d0d6a9432532f582c0aaf973b2a30"
CONTROL_DIGEST = "6e39ca43e5244e2bbf8d1b7b829951c2fc4f49249a17a77b175aa95b1106b995"


def readonly_ref():
    return {
        "workflow_run_id": 34689968467,
        "artifact_id": 10296697770,
        "name": "THF-Token-ReadOnly-Audit",
        "artifact_sha256": READONLY_DIGEST,
        "branch": "tokenops/read-only-audit-20260911",
        "head_sha": HEAD,
        "expired": False,
    }


def control_ref():
    return {
        "workflow_run_id": 34689968491,
        "artifact_id": 10297132067,
        "name": "THF-TokenOps-Registry-Compiler-Binding-Gate",
        "artifact_sha256": "sha256:" + CONTROL_DIGEST,
        "branch": "tokenops/read-only-audit-20260911",
        "head_sha": HEAD,
        "expired": False,
    }


class EvidenceArtifactBindingTests(unittest.TestCase):
    def test_build_verify_and_append_to_audit_chain(self):
        binding = build(readonly_ref(), control_ref(), HEAD, REGISTRY_BINDING)
        self.assertTrue(verify(binding)["verified"])
        self.assertFalse(binding["transaction_created"])
        self.assertFalse(binding["transaction_signed"])
        self.assertFalse(binding["transaction_submitted"])
        self.assertFalse(binding["broadcast_allowed"])
        self.assertFalse(binding["financial_effect"])
        self.assertFalse(binding["private_key_used"])
        self.assertFalse(binding["wave_mawja_touched"])
        with tempfile.TemporaryDirectory() as td:
            ledger = Path(td) / "audit.jsonl"
            entry = append_entry(binding, ledger, created_at=1)
            result = verify_audit(ledger)
            self.assertTrue(result["verified"])
            self.assertEqual(result["entries"], 1)
            self.assertEqual(entry["event"]["evidence_binding_sha256"], binding["evidence_binding_sha256"])

    def test_rejects_head_mismatch(self):
        ref = readonly_ref(); ref["head_sha"] = "0" * 40
        with self.assertRaises(ValueError):
            build(ref, control_ref(), HEAD, REGISTRY_BINDING)

    def test_rejects_wrong_artifact_name(self):
        ref = control_ref(); ref["name"] = "not-tokenops"
        with self.assertRaises(ValueError):
            build(readonly_ref(), ref, HEAD, REGISTRY_BINDING)

    def test_rejects_expired_artifact(self):
        ref = readonly_ref(); ref["expired"] = True
        with self.assertRaises(ValueError):
            build(ref, control_ref(), HEAD, REGISTRY_BINDING)

    def test_rejects_invalid_digest(self):
        ref = readonly_ref(); ref["artifact_sha256"] = "bad"
        with self.assertRaises(ValueError):
            build(ref, control_ref(), HEAD, REGISTRY_BINDING)

    def test_rejects_secret_fields_recursively(self):
        ref = readonly_ref(); ref["nested"] = {"private_key": "forbidden"}
        with self.assertRaises(ValueError):
            build(ref, control_ref(), HEAD, REGISTRY_BINDING)

    def test_verify_rejects_tampering(self):
        binding = build(readonly_ref(), control_ref(), HEAD, REGISTRY_BINDING)
        binding["financial_effect"] = True
        with self.assertRaises(ValueError):
            verify(binding)


if __name__ == "__main__":
    unittest.main()
