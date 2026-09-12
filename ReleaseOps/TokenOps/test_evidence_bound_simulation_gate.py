#!/usr/bin/env python3
import hashlib
import json
import unittest

import evidence_artifact_binding
import evidence_bound_simulation_gate as gate

HEAD = "a" * 40
REGISTRY_BINDING = "b" * 64

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
        "network": gate.NETWORK,
        "mint": gate.CANONICAL_MINT,
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
    digest_input = dict(core)
    core["manifest_sha256"] = hashlib.sha256(
        json.dumps(digest_input, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return core

class GateTests(unittest.TestCase):
    def test_happy_path_is_review_only(self):
        ev = evidence()
        out = gate.build(manifest(ev["evidence_binding_sha256"]), ev)
        self.assertTrue(out["simulation_review_eligible"])
        self.assertFalse(out["simulation_execution_permitted"])
        self.assertFalse(out["broadcast_allowed"])
        self.assertTrue(gate.verify(out)["verified"])

    def test_evidence_mismatch_fails_closed(self):
        ev = evidence()
        m = manifest("c" * 64)
        with self.assertRaises(ValueError):
            gate.build(m, ev)

    def test_tampered_evidence_fails_closed(self):
        ev = evidence()
        m = manifest(ev["evidence_binding_sha256"])
        ev["readonly_audit"]["artifact_id"] += 1
        with self.assertRaises(ValueError):
            gate.build(m, ev)

    def test_wrong_mint_fails_closed(self):
        ev = evidence()
        m = manifest(ev["evidence_binding_sha256"])
        m["mint"] = "not-the-canonical-mint"
        with self.assertRaises(ValueError):
            gate.build(m, ev)

    def test_execution_flags_fail_closed(self):
        ev = evidence()
        for key in ("transaction_created", "transaction_signed", "transaction_submitted", "broadcast_allowed"):
            m = manifest(ev["evidence_binding_sha256"])
            m[key] = True
            with self.assertRaises(ValueError, msg=key):
                gate.build(m, ev)

    def test_external_signer_boundary_required(self):
        ev = evidence()
        m = manifest(ev["evidence_binding_sha256"])
        m["external_signer_required"] = False
        with self.assertRaises(ValueError):
            gate.build(m, ev)

    def test_secret_fields_rejected_recursively(self):
        ev = evidence()
        m = manifest(ev["evidence_binding_sha256"])
        m["payload"]["private_key"] = "forbidden"
        with self.assertRaises(ValueError):
            gate.build(m, ev)

    def test_post_gate_tamper_detected(self):
        ev = evidence()
        out = gate.build(manifest(ev["evidence_binding_sha256"]), ev)
        out["operation"] = "burn"
        with self.assertRaises(ValueError):
            gate.verify(out)

if __name__ == "__main__":
    unittest.main()
