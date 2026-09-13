#!/usr/bin/env python3
"""Fail-closed freshness gate for THF TokenOps simulation-review evidence.

This module is non-executing. It validates that an already verified evidence-bound
simulation-review gate is backed by successful GitHub workflow runs whose immutable
run IDs/head SHA match the evidence binding and whose completion timestamps are
within explicit age limits. It never creates, serializes, signs, submits, broadcasts,
or simulates a Solana transaction.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from typing import Any, Dict

import evidence_artifact_binding
import evidence_bound_simulation_gate

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK = "solana-mainnet-beta"
TOKENOPS_BRANCH = evidence_artifact_binding.TOKENOPS_BRANCH
READONLY_MAX_AGE_SECONDS = 2 * 60 * 60
CONTROL_MAX_AGE_SECONDS = 24 * 60 * 60
MAX_FUTURE_SKEW_SECONDS = 5 * 60
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_FIELDS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "raw_transaction", "serialized_transaction",
}


def _canonical_sha256(value: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


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


def _hex64(value: Any, name: str) -> str:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise ValueError(f"{name} must be lowercase 64-hex")
    return value


def _parse_utc(value: Any, name: str) -> dt.datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{name} must be an RFC3339 UTC timestamp ending in Z")
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(f"invalid {name}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != dt.timedelta(0):
        raise ValueError(f"{name} must be UTC")
    return parsed


def _validate_run(meta: Dict[str, Any], bound: Dict[str, Any], source_head_sha: str,
                  review_at: dt.datetime, max_age_seconds: int, label: str) -> Dict[str, Any]:
    _reject_secrets(meta)
    if meta.get("workflow_run_id") != bound.get("workflow_run_id"):
        raise ValueError(f"{label} workflow run ID mismatch")
    if meta.get("head_sha") != source_head_sha or meta.get("branch") != TOKENOPS_BRANCH:
        raise ValueError(f"{label} source mismatch")
    if meta.get("status") != "completed" or meta.get("conclusion") != "success":
        raise ValueError(f"{label} workflow must be completed successfully")
    completed_at = _parse_utc(meta.get("completed_at"), f"{label}.completed_at")
    age_seconds = int((review_at - completed_at).total_seconds())
    if age_seconds < -MAX_FUTURE_SKEW_SECONDS:
        raise ValueError(f"{label} completion time is too far in the future")
    effective_age = max(0, age_seconds)
    if effective_age > max_age_seconds:
        raise ValueError(f"{label} evidence is stale")
    return {
        "workflow_run_id": bound["workflow_run_id"],
        "artifact_id": bound["artifact_id"],
        "head_sha": source_head_sha,
        "completed_at": meta["completed_at"],
        "age_seconds": effective_age,
        "max_age_seconds": max_age_seconds,
        "fresh": True,
    }


def build(simulation_gate: Dict[str, Any], evidence_binding: Dict[str, Any],
          workflow_metadata: Dict[str, Any], review_at_utc: str) -> Dict[str, Any]:
    request = {
        "simulation_gate": simulation_gate,
        "evidence_binding": evidence_binding,
        "workflow_metadata": workflow_metadata,
        "review_at_utc": review_at_utc,
    }
    _reject_secrets(request)
    evidence_bound_simulation_gate.verify(simulation_gate)
    evidence_verification = evidence_artifact_binding.verify(evidence_binding)
    evidence_sha = _hex64(evidence_verification["evidence_binding_sha256"], "evidence_binding_sha256")
    if simulation_gate.get("evidence_binding_sha256") != evidence_sha:
        raise ValueError("simulation gate evidence binding mismatch")
    if simulation_gate.get("network") != NETWORK or simulation_gate.get("mint") != CANONICAL_MINT:
        raise ValueError("canonical scope mismatch")
    source_head_sha = evidence_binding.get("source_head_sha")
    if simulation_gate.get("source_head_sha") != source_head_sha:
        raise ValueError("source head mismatch")
    review_at = _parse_utc(review_at_utc, "review_at_utc")

    readonly = _validate_run(
        workflow_metadata.get("readonly_audit") or {}, evidence_binding.get("readonly_audit") or {},
        source_head_sha, review_at, READONLY_MAX_AGE_SECONDS, "readonly_audit",
    )
    control = _validate_run(
        workflow_metadata.get("registry_compiler_gate") or {}, evidence_binding.get("registry_compiler_gate") or {},
        source_head_sha, review_at, CONTROL_MAX_AGE_SECONDS, "registry_compiler_gate",
    )

    core = {
        "version": 1,
        "network": NETWORK,
        "mint": CANONICAL_MINT,
        "source_head_sha": source_head_sha,
        "manifest_sha256": _hex64(simulation_gate.get("manifest_sha256"), "manifest_sha256"),
        "evidence_binding_sha256": evidence_sha,
        "evidence_bound_simulation_gate_sha256": _hex64(
            simulation_gate.get("evidence_bound_simulation_gate_sha256"),
            "evidence_bound_simulation_gate_sha256",
        ),
        "review_at_utc": review_at_utc,
        "readonly_audit": readonly,
        "registry_compiler_gate": control,
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
    core["evidence_freshness_gate_sha256"] = _canonical_sha256(core)
    return core


def verify(gate: Dict[str, Any]) -> Dict[str, Any]:
    _reject_secrets(gate)
    supplied = _hex64(gate.get("evidence_freshness_gate_sha256"), "evidence_freshness_gate_sha256")
    core = dict(gate)
    core.pop("evidence_freshness_gate_sha256", None)
    if _canonical_sha256(core) != supplied:
        raise ValueError("evidence freshness gate digest mismatch")
    if core.get("network") != NETWORK or core.get("mint") != CANONICAL_MINT:
        raise ValueError("canonical scope mismatch")
    if core.get("evidence_fresh") is not True or core.get("simulation_review_eligible") is not True:
        raise ValueError("fresh simulation-review eligibility missing")
    for item in (core.get("readonly_audit") or {}, core.get("registry_compiler_gate") or {}):
        if item.get("fresh") is not True or int(item.get("age_seconds", -1)) > int(item.get("max_age_seconds", -1)):
            raise ValueError("stale bound workflow evidence")
    for key in (
        "simulation_execution_permitted", "transaction_created", "transaction_serialized",
        "transaction_signed", "transaction_submitted", "broadcast_allowed", "financial_effect",
        "private_key_used", "wave_mawja_touched",
    ):
        if core.get(key) is not False:
            raise ValueError(f"unsafe freshness-gate flag: {key}")
    if core.get("external_signer_required_for_execution") is not True:
        raise ValueError("external signer requirement missing")
    if core.get("user_controlled_approval_required_for_execution") is not True:
        raise ValueError("user approval requirement missing")
    return {"verified": True, "evidence_freshness_gate_sha256": supplied}
