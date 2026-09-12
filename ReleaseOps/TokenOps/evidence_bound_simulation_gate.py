#!/usr/bin/env python3
"""Fail-closed evidence-bound approval input for unsigned TokenOps simulations.

This module never serializes, signs, submits, or broadcasts a transaction. It
binds a validated CI/on-chain evidence artifact digest to a non-executing
financial manifest and to the derived simulation plan. A plan can be marked
eligible for simulation review only; execution always remains prohibited here.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict

import evidence_artifact_binding
import simulation_plan

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK = "solana-mainnet-beta"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
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

def build(manifest: Dict[str, Any], evidence_binding: Dict[str, Any]) -> Dict[str, Any]:
    """Bind evidence to an unsigned manifest and its non-executing simulation plan."""
    _reject_secrets({"manifest": manifest, "evidence_binding": evidence_binding})
    verification = evidence_artifact_binding.verify(evidence_binding)
    evidence_sha = _hex64(verification["evidence_binding_sha256"], "evidence_binding_sha256")

    if manifest.get("network") != NETWORK or manifest.get("mint") != CANONICAL_MINT:
        raise ValueError("canonical network/mint mismatch")
    if manifest.get("evidence_binding_sha256") != evidence_sha:
        raise ValueError("manifest evidence binding mismatch")
    for key in ("transaction_created", "transaction_signed", "transaction_submitted", "broadcast_allowed"):
        if manifest.get(key) is not False:
            raise ValueError(f"unsafe manifest flag: {key}")
    if manifest.get("external_signer_required") is not True:
        raise ValueError("external signer boundary missing")
    if manifest.get("financial_effect") not in (None, False):
        raise ValueError("financial effect must remain false")

    manifest_sha = _hex64(manifest.get("manifest_sha256"), "manifest_sha256")
    plan = simulation_plan.build(manifest)
    if plan.get("manifest_sha256") != manifest_sha:
        raise ValueError("simulation plan manifest digest mismatch")
    if plan.get("network") != NETWORK or plan.get("mint") != CANONICAL_MINT:
        raise ValueError("simulation plan canonical scope mismatch")

    safety = plan.get("safety") or {}
    for key in ("transaction_created", "transaction_signed", "transaction_submitted", "financial_effect"):
        if safety.get(key) is not False:
            raise ValueError(f"unsafe simulation plan flag: {key}")
    sim = plan.get("solana_simulation") or {}
    if sim.get("simulation_only") is not True or sim.get("broadcast_allowed") is not False:
        raise ValueError("simulation boundary invalid")

    core = {
        "version": 1,
        "network": NETWORK,
        "mint": CANONICAL_MINT,
        "operation": manifest.get("operation"),
        "manifest_sha256": manifest_sha,
        "simulation_plan_sha256": _hex64(plan.get("simulation_plan_sha256"), "simulation_plan_sha256"),
        "evidence_binding_sha256": evidence_sha,
        "source_head_sha": evidence_binding.get("source_head_sha"),
        "registry_compiler_binding_sha256": evidence_binding.get("registry_compiler_binding_sha256"),
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
    core["evidence_bound_simulation_gate_sha256"] = _canonical_sha256(core)
    return core

def verify(gate: Dict[str, Any]) -> Dict[str, Any]:
    _reject_secrets(gate)
    supplied = _hex64(
        gate.get("evidence_bound_simulation_gate_sha256"),
        "evidence_bound_simulation_gate_sha256",
    )
    core = dict(gate)
    core.pop("evidence_bound_simulation_gate_sha256", None)
    if _canonical_sha256(core) != supplied:
        raise ValueError("evidence-bound simulation gate digest mismatch")
    if core.get("network") != NETWORK or core.get("mint") != CANONICAL_MINT:
        raise ValueError("canonical scope mismatch")
    if core.get("simulation_review_eligible") is not True:
        raise ValueError("simulation review eligibility missing")
    for key in (
        "simulation_execution_permitted", "transaction_created", "transaction_serialized",
        "transaction_signed", "transaction_submitted", "broadcast_allowed",
        "financial_effect", "private_key_used", "wave_mawja_touched",
    ):
        if core.get(key) is not False:
            raise ValueError(f"unsafe gate flag: {key}")
    if core.get("external_signer_required_for_execution") is not True:
        raise ValueError("external signer requirement missing")
    if core.get("user_controlled_approval_required_for_execution") is not True:
        raise ValueError("user approval requirement missing")
    return {"verified": True, "evidence_bound_simulation_gate_sha256": supplied}
