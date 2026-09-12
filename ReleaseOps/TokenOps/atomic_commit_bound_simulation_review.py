#!/usr/bin/env python3
"""Bind simulation-review eligibility to a durably committed anchored approval ledger head.

Review-only control plane. This module verifies the atomic anchored approval
commit receipt against the exact live append-only ledger head and binds that
proof to a non-executing simulation plan. It never creates, serializes, signs,
submits, broadcasts, transfers, burns, changes authorities, settles rewards or
vesting, migrates treasury, or executes DAO decisions.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict

import audit_export
import simulation_plan

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK = "solana-mainnet-beta"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
FORBIDDEN_FIELDS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "raw_transaction", "serialized_transaction",
}


def _sha(value: Dict[str, Any]) -> str:
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


def _verify_commit_receipt(receipt: Dict[str, Any], ledger_path: str, expected_source_head_sha: str) -> Dict[str, Any]:
    _reject_secrets(receipt)
    supplied = _hex64(receipt.get("anchored_approval_ledger_commit_sha256"), "anchored_approval_ledger_commit_sha256")
    core = dict(receipt)
    core.pop("anchored_approval_ledger_commit_sha256", None)
    if _sha(core) != supplied:
        raise ValueError("atomic approval commit receipt digest mismatch")
    if receipt.get("record_type") != "tokenops_atomic_anchored_approval_ledger_commit":
        raise ValueError("unexpected receipt type")
    if receipt.get("network") != NETWORK or receipt.get("mint") != CANONICAL_MINT:
        raise ValueError("canonical receipt scope mismatch")
    if not isinstance(expected_source_head_sha, str) or not HEX40.fullmatch(expected_source_head_sha):
        raise ValueError("expected source head must be lowercase 40-hex")
    if receipt.get("source_head_sha") != expected_source_head_sha:
        raise ValueError("receipt source head mismatch")
    for key in ("atomic_local_commit", "anchored_replay_consumed", "approval_evidence_appended"):
        if receipt.get(key) is not True:
            raise ValueError(f"required receipt control missing: {key}")
    for key in (
        "simulation_execution_permitted", "execution_authorized", "transaction_created",
        "transaction_serialized", "transaction_signed", "transaction_submitted",
        "broadcast_allowed", "financial_effect", "private_key_used", "wave_mawja_touched",
    ):
        if receipt.get(key) is not False:
            raise ValueError(f"unsafe receipt flag: {key}")
    if receipt.get("external_signer_required_for_execution") is not True:
        raise ValueError("external signer boundary missing")
    if receipt.get("user_controlled_approval_required_for_execution") is not True:
        raise ValueError("user-controlled approval boundary missing")

    final_head = _hex64(receipt.get("final_ledger_head_sha256"), "final_ledger_head_sha256")
    if receipt.get("approval_ledger_entry_sha256") != final_head:
        raise ValueError("approval entry is not receipt final ledger head")
    live = audit_export.verify(ledger_path)
    if live.get("head_hash") != final_head:
        raise ValueError("live ledger head differs from atomic approval commit receipt")
    return {"receipt_sha256": supplied, "final_ledger_head_sha256": final_head, "ledger_entries": live.get("entries")}


def build(manifest: Dict[str, Any], commit_receipt: Dict[str, Any], ledger_path: str, expected_source_head_sha: str) -> Dict[str, Any]:
    _reject_secrets({"manifest": manifest, "commit_receipt": commit_receipt})
    verified = _verify_commit_receipt(commit_receipt, ledger_path, expected_source_head_sha)
    if manifest.get("network") != NETWORK or manifest.get("mint") != CANONICAL_MINT:
        raise ValueError("canonical manifest scope mismatch")
    manifest_sha = _hex64(manifest.get("manifest_sha256"), "manifest_sha256")
    if commit_receipt.get("manifest_sha256") != manifest_sha:
        raise ValueError("manifest is not the one durably approved in the ledger")
    for key in ("transaction_created", "transaction_signed", "transaction_submitted", "broadcast_allowed"):
        if manifest.get(key) is not False:
            raise ValueError(f"unsafe manifest flag: {key}")
    if manifest.get("external_signer_required") is not True:
        raise ValueError("manifest external signer boundary missing")
    if manifest.get("financial_effect") not in (None, False):
        raise ValueError("manifest financial effect must remain false")

    plan = simulation_plan.build(manifest)
    safety = plan.get("safety") or {}
    for key in ("transaction_created", "transaction_signed", "transaction_submitted", "financial_effect"):
        if safety.get(key) is not False:
            raise ValueError(f"unsafe simulation plan flag: {key}")
    sim = plan.get("solana_simulation") or {}
    if sim.get("simulation_only") is not True or sim.get("broadcast_allowed") is not False:
        raise ValueError("simulation boundary invalid")

    core = {
        "version": 1,
        "record_type": "tokenops_atomic_commit_bound_simulation_review",
        "network": NETWORK,
        "mint": CANONICAL_MINT,
        "operation": manifest.get("operation"),
        "manifest_sha256": manifest_sha,
        "simulation_plan_sha256": _hex64(plan.get("simulation_plan_sha256"), "simulation_plan_sha256"),
        "anchored_approval_ledger_commit_sha256": verified["receipt_sha256"],
        "final_ledger_head_sha256": verified["final_ledger_head_sha256"],
        "ledger_entries_verified": verified["ledger_entries"],
        "source_head_sha": expected_source_head_sha,
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
    core["atomic_commit_bound_simulation_review_sha256"] = _sha(core)
    return core


def verify(gate: Dict[str, Any]) -> Dict[str, Any]:
    _reject_secrets(gate)
    supplied = _hex64(gate.get("atomic_commit_bound_simulation_review_sha256"), "atomic_commit_bound_simulation_review_sha256")
    core = dict(gate)
    core.pop("atomic_commit_bound_simulation_review_sha256", None)
    if _sha(core) != supplied:
        raise ValueError("atomic-commit-bound review digest mismatch")
    if core.get("network") != NETWORK or core.get("mint") != CANONICAL_MINT:
        raise ValueError("canonical scope mismatch")
    if core.get("durable_approval_commit_verified") is not True or core.get("exact_final_ledger_head_verified") is not True:
        raise ValueError("durable ledger proof missing")
    if core.get("simulation_review_eligible") is not True:
        raise ValueError("simulation review eligibility missing")
    for key in (
        "simulation_execution_permitted", "execution_authorized", "transaction_created",
        "transaction_serialized", "transaction_signed", "transaction_submitted",
        "broadcast_allowed", "financial_effect", "private_key_used", "wave_mawja_touched",
    ):
        if core.get(key) is not False:
            raise ValueError(f"unsafe gate flag: {key}")
    if core.get("external_signer_required_for_execution") is not True or core.get("user_controlled_approval_required_for_execution") is not True:
        raise ValueError("execution approval boundary missing")
    return {"verified": True, "atomic_commit_bound_simulation_review_sha256": supplied}
