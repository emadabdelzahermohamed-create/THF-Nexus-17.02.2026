#!/usr/bin/env python3
"""Bind externally anchored one-time review consumption into THF approval evidence.

Review-only and fail-closed. This module never creates, serializes, simulates, signs,
submits, broadcasts, transfers, burns, changes authorities, settles rewards/vesting,
or executes DAO decisions on Solana.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

import anchored_review_replay_guard
import evidence_freshness_gate
import freshness_ledger_binding

FORBIDDEN_FIELDS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "raw_transaction", "serialized_transaction",
}


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


def consume_and_build(
    manifest: Dict[str, Any],
    policy: Dict[str, Any],
    freshness_gate: Dict[str, Any],
    anchored_guard: Dict[str, Any],
    anchor_request: Dict[str, Any],
    anchor_receipt: Dict[str, Any],
    ledger_path: str,
    expected_source_head_sha: str,
    created_at: int | None = None,
) -> Dict[str, Any]:
    """Build review approval only after externally anchored one-time token consumption."""
    _reject({
        "manifest": manifest,
        "policy": policy,
        "freshness_gate": freshness_gate,
        "anchored_guard": anchored_guard,
        "anchor_request": anchor_request,
        "anchor_receipt": anchor_receipt,
    })

    verified_freshness = evidence_freshness_gate.verify(freshness_gate)
    manifest_sha = manifest.get("manifest_sha256")
    if freshness_gate.get("manifest_sha256") != manifest_sha:
        raise ValueError("freshness gate manifest mismatch")
    if anchored_guard.get("manifest_sha256") != manifest_sha:
        raise ValueError("anchored replay guard manifest mismatch")
    if anchored_guard.get("evidence_freshness_gate_sha256") != verified_freshness["evidence_freshness_gate_sha256"]:
        raise ValueError("anchored replay guard freshness digest mismatch")
    if anchored_guard.get("source_head_sha") != expected_source_head_sha.lower():
        raise ValueError("anchored replay guard source head mismatch")
    if anchored_guard.get("mint") != manifest.get("mint") or anchored_guard.get("network") != policy.get("network"):
        raise ValueError("anchored replay guard mint/network mismatch")

    # Pre-build the non-authorizing approval record before consuming the one-time token.
    # This avoids consuming a valid token if the manifest/policy approval record is invalid.
    base = freshness_ledger_binding.build_approval_record(manifest, policy, freshness_gate)
    if base.get("execution_authorized") is not False:
        raise ValueError("approval record must not authorize execution")
    if base.get("external_multisig_required") is not True:
        raise ValueError("external multisig boundary missing")

    consumed = anchored_review_replay_guard.consume(
        anchored_guard,
        anchor_request,
        anchor_receipt,
        ledger_path,
        expected_source_head_sha,
        created_at=created_at,
    )
    if consumed.get("consumed") is not True:
        raise ValueError("anchored replay token was not consumed")
    if consumed.get("execution_authorized") is not False:
        raise ValueError("anchored consumption unexpectedly authorized execution")

    entry = consumed.get("entry") or {}
    event = entry.get("event") or {}
    if event.get("manifest_sha256") != manifest_sha:
        raise ValueError("consumed replay entry manifest mismatch")
    if event.get("evidence_freshness_gate_sha256") != verified_freshness["evidence_freshness_gate_sha256"]:
        raise ValueError("consumed replay entry freshness mismatch")
    if event.get("review_replay_token_sha256") != anchored_guard.get("review_replay_token_sha256"):
        raise ValueError("consumed replay token mismatch")
    if event.get("source_head_sha") != expected_source_head_sha.lower():
        raise ValueError("consumed replay entry source head mismatch")

    base.pop("ledger_entry_sha256", None)
    base.update({
        "record_type": "anchored_one_time_simulation_review_approval",
        "source_head_sha": expected_source_head_sha.lower(),
        "external_anchor_continuity_sha256": anchored_guard.get("external_anchor_continuity_sha256"),
        "anchored_review_replay_guard_sha256": anchored_guard.get("anchored_review_replay_guard_sha256"),
        "review_replay_token_sha256": anchored_guard.get("review_replay_token_sha256"),
        "replay_consumption_entry_sha256": entry.get("entry_hash"),
        "anchored_replay_consumed": True,
        "external_immutable_anchor_verified": True,
        "ledger_continuity_verified": True,
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
    })
    base["anchored_approval_binding_sha256"] = _sha(base)
    return base
