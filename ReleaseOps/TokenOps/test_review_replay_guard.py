#!/usr/bin/env python3
import hashlib
import json
import tempfile
import unittest

import audit_export
import evidence_freshness_gate
import github_evidence_metadata
import review_replay_guard as guardmod

HEAD = "a" * 40
MINT = evidence_freshness_gate.CANONICAL_MINT
BRANCH = github_evidence_metadata.TOKENOPS_BRANCH


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def fresh_gate():
    core = {
        "version": 1,
        "network": evidence_freshness_gate.NETWORK,
        "mint": MINT,
        "source_head_sha": HEAD,
        "manifest_sha256": "b" * 64,
        "evidence_binding_sha256": "c" * 64,
        "evidence_bound_simulation_gate_sha256": "d" * 64,
        "review_at_utc": "2026-09-12T15:00:00Z",
        "readonly_audit": {"workflow_run_id": 101, "artifact_id": 201, "head_sha": HEAD, "completed_at": "2026-09-12T14:30:00Z", "age_seconds": 1800, "max_age_seconds": 7200, "fresh": True},
        "registry_compiler_gate": {"workflow_run_id": 102, "artifact_id": 202, "head_sha": HEAD, "completed_at": "2026-09-12T13:00:00Z", "age_seconds": 7200, "max_age_seconds": 86400, "fresh": True},
        "evidence_fresh": True,
        "simulation_review_eligible": True,
        "simulation_execution_permitted": False,
        "transaction_created": False,
        "transaction_serialized": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "broadcast_allowed": False,
        "financial_effect": False,
        "external_signer_required_for_execution": True,
        "user_controlled_approval_required_for_execution": True,
        "private_key_used": False,
        "wave_mawja_touched": False,
    }
    core["evidence_freshness_gate_sha256"] = sha(core)
    return core


def metadata(run_id, artifact_id, name):
    run = {
        "id": run_id, "name": name, "path": f".github/workflows/{name}.yml",
        "head_branch": BRANCH, "head_sha": HEAD, "event": "push",
        "status": "completed", "conclusion": "success", "run_attempt": 1,
        "created_at": "2026-09-12T14:00:00Z",
        "run_started_at": "2026-09-12T14:01:00Z",
        "updated_at": "2026-09-12T14:10:00Z",
    }
    artifact = {
        "id": artifact_id, "name": name, "size_in_bytes": 1234,
        "digest": "sha256:" + ("%064x" % artifact_id)[-64:],
        "expired": False, "created_at": "2026-09-12T14:11:00Z",
        "updated_at": "2026-09-12T14:11:00Z",
        "expires_at": "2026-12-11T14:11:00Z",
        "workflow_run": {"id": run_id, "head_branch": BRANCH, "head_sha": HEAD},
    }
    return github_evidence_metadata.build(run, artifact, name, HEAD, "2026-09-12T14:20:00Z")


class ReplayGuardTests(unittest.TestCase):
    def snaps(self):
        return [metadata(101, 201, "readonly"), metadata(102, 202, "control")]

    def test_prepare_and_consume_once(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp:
            g = guardmod.prepare(fresh_gate(), self.snaps(), tmp.name, "GENESIS")
            self.assertTrue(g["simulation_review_eligible"])
            self.assertFalse(g["simulation_execution_permitted"])
            entry = guardmod.consume(g, tmp.name, "GENESIS", created_at=100)
            self.assertEqual(entry["sequence"], 1)
            self.assertTrue(audit_export.verify(tmp.name)["verified"])
            with self.assertRaises(ValueError):
                guardmod.prepare(fresh_gate(), self.snaps(), tmp.name, entry["entry_hash"])

    def test_duplicate_consume_fails_closed(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp:
            g = guardmod.prepare(fresh_gate(), self.snaps(), tmp.name, "GENESIS")
            guardmod.consume(g, tmp.name, "GENESIS", created_at=100)
            with self.assertRaises(ValueError):
                guardmod.consume(g, tmp.name, "GENESIS", created_at=101)

    def test_wrong_prior_head_detects_rollback_or_stale_state(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp:
            with self.assertRaises(ValueError):
                guardmod.prepare(fresh_gate(), self.snaps(), tmp.name, "f" * 64)

    def test_metadata_workflow_mismatch_fails_closed(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp:
            snaps = self.snaps()
            snaps[1] = metadata(999, 202, "control")
            with self.assertRaises(ValueError):
                guardmod.prepare(fresh_gate(), snaps, tmp.name, "GENESIS")

    def test_tampered_metadata_fails_closed(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp:
            snaps = self.snaps()
            snaps[0]["artifact"]["artifact_id"] = 999
            with self.assertRaises(ValueError):
                guardmod.prepare(fresh_gate(), snaps, tmp.name, "GENESIS")

    def test_secret_field_fails_closed(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp:
            fg = fresh_gate()
            fg["seed_phrase"] = "forbidden"
            with self.assertRaises(ValueError):
                guardmod.prepare(fg, self.snaps(), tmp.name, "GENESIS")


if __name__ == "__main__":
    unittest.main()
