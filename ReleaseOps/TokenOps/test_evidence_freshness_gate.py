#!/usr/bin/env python3
import datetime as dt
import hashlib
import json
import unittest

import evidence_artifact_binding
import evidence_bound_simulation_gate
import evidence_freshness_gate as freshness

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


def evidence():
    return evidence_artifact_binding.build(
        artifact(evidence_artifact_binding.READONLY_ARTIFACT_NAME, 11),
        artifact(evidence_artifact_binding.CONTROL_ARTIFACT_NAME, 12),
        HEAD,
        REGISTRY_BINDING,
    )


def manifest(evidence_sha):
    core = {
        "network": freshness.NETWORK,
        "mint": freshness.CANONICAL_MINT,
        "operation": "treasury_transfer",
        "payload": {"amount_raw": "100000000", "destination": "11111111111111111111111111111111"},
        "evidence_binding_sha256": evidence_sha,
        "transaction_created": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "broadcast_allowed": False,
        "financial_effect": False,
        "external_signer_required": True,
    }
    core["manifest_sha256"] = hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return core


def inputs():
    ev = evidence()
    sim_gate = evidence_bound_simulation_gate.build(manifest(ev["evidence_binding_sha256"]), ev)
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
    return ev, sim_gate, metadata


class FreshnessGateTests(unittest.TestCase):
    def test_fresh_evidence_is_review_only(self):
        ev, sim_gate, metadata = inputs()
        out = freshness.build(sim_gate, ev, metadata, REVIEW_AT)
        self.assertTrue(out["evidence_fresh"])
        self.assertTrue(out["simulation_review_eligible"])
        self.assertFalse(out["simulation_execution_permitted"])
        self.assertFalse(out["broadcast_allowed"])
        self.assertTrue(freshness.verify(out)["verified"])

    def test_stale_readonly_audit_fails_closed(self):
        ev, sim_gate, metadata = inputs()
        metadata["readonly_audit"]["completed_at"] = "2026-09-12T11:00:00Z"
        with self.assertRaises(ValueError):
            freshness.build(sim_gate, ev, metadata, REVIEW_AT)

    def test_stale_control_gate_fails_closed(self):
        ev, sim_gate, metadata = inputs()
        metadata["registry_compiler_gate"]["completed_at"] = "2026-09-11T12:00:00Z"
        with self.assertRaises(ValueError):
            freshness.build(sim_gate, ev, metadata, REVIEW_AT)

    def test_mismatched_run_id_fails_closed(self):
        ev, sim_gate, metadata = inputs()
        metadata["readonly_audit"]["workflow_run_id"] += 1
        with self.assertRaises(ValueError):
            freshness.build(sim_gate, ev, metadata, REVIEW_AT)

    def test_mismatched_head_fails_closed(self):
        ev, sim_gate, metadata = inputs()
        metadata["registry_compiler_gate"]["head_sha"] = "c" * 40
        with self.assertRaises(ValueError):
            freshness.build(sim_gate, ev, metadata, REVIEW_AT)

    def test_failed_workflow_fails_closed(self):
        ev, sim_gate, metadata = inputs()
        metadata["readonly_audit"]["conclusion"] = "failure"
        with self.assertRaises(ValueError):
            freshness.build(sim_gate, ev, metadata, REVIEW_AT)

    def test_future_timestamp_beyond_skew_fails_closed(self):
        ev, sim_gate, metadata = inputs()
        metadata["readonly_audit"]["completed_at"] = "2026-09-12T13:40:01Z"
        with self.assertRaises(ValueError):
            freshness.build(sim_gate, ev, metadata, REVIEW_AT)

    def test_secret_field_fails_closed(self):
        ev, sim_gate, metadata = inputs()
        metadata["readonly_audit"]["private_key"] = "forbidden"
        with self.assertRaises(ValueError):
            freshness.build(sim_gate, ev, metadata, REVIEW_AT)

    def test_tampered_output_fails_verification(self):
        ev, sim_gate, metadata = inputs()
        out = freshness.build(sim_gate, ev, metadata, REVIEW_AT)
        out["simulation_execution_permitted"] = True
        with self.assertRaises(ValueError):
            freshness.verify(out)


if __name__ == "__main__":
    unittest.main()
