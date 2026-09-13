#!/usr/bin/env python3
"""Unified fail-closed provenance envelope for THF TokenOps simulation review.

Review-only control plane. This module binds an already verified atomic ledger
approval, freshness gate, and GitHub read-only-audit metadata snapshot to one
canonical digest. It never creates, serializes, simulates, signs, submits,
broadcasts, transfers, burns, changes authorities, settles rewards/vesting,
migrates treasury, or executes DAO decisions.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict

import atomic_commit_bound_simulation_review as atomic_review
import evidence_artifact_binding
import evidence_freshness_gate as freshness
import github_evidence_metadata as github_metadata

CANONICAL_MINT = evidence_artifact_binding.CANONICAL_MINT
NETWORK = evidence_artifact_binding.NETWORK
TOKENOPS_BRANCH = evidence_artifact_binding.TOKENOPS_BRANCH
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_FIELDS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "raw_transaction", "serialized_transaction",
}


def _sha(value: Dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _reject_secrets(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_FIELDS:
                raise ValueError(f"forbidden secret/signature field: {key}")
            _reject_secrets(item)
    elif isinstance(value, list):
        for item in value:
            _reject_secrets(item)


def _hex40(value: Any, name: str) -> str:
    if not isinstance(value, str) or not HEX40.fullmatch(value):
        raise ValueError(f"{name} must be lowercase 40-hex")
    return value


def _hex64(value: Any, name: str) -> str:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise ValueError(f"{name} must be lowercase 64-hex")
    return value


def build(atomic_record: Dict[str, Any], freshness_record: Dict[str, Any],
          github_snapshot: Dict[str, Any], expected_source_head_sha: str) -> Dict[str, Any]:
    request = {
        "atomic_record": atomic_record,
        "freshness_record": freshness_record,
        "github_snapshot": github_snapshot,
        "expected_source_head_sha": expected_source_head_sha,
    }
    _reject_secrets(request)
    source_head = _hex40(expected_source_head_sha, "expected_source_head_sha")

    atomic_verified = atomic_review.verify(atomic_record)
    freshness_verified = freshness.verify(freshness_record)
    metadata_verified = github_metadata.verify(github_snapshot)

    for label, record in (
        ("atomic review", atomic_record),
        ("freshness gate", freshness_record),
        ("GitHub metadata", github_snapshot),
    ):
        if record.get("network") != NETWORK or record.get("mint") != CANONICAL_MINT:
            raise ValueError(f"{label} canonical scope mismatch")
        if record.get("source_head_sha") != source_head:
            raise ValueError(f"{label} source head mismatch")

    if github_snapshot.get("branch") != TOKENOPS_BRANCH:
        raise ValueError("GitHub metadata TokenOps branch mismatch")

    manifest_sha = _hex64(atomic_record.get("manifest_sha256"), "manifest_sha256")
    if freshness_record.get("manifest_sha256") != manifest_sha:
        raise ValueError("freshness gate manifest does not match durable atomic approval")

    readonly = freshness_record.get("readonly_audit") or {}
    run = github_snapshot.get("workflow_run") or {}
    artifact = github_snapshot.get("artifact") or {}
    if run.get("workflow_run_id") != readonly.get("workflow_run_id"):
        raise ValueError("GitHub metadata run is not the freshness-bound read-only audit")
    if artifact.get("artifact_id") != readonly.get("artifact_id"):
        raise ValueError("GitHub metadata artifact is not the freshness-bound read-only audit artifact")
    if artifact.get("name") != evidence_artifact_binding.READONLY_ARTIFACT_NAME:
        raise ValueError("unexpected read-only audit artifact name")
    if run.get("completed_at") != readonly.get("completed_at"):
        raise ValueError("GitHub metadata completion time differs from freshness evidence")
    if run.get("head_sha") != source_head or artifact.get("head_sha") != source_head:
        raise ValueError("GitHub run/artifact source head mismatch")

    if atomic_record.get("simulation_review_eligible") is not True:
        raise ValueError("atomic review eligibility missing")
    if freshness_record.get("simulation_review_eligible") is not True:
        raise ValueError("fresh review eligibility missing")

    core = {
        "version": 1,
        "record_type": "tokenops_unified_review_provenance_envelope",
        "network": NETWORK,
        "mint": CANONICAL_MINT,
        "branch": TOKENOPS_BRANCH,
        "source_head_sha": source_head,
        "manifest_sha256": manifest_sha,
        "atomic_commit_bound_simulation_review_sha256": _hex64(
            atomic_verified["atomic_commit_bound_simulation_review_sha256"],
            "atomic_commit_bound_simulation_review_sha256",
        ),
        "anchored_approval_ledger_commit_sha256": _hex64(
            atomic_record.get("anchored_approval_ledger_commit_sha256"),
            "anchored_approval_ledger_commit_sha256",
        ),
        "final_ledger_head_sha256": _hex64(
            atomic_record.get("final_ledger_head_sha256"),
            "final_ledger_head_sha256",
        ),
        "evidence_freshness_gate_sha256": _hex64(
            freshness_verified["evidence_freshness_gate_sha256"],
            "evidence_freshness_gate_sha256",
        ),
        "github_evidence_metadata_sha256": _hex64(
            metadata_verified["github_evidence_metadata_sha256"],
            "github_evidence_metadata_sha256",
        ),
        "readonly_audit_workflow_run_id": run["workflow_run_id"],
        "readonly_audit_artifact_id": artifact["artifact_id"],
        "readonly_audit_artifact_sha256": _hex64(
            artifact.get("artifact_sha256"), "readonly_audit_artifact_sha256"
        ),
        "review_at_utc": freshness_record.get("review_at_utc"),
        "provenance_complete": True,
        "durable_approval_commit_verified": True,
        "freshness_verified": True,
        "github_artifact_provenance_verified": True,
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
    core["unified_review_provenance_sha256"] = _sha(core)
    return core


def verify(envelope: Dict[str, Any]) -> Dict[str, Any]:
    _reject_secrets(envelope)
    supplied = _hex64(
        envelope.get("unified_review_provenance_sha256"),
        "unified_review_provenance_sha256",
    )
    core = dict(envelope)
    core.pop("unified_review_provenance_sha256", None)
    if _sha(core) != supplied:
        raise ValueError("unified review provenance digest mismatch")
    if core.get("record_type") != "tokenops_unified_review_provenance_envelope":
        raise ValueError("unexpected provenance record type")
    if core.get("network") != NETWORK or core.get("mint") != CANONICAL_MINT:
        raise ValueError("canonical scope mismatch")
    if core.get("branch") != TOKENOPS_BRANCH:
        raise ValueError("TokenOps branch mismatch")
    _hex40(core.get("source_head_sha"), "source_head_sha")
    for key in (
        "manifest_sha256", "atomic_commit_bound_simulation_review_sha256",
        "anchored_approval_ledger_commit_sha256", "final_ledger_head_sha256",
        "evidence_freshness_gate_sha256", "github_evidence_metadata_sha256",
        "readonly_audit_artifact_sha256",
    ):
        _hex64(core.get(key), key)
    for key in (
        "provenance_complete", "durable_approval_commit_verified",
        "freshness_verified", "github_artifact_provenance_verified",
        "simulation_review_eligible",
    ):
        if core.get(key) is not True:
            raise ValueError(f"required provenance control missing: {key}")
    for key in (
        "simulation_execution_permitted", "execution_authorized", "transaction_created",
        "transaction_serialized", "transaction_signed", "transaction_submitted",
        "broadcast_allowed", "financial_effect", "private_key_used", "wave_mawja_touched",
    ):
        if core.get(key) is not False:
            raise ValueError(f"unsafe provenance flag: {key}")
    if core.get("external_signer_required_for_execution") is not True:
        raise ValueError("external signer boundary missing")
    if core.get("user_controlled_approval_required_for_execution") is not True:
        raise ValueError("user-controlled approval boundary missing")
    return {"verified": True, "unified_review_provenance_sha256": supplied}
