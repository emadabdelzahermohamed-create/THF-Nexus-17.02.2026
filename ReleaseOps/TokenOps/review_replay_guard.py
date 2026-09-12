#!/usr/bin/env python3
"""One-time replay/rollback guard for THF TokenOps simulation-review evidence.

Review-only. This module never creates, serializes, simulates, signs, submits,
broadcasts, transfers, burns, or changes any Solana state.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any, Dict, Iterable

import audit_export
import evidence_freshness_gate
import github_evidence_metadata

FORBIDDEN_FIELDS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "raw_transaction", "serialized_transaction",
}
GENESIS = "GENESIS"


def _sha(value: Dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _reject(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_FIELDS:
                raise ValueError(f"forbidden secret/signature field: {key}")
            _reject(item)
    elif isinstance(value, list):
        for item in value:
            _reject(item)


def _ledger_entries(path: str) -> list[Dict[str, Any]]:
    p = pathlib.Path(path)
    if not p.exists() or not p.read_text().strip():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def _metadata_bundle(
    freshness_gate: Dict[str, Any],
    metadata_snapshots: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    snapshots = list(metadata_snapshots)
    if len(snapshots) != 2:
        raise ValueError("exactly two GitHub evidence metadata snapshots are required")
    expected_ids = {
        int((freshness_gate.get("readonly_audit") or {}).get("workflow_run_id", 0)),
        int((freshness_gate.get("registry_compiler_gate") or {}).get("workflow_run_id", 0)),
    }
    if 0 in expected_ids or len(expected_ids) != 2:
        raise ValueError("freshness gate workflow IDs are invalid or ambiguous")

    normalized = []
    observed_ids = set()
    for snap in snapshots:
        verified = github_evidence_metadata.verify(snap)
        if snap.get("source_head_sha") != freshness_gate.get("source_head_sha"):
            raise ValueError("GitHub metadata source head mismatch")
        run_id = int((snap.get("workflow_run") or {}).get("workflow_run_id", 0))
        observed_ids.add(run_id)
        normalized.append({
            "workflow_run_id": run_id,
            "artifact_id": int((snap.get("artifact") or {}).get("artifact_id", 0)),
            "github_evidence_metadata_sha256": verified["github_evidence_metadata_sha256"],
        })
    if observed_ids != expected_ids:
        raise ValueError("GitHub metadata workflow set does not match freshness evidence")
    normalized.sort(key=lambda item: item["workflow_run_id"])
    bundle = {"version": 1, "snapshots": normalized}
    bundle["github_metadata_bundle_sha256"] = _sha(bundle)
    return bundle


def prepare(
    freshness_gate: Dict[str, Any],
    metadata_snapshots: Iterable[Dict[str, Any]],
    ledger_path: str,
    expected_prior_ledger_head: str,
) -> Dict[str, Any]:
    snapshots = list(metadata_snapshots)
    _reject({
        "freshness_gate": freshness_gate,
        "metadata_snapshots": snapshots,
        "expected_prior_ledger_head": expected_prior_ledger_head,
    })
    verified = evidence_freshness_gate.verify(freshness_gate)
    ledger_state = audit_export.verify(ledger_path) if pathlib.Path(ledger_path).exists() else {
        "entries": 0, "head_hash": GENESIS, "verified": True
    }
    if ledger_state["head_hash"] != expected_prior_ledger_head:
        raise ValueError("prior ledger head mismatch; rollback or stale reviewer state")
    bundle = _metadata_bundle(freshness_gate, snapshots)
    token_core = {
        "version": 1,
        "network": freshness_gate.get("network"),
        "mint": freshness_gate.get("mint"),
        "source_head_sha": freshness_gate.get("source_head_sha"),
        "manifest_sha256": freshness_gate.get("manifest_sha256"),
        "evidence_freshness_gate_sha256": verified["evidence_freshness_gate_sha256"],
        "github_metadata_bundle_sha256": bundle["github_metadata_bundle_sha256"],
    }
    replay_token = _sha(token_core)
    for entry in _ledger_entries(ledger_path):
        event = entry.get("event") or {}
        if event.get("review_replay_token_sha256") == replay_token:
            raise ValueError("review replay token already consumed")

    out = dict(token_core)
    out.update({
        "record_type": "tokenops_review_replay_guard",
        "prior_ledger_head": expected_prior_ledger_head,
        "review_replay_token_sha256": replay_token,
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
    })
    out["review_replay_guard_sha256"] = _sha(out)
    return out


def consume(
    guard: Dict[str, Any],
    ledger_path: str,
    expected_prior_ledger_head: str,
    created_at: int | None = None,
) -> Dict[str, Any]:
    _reject(guard)
    supplied = guard.get("review_replay_guard_sha256")
    core = dict(guard)
    core.pop("review_replay_guard_sha256", None)
    if not isinstance(supplied, str) or _sha(core) != supplied:
        raise ValueError("review replay guard digest mismatch")
    if guard.get("prior_ledger_head") != expected_prior_ledger_head:
        raise ValueError("guard prior ledger head mismatch")
    state = audit_export.verify(ledger_path) if pathlib.Path(ledger_path).exists() else {
        "entries": 0, "head_hash": GENESIS, "verified": True
    }
    if state["head_hash"] != expected_prior_ledger_head:
        raise ValueError("ledger advanced or rolled back since guard preparation")
    token = guard.get("review_replay_token_sha256")
    for entry in _ledger_entries(ledger_path):
        if (entry.get("event") or {}).get("review_replay_token_sha256") == token:
            raise ValueError("review replay token already consumed")
    event = {
        "version": 1,
        "event_type": "tokenops_review_replay_token_consumed",
        "network": guard.get("network"),
        "mint": guard.get("mint"),
        "source_head_sha": guard.get("source_head_sha"),
        "manifest_sha256": guard.get("manifest_sha256"),
        "evidence_freshness_gate_sha256": guard.get("evidence_freshness_gate_sha256"),
        "github_metadata_bundle_sha256": guard.get("github_metadata_bundle_sha256"),
        "review_replay_token_sha256": token,
        "expected_prior_ledger_head": expected_prior_ledger_head,
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
    return audit_export.append_entry(event, ledger_path, created_at=created_at)
