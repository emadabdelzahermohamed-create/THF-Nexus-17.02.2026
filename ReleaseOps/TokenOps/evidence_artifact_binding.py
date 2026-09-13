#!/usr/bin/env python3
"""Bind immutable GitHub Actions evidence metadata into TokenOps audit events.

This module is deliberately offline and non-executing. It accepts only public
workflow/artifact identifiers and SHA-256 digests, validates that all evidence
belongs to the same TokenOps branch/head, then emits a canonical binding that
can be appended to audit_export's hash-chained JSONL ledger.

It never creates, serializes, signs, submits, or broadcasts a Solana transaction.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK = "solana-mainnet-beta"
TOKENOPS_BRANCH = "tokenops/read-only-audit-20260911"
READONLY_ARTIFACT_NAME = "THF-Token-ReadOnly-Audit"
CONTROL_ARTIFACT_NAME = "THF-TokenOps-Registry-Compiler-Binding-Gate"

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
FORBIDDEN_FIELDS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "raw_transaction", "serialized_transaction",
}


def _canonical_sha256(value: Dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


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


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _validate_artifact(ref: Dict[str, Any], expected_name: str, source_head_sha: str) -> Dict[str, Any]:
    _reject_secrets(ref)
    if ref.get("name") != expected_name:
        raise ValueError(f"unexpected artifact name: {ref.get('name')}")
    if ref.get("branch") != TOKENOPS_BRANCH:
        raise ValueError("artifact branch mismatch")
    if ref.get("head_sha") != source_head_sha:
        raise ValueError("artifact head SHA mismatch")
    digest = ref.get("artifact_sha256")
    if isinstance(digest, str) and digest.startswith("sha256:"):
        digest = digest[7:]
    return {
        "workflow_run_id": _positive_int(ref.get("workflow_run_id"), "workflow_run_id"),
        "artifact_id": _positive_int(ref.get("artifact_id"), "artifact_id"),
        "name": expected_name,
        "artifact_sha256": _hex64(digest, "artifact_sha256"),
        "branch": TOKENOPS_BRANCH,
        "head_sha": source_head_sha,
        "expired": bool(ref.get("expired", False)),
    }


def build(
    readonly_evidence: Dict[str, Any],
    control_gate_evidence: Dict[str, Any],
    source_head_sha: str,
    registry_compiler_binding_sha256: str,
) -> Dict[str, Any]:
    """Create a fail-closed evidence binding suitable for audit_export.append_entry."""
    request = {
        "readonly_evidence": readonly_evidence,
        "control_gate_evidence": control_gate_evidence,
        "source_head_sha": source_head_sha,
        "registry_compiler_binding_sha256": registry_compiler_binding_sha256,
    }
    _reject_secrets(request)
    if not isinstance(source_head_sha, str) or not HEX40.fullmatch(source_head_sha):
        raise ValueError("source_head_sha must be lowercase 40-hex")
    registry_binding = _hex64(registry_compiler_binding_sha256, "registry_compiler_binding_sha256")
    readonly = _validate_artifact(readonly_evidence, READONLY_ARTIFACT_NAME, source_head_sha)
    control = _validate_artifact(control_gate_evidence, CONTROL_ARTIFACT_NAME, source_head_sha)
    if readonly["expired"] or control["expired"]:
        raise ValueError("expired evidence artifact cannot establish a new binding")

    core = {
        "version": 1,
        "event_type": "tokenops_ci_evidence_binding",
        "network": NETWORK,
        "mint": CANONICAL_MINT,
        "branch": TOKENOPS_BRANCH,
        "source_head_sha": source_head_sha,
        "registry_compiler_binding_sha256": registry_binding,
        "readonly_audit": readonly,
        "registry_compiler_gate": control,
        "transaction_created": False,
        "transaction_serialized": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "broadcast_allowed": False,
        "financial_effect": False,
        "private_key_used": False,
        "wave_mawja_touched": False,
    }
    core["evidence_binding_sha256"] = _canonical_sha256(core)
    return core


def verify(binding: Dict[str, Any]) -> Dict[str, Any]:
    """Recompute the binding digest and reassert all safety invariants."""
    _reject_secrets(binding)
    supplied = _hex64(binding.get("evidence_binding_sha256"), "evidence_binding_sha256")
    core = dict(binding)
    core.pop("evidence_binding_sha256", None)
    if _canonical_sha256(core) != supplied:
        raise ValueError("evidence binding digest mismatch")
    if core.get("mint") != CANONICAL_MINT or core.get("network") != NETWORK:
        raise ValueError("canonical mint/network mismatch")
    if core.get("branch") != TOKENOPS_BRANCH:
        raise ValueError("TokenOps branch mismatch")
    for key in (
        "transaction_created", "transaction_serialized", "transaction_signed",
        "transaction_submitted", "broadcast_allowed", "financial_effect",
        "private_key_used", "wave_mawja_touched",
    ):
        if core.get(key) is not False:
            raise ValueError(f"unsafe evidence flag: {key}")
    return {"verified": True, "evidence_binding_sha256": supplied}
