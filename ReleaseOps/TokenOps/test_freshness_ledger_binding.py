#!/usr/bin/env python3
import hashlib
import json
import tempfile
import unittest

import audit_export
import evidence_artifact_binding
import evidence_bound_simulation_gate
import evidence_freshness_gate
import freshness_ledger_binding as binding

HEAD = "a" * 40
REGISTRY_BINDING = "b" * 64
REVIEW_AT = "2026-09-12T13:30:00Z"


def artifact(name, artifact_id):
    return {
        "workflow_run_id": 1000 + artifact_id,
        "artifact_id": artifact_id,
        "name": name,
        "artifact_sha256": ("%064x" % artifact_id)[-64:],
        "branch": evidence_artifact_binding.TOKENOPS_BRANCH,
        "head_sha": HEAD,
        "expired": False,
    }


def build_inputs():
    ev = evidence_artifact_binding.build(
        artifact(evidence_artifact_binding.READONLY_ARTIFACT_NAME, 11),
        artifact(evidence_artifact_binding.CONTROL_ARTIFACT_NAME, 12),
        HEAD,
        REGISTRY_BINDING,
    )
    manifest = {
        "network": evidence_freshness_gate.NETWORK,
        "mint": evidence_freshness_gate.CANONICAL_MINT,
        "operation": "treasury_transfer",
        "payload": {"amount_raw": "100000000", "destination": "11111111111111111111111111111111"},
        "evidence_binding_sha256": ev["evidence_binding_sha256"],
        "transaction_created": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "broadcast_allowed": False,
        "financial_effect": False,
        "external_signer_required": True,
        "approvals": [],
    }
    manifest["manifest_sha256"] = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    sim_gate = evidence_bound_simulation_gate.build(manifest, ev)
    metadata = {
        "readonly_audit": {
            "workflow_run_id": ev["readonly_audit"]["workflow_run_id"],
            "head_sha": HEAD,
            "branch": evidence_artifact_binding.TOKENOPS_BRANCH,
            "status": "completed",
            "conclusion": "success",
            "completed_at": "2026-09-12T12:45:00Z",
        },
        "registry_compiler_gate": {
            "workflow_run_id": ev["registry_compiler_gate"]["workflow_run_id"],
            "head_sha": HEAD,
            "branch": evidence_artifact_binding.TOKENOPS_BRANCH,
            "status": "completed",
            "conclusion": "success",
            "completed_at": "2026-09-12T10:00:00Z",
        },
    }
    fresh_gate = evidence_freshness_gate.build(sim_gate, ev, metadata, REVIEW_AT)
    policy = {
        "network": evidence_freshness_gate.NETWORK,
        "mint": evidence_freshness_gate.CANONICAL_MINT,
        "approval_classes": {"treasury_transfer": {"minimum_approvals": 2}},
    }
    return manifest, fresh_gate, policy


class LedgerBindingTests(unittest.TestCase):
    def test_approval_record_binds_freshness_without_execution(self):
        manifest, fresh_gate, policy = build_inputs()
        out = binding.build_approval_record(manifest, policy, fresh_gate)
        self.assertTrue(out["evidence_fresh"])
        self.assertTrue(out["simulation_review_eligible"])
        self.assertFalse(out["simulation_execution_permitted"])
        self.assertFalse(out["execution_authorized"])
        self.assertFalse(out["broadcast_allowed"])
        self.assertEqual(out["evidence_freshness_gate_sha256"], fresh_gate["evidence_freshness_gate_sha256"])

    def test_audit_record_is_append_only_and_verifiable(self):
        manifest, fresh_gate, _ = build_inputs()
        with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp:
            first = binding.append_audit_record(manifest, fresh_gate, tmp.name, created_at=100)
            second = binding.append_audit_record(manifest, fresh_gate, tmp.name, created_at=101)
            self.assertEqual(first["sequence"], 1)
            self.assertEqual(second["sequence"], 2)
            verified = audit_export.verify(tmp.name)
            self.assertTrue(verified["verified"])
            self.assertEqual(verified["entries"], 2)

    def test_manifest_mismatch_fails_closed(self):
        manifest, fresh_gate, policy = build_inputs()
        manifest["manifest_sha256"] = "c" * 64
        with self.assertRaises(ValueError):
            binding.build_approval_record(manifest, policy, fresh_gate)

    def test_tampered_freshness_gate_fails_closed(self):
        manifest, fresh_gate, policy = build_inputs()
        fresh_gate["evidence_fresh"] = False
        with self.assertRaises(ValueError):
            binding.build_approval_record(manifest, policy, fresh_gate)

    def test_secret_field_fails_closed(self):
        manifest, fresh_gate, policy = build_inputs()
        manifest["payload"]["seed_phrase"] = "forbidden"
        with self.assertRaises(ValueError):
            binding.build_approval_record(manifest, policy, fresh_gate)


if __name__ == "__main__":
    unittest.main()
