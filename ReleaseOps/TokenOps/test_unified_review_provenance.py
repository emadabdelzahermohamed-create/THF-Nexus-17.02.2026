#!/usr/bin/env python3
import hashlib
import json
import unittest

import evidence_artifact_binding
import github_evidence_metadata
import unified_review_provenance as mod

HEAD = "a" * 40
MANIFEST = "b" * 64
REVIEW_AT = "2026-09-12T15:00:00Z"
COMPLETED_AT = "2026-09-12T14:04:21Z"
RUN_ID = 4001
ARTIFACT_ID = 5001


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def atomic_record():
    core = {
        "version": 1,
        "record_type": "tokenops_atomic_commit_bound_simulation_review",
        "network": mod.NETWORK,
        "mint": mod.CANONICAL_MINT,
        "operation": "treasury_transfer",
        "manifest_sha256": MANIFEST,
        "anchored_approval_ledger_commit_sha256": "c" * 64,
        "final_ledger_head_sha256": "d" * 64,
        "ledger_entries_verified": 2,
        "source_head_sha": HEAD,
        "durable_approval_commit_verified": True,
        "exact_final_ledger_head_verified": True,
        "simulation_review_eligible": True,
        "simulation_execution_permitted": False,
        "execution_authorized": False,
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
    core["atomic_commit_bound_simulation_review_sha256"] = sha(core)
    return core


def freshness_record():
    core = {
        "version": 1,
        "network": mod.NETWORK,
        "mint": mod.CANONICAL_MINT,
        "source_head_sha": HEAD,
        "manifest_sha256": MANIFEST,
        "evidence_binding_sha256": "e" * 64,
        "evidence_bound_simulation_gate_sha256": "f" * 64,
        "review_at_utc": REVIEW_AT,
        "readonly_audit": {
            "workflow_run_id": RUN_ID,
            "artifact_id": ARTIFACT_ID,
            "head_sha": HEAD,
            "completed_at": COMPLETED_AT,
            "age_seconds": 3340,
            "max_age_seconds": 7200,
            "fresh": True,
        },
        "registry_compiler_gate": {
            "workflow_run_id": 4002,
            "artifact_id": 5002,
            "head_sha": HEAD,
            "completed_at": "2026-09-12T10:00:00Z",
            "age_seconds": 18000,
            "max_age_seconds": 86400,
            "fresh": True,
        },
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


def metadata_snapshot():
    run = {
        "id": RUN_ID,
        "name": "THF Token Read-Only Audit",
        "path": ".github/workflows/thf-token-readonly-audit.yml",
        "head_branch": evidence_artifact_binding.TOKENOPS_BRANCH,
        "head_sha": HEAD,
        "event": "push",
        "status": "completed",
        "conclusion": "success",
        "run_attempt": 1,
        "created_at": "2026-09-12T14:03:40Z",
        "run_started_at": "2026-09-12T14:03:40Z",
        "updated_at": COMPLETED_AT,
    }
    artifact = {
        "id": ARTIFACT_ID,
        "name": evidence_artifact_binding.READONLY_ARTIFACT_NAME,
        "size_in_bytes": 5152,
        "digest": "sha256:" + ("1" * 64),
        "expired": False,
        "created_at": "2026-09-12T14:04:19Z",
        "updated_at": "2026-09-12T14:04:19Z",
        "expires_at": "2026-10-12T14:04:19Z",
        "workflow_run": {
            "id": RUN_ID,
            "head_branch": evidence_artifact_binding.TOKENOPS_BRANCH,
            "head_sha": HEAD,
        },
    }
    return github_evidence_metadata.build(
        run, artifact, evidence_artifact_binding.READONLY_ARTIFACT_NAME,
        HEAD, REVIEW_AT,
    )


class UnifiedReviewProvenanceTests(unittest.TestCase):
    def inputs(self):
        return atomic_record(), freshness_record(), metadata_snapshot()

    def test_build_and_verify_review_only(self):
        atomic, fresh, meta = self.inputs()
        out = mod.build(atomic, fresh, meta, HEAD)
        self.assertTrue(mod.verify(out)["verified"])
        self.assertTrue(out["provenance_complete"])
        self.assertTrue(out["simulation_review_eligible"])
        self.assertFalse(out["simulation_execution_permitted"])
        self.assertFalse(out["execution_authorized"])
        self.assertFalse(out["transaction_created"])
        self.assertFalse(out["transaction_signed"])
        self.assertFalse(out["transaction_submitted"])
        self.assertFalse(out["broadcast_allowed"])
        self.assertFalse(out["financial_effect"])
        self.assertFalse(out["private_key_used"])
        self.assertFalse(out["wave_mawja_touched"])

    def test_manifest_mismatch_fails_closed(self):
        atomic, fresh, meta = self.inputs()
        fresh["manifest_sha256"] = "2" * 64
        fresh["evidence_freshness_gate_sha256"] = sha({k: v for k, v in fresh.items() if k != "evidence_freshness_gate_sha256"})
        with self.assertRaises(ValueError):
            mod.build(atomic, fresh, meta, HEAD)

    def test_readonly_run_mismatch_fails_closed(self):
        atomic, fresh, meta = self.inputs()
        fresh["readonly_audit"]["workflow_run_id"] += 1
        fresh["evidence_freshness_gate_sha256"] = sha({k: v for k, v in fresh.items() if k != "evidence_freshness_gate_sha256"})
        with self.assertRaises(ValueError):
            mod.build(atomic, fresh, meta, HEAD)

    def test_artifact_mismatch_fails_closed(self):
        atomic, fresh, meta = self.inputs()
        fresh["readonly_audit"]["artifact_id"] += 1
        fresh["evidence_freshness_gate_sha256"] = sha({k: v for k, v in fresh.items() if k != "evidence_freshness_gate_sha256"})
        with self.assertRaises(ValueError):
            mod.build(atomic, fresh, meta, HEAD)

    def test_source_head_mismatch_fails_closed(self):
        atomic, fresh, meta = self.inputs()
        with self.assertRaises(ValueError):
            mod.build(atomic, fresh, meta, "3" * 40)

    def test_metadata_tamper_fails_closed(self):
        atomic, fresh, meta = self.inputs()
        meta["artifact"]["artifact_sha256"] = "4" * 64
        with self.assertRaises(ValueError):
            mod.build(atomic, fresh, meta, HEAD)

    def test_secret_field_fails_closed(self):
        atomic, fresh, meta = self.inputs()
        meta["private_key"] = "forbidden"
        with self.assertRaises(ValueError):
            mod.build(atomic, fresh, meta, HEAD)

    def test_output_execution_flag_tamper_fails_closed(self):
        atomic, fresh, meta = self.inputs()
        out = mod.build(atomic, fresh, meta, HEAD)
        out["execution_authorized"] = True
        out["unified_review_provenance_sha256"] = sha({k: v for k, v in out.items() if k != "unified_review_provenance_sha256"})
        with self.assertRaises(ValueError):
            mod.verify(out)


if __name__ == "__main__":
    unittest.main()
