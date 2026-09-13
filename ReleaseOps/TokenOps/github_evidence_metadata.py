#!/usr/bin/env python3
"""Canonical GitHub metadata snapshot for THF TokenOps review evidence.

This module is deliberately offline and non-executing. It validates public GitHub
Actions run/artifact metadata, binds immutable identifiers and timestamps into one
canonical digest, and preserves the TokenOps safety boundary. It never creates,
serializes, simulates, signs, submits, or broadcasts a Solana transaction.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from typing import Any, Dict

import evidence_artifact_binding

CANONICAL_MINT = evidence_artifact_binding.CANONICAL_MINT
NETWORK = evidence_artifact_binding.NETWORK
TOKENOPS_BRANCH = evidence_artifact_binding.TOKENOPS_BRANCH
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_FIELDS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "raw_transaction", "serialized_transaction",
}


def _canonical_sha256(value: Dict[str, Any]) -> str:
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


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _hex40(value: Any, name: str) -> str:
    if not isinstance(value, str) or not HEX40.fullmatch(value):
        raise ValueError(f"{name} must be lowercase 40-hex")
    return value


def _hex64(value: Any, name: str) -> str:
    if isinstance(value, str) and value.startswith("sha256:"):
        value = value[7:]
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise ValueError(f"{name} must be lowercase 64-hex")
    return value


def _utc(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{name} must be RFC3339 UTC ending in Z")
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(f"invalid {name}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != dt.timedelta(0):
        raise ValueError(f"{name} must be UTC")
    return parsed.isoformat().replace("+00:00", "Z")


def _run(run: Dict[str, Any], source_head_sha: str) -> Dict[str, Any]:
    _reject_secrets(run)
    if run.get("head_branch") != TOKENOPS_BRANCH:
        raise ValueError("workflow branch mismatch")
    if run.get("head_sha") != source_head_sha:
        raise ValueError("workflow head SHA mismatch")
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        raise ValueError("workflow run must be completed successfully")
    event = run.get("event")
    if event not in {"push", "workflow_dispatch"}:
        raise ValueError("unexpected workflow event")
    return {
        "workflow_run_id": _positive_int(run.get("id"), "workflow_run_id"),
        "workflow_name": str(run.get("name") or ""),
        "workflow_path": str(run.get("path") or ""),
        "head_branch": TOKENOPS_BRANCH,
        "head_sha": source_head_sha,
        "event": event,
        "status": "completed",
        "conclusion": "success",
        "run_attempt": _positive_int(run.get("run_attempt", 1), "run_attempt"),
        "created_at": _utc(run.get("created_at"), "run.created_at"),
        "run_started_at": _utc(run.get("run_started_at"), "run.run_started_at"),
        "completed_at": _utc(run.get("updated_at"), "run.updated_at"),
    }


def _artifact(artifact: Dict[str, Any], run_record: Dict[str, Any],
              expected_name: str, captured_at: dt.datetime) -> Dict[str, Any]:
    _reject_secrets(artifact)
    if artifact.get("name") != expected_name:
        raise ValueError("artifact name mismatch")
    workflow_run = artifact.get("workflow_run") or {}
    if workflow_run.get("id") != run_record["workflow_run_id"]:
        raise ValueError("artifact workflow run mismatch")
    if workflow_run.get("head_branch") != TOKENOPS_BRANCH:
        raise ValueError("artifact branch mismatch")
    if workflow_run.get("head_sha") != run_record["head_sha"]:
        raise ValueError("artifact head SHA mismatch")
    if artifact.get("expired") is not False:
        raise ValueError("expired evidence artifact")
    expires_at = _utc(artifact.get("expires_at"), "artifact.expires_at")
    expiry = dt.datetime.fromisoformat(expires_at[:-1] + "+00:00")
    if expiry <= captured_at:
        raise ValueError("artifact already expired at capture time")
    return {
        "artifact_id": _positive_int(artifact.get("id"), "artifact_id"),
        "name": expected_name,
        "size_in_bytes": _positive_int(artifact.get("size_in_bytes"), "size_in_bytes"),
        "artifact_sha256": _hex64(artifact.get("digest"), "artifact.digest"),
        "expired": False,
        "created_at": _utc(artifact.get("created_at"), "artifact.created_at"),
        "updated_at": _utc(artifact.get("updated_at"), "artifact.updated_at"),
        "expires_at": expires_at,
        "workflow_run_id": run_record["workflow_run_id"],
        "head_branch": TOKENOPS_BRANCH,
        "head_sha": run_record["head_sha"],
    }


def build(run: Dict[str, Any], artifact: Dict[str, Any], expected_artifact_name: str,
          source_head_sha: str, captured_at_utc: str) -> Dict[str, Any]:
    request = {
        "run": run,
        "artifact": artifact,
        "expected_artifact_name": expected_artifact_name,
        "source_head_sha": source_head_sha,
        "captured_at_utc": captured_at_utc,
    }
    _reject_secrets(request)
    source_head_sha = _hex40(source_head_sha, "source_head_sha")
    captured_at_text = _utc(captured_at_utc, "captured_at_utc")
    captured_at = dt.datetime.fromisoformat(captured_at_text[:-1] + "+00:00")
    run_record = _run(run, source_head_sha)
    artifact_record = _artifact(
        artifact, run_record, expected_artifact_name, captured_at
    )
    completed = dt.datetime.fromisoformat(run_record["completed_at"][:-1] + "+00:00")
    if completed > captured_at + dt.timedelta(minutes=5):
        raise ValueError("workflow completion is too far in the future")
    core = {
        "version": 1,
        "record_type": "tokenops_github_evidence_metadata_snapshot",
        "network": NETWORK,
        "mint": CANONICAL_MINT,
        "branch": TOKENOPS_BRANCH,
        "source_head_sha": source_head_sha,
        "captured_at_utc": captured_at_text,
        "workflow_run": run_record,
        "artifact": artifact_record,
        "transaction_created": False,
        "transaction_serialized": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "simulation_execution_permitted": False,
        "broadcast_allowed": False,
        "financial_effect": False,
        "private_key_used": False,
        "wave_mawja_touched": False,
    }
    core["github_evidence_metadata_sha256"] = _canonical_sha256(core)
    return core


def verify(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    _reject_secrets(snapshot)
    supplied = _hex64(
        snapshot.get("github_evidence_metadata_sha256"),
        "github_evidence_metadata_sha256",
    )
    core = dict(snapshot)
    core.pop("github_evidence_metadata_sha256", None)
    if _canonical_sha256(core) != supplied:
        raise ValueError("GitHub evidence metadata digest mismatch")
    if core.get("network") != NETWORK or core.get("mint") != CANONICAL_MINT:
        raise ValueError("canonical scope mismatch")
    if core.get("branch") != TOKENOPS_BRANCH:
        raise ValueError("TokenOps branch mismatch")
    if core.get("source_head_sha") != (core.get("workflow_run") or {}).get("head_sha"):
        raise ValueError("workflow source mismatch")
    if core.get("source_head_sha") != (core.get("artifact") or {}).get("head_sha"):
        raise ValueError("artifact source mismatch")
    if (core.get("workflow_run") or {}).get("workflow_run_id") != (core.get("artifact") or {}).get("workflow_run_id"):
        raise ValueError("run/artifact identifier mismatch")
    for key in (
        "transaction_created", "transaction_serialized", "transaction_signed",
        "transaction_submitted", "simulation_execution_permitted",
        "broadcast_allowed", "financial_effect", "private_key_used",
        "wave_mawja_touched",
    ):
        if core.get(key) is not False:
            raise ValueError(f"unsafe metadata snapshot flag: {key}")
    return {"verified": True, "github_evidence_metadata_sha256": supplied}
