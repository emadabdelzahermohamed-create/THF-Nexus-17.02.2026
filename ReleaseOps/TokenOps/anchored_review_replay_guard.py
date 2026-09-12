#!/usr/bin/env python3
"""Externally anchored one-time review replay guard for THF TokenOps.

Review-only fail-closed control. This module binds the existing freshness/GitHub
metadata replay guard to a live verification of the external immutable ledger
anchor. It never creates, serializes, simulates, signs, submits, broadcasts,
transfers, burns, or changes Solana state.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable

import external_anchor_continuity_gate
import review_replay_guard


def _sha(value: Dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def prepare(
    freshness_gate: Dict[str, Any],
    metadata_snapshots: Iterable[Dict[str, Any]],
    anchor_request: Dict[str, Any],
    anchor_receipt: Dict[str, Any],
    ledger_path: str,
    expected_source_head_sha: str,
) -> Dict[str, Any]:
    """Prepare a one-time review token only from a freshly verified external anchor."""
    continuity = external_anchor_continuity_gate.verify_continuity(
        anchor_request,
        anchor_receipt,
        ledger_path,
        expected_source_head_sha,
    )
    external_anchor_continuity_gate.verify_record(continuity)
    if freshness_gate.get("source_head_sha") != expected_source_head_sha.lower():
        raise ValueError("freshness source head differs from externally anchored source head")

    anchored_prior_head = continuity["anchored_prior_ledger_head_sha256"]
    base_guard = review_replay_guard.prepare(
        freshness_gate,
        metadata_snapshots,
        ledger_path,
        anchored_prior_head,
    )
    if base_guard.get("source_head_sha") != continuity.get("source_head_sha"):
        raise ValueError("replay guard source head differs from immutable anchor")
    if base_guard.get("prior_ledger_head") != anchored_prior_head:
        raise ValueError("replay guard prior head differs from immutable anchor")

    out = {
        "version": 1,
        "record_type": "tokenops_anchored_review_replay_guard",
        "network": base_guard.get("network"),
        "mint": base_guard.get("mint"),
        "source_head_sha": base_guard.get("source_head_sha"),
        "manifest_sha256": base_guard.get("manifest_sha256"),
        "evidence_freshness_gate_sha256": base_guard.get("evidence_freshness_gate_sha256"),
        "github_metadata_bundle_sha256": base_guard.get("github_metadata_bundle_sha256"),
        "external_anchor_continuity_sha256": continuity["external_anchor_continuity_sha256"],
        "anchored_prior_ledger_head_sha256": anchored_prior_head,
        "review_replay_token_sha256": base_guard.get("review_replay_token_sha256"),
        "base_review_replay_guard": base_guard,
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
    }
    out["anchored_review_replay_guard_sha256"] = _sha(out)
    return out


def consume(
    anchored_guard: Dict[str, Any],
    anchor_request: Dict[str, Any],
    anchor_receipt: Dict[str, Any],
    ledger_path: str,
    expected_source_head_sha: str,
    created_at: int | None = None,
) -> Dict[str, Any]:
    """Consume exactly once, after re-verifying that the external anchor still matches live ledger bytes."""
    supplied = anchored_guard.get("anchored_review_replay_guard_sha256")
    core = dict(anchored_guard)
    core.pop("anchored_review_replay_guard_sha256", None)
    if not isinstance(supplied, str) or _sha(core) != supplied:
        raise ValueError("anchored review replay guard digest mismatch")

    continuity = external_anchor_continuity_gate.verify_continuity(
        anchor_request,
        anchor_receipt,
        ledger_path,
        expected_source_head_sha,
    )
    external_anchor_continuity_gate.verify_record(continuity)
    if continuity["external_anchor_continuity_sha256"] != anchored_guard.get("external_anchor_continuity_sha256"):
        raise ValueError("external anchor continuity evidence changed")
    if continuity["anchored_prior_ledger_head_sha256"] != anchored_guard.get("anchored_prior_ledger_head_sha256"):
        raise ValueError("externally anchored prior ledger head changed")
    if continuity.get("source_head_sha") != anchored_guard.get("source_head_sha"):
        raise ValueError("externally anchored source head changed")

    base_guard = anchored_guard.get("base_review_replay_guard")
    if not isinstance(base_guard, dict):
        raise ValueError("base review replay guard missing")
    if base_guard.get("review_replay_token_sha256") != anchored_guard.get("review_replay_token_sha256"):
        raise ValueError("review replay token binding mismatch")

    entry = review_replay_guard.consume(
        base_guard,
        ledger_path,
        anchored_guard["anchored_prior_ledger_head_sha256"],
        created_at=created_at,
    )
    return {
        "consumed": True,
        "entry": entry,
        "external_anchor_continuity_sha256": anchored_guard["external_anchor_continuity_sha256"],
        "anchored_review_replay_guard_sha256": supplied,
        "simulation_review_eligible": True,
        "simulation_execution_permitted": False,
        "execution_authorized": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "broadcast_allowed": False,
        "financial_effect": False,
        "private_key_used": False,
        "wave_mawja_touched": False,
    }
