#!/usr/bin/env python3
"""Atomically commit anchored simulation-review approval evidence to the TokenOps ledger.

Fail-closed, review-only control. The externally anchored one-time replay token
consumption and its corresponding approval evidence are staged on a temporary
copy of the append-only ledger and installed with one atomic local replace only
after the complete chain verifies. This module never creates, serializes,
simulates, signs, submits, broadcasts, transfers, burns, changes authorities,
settles rewards/vesting, migrates treasury, or executes DAO decisions.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import tempfile
from typing import Any, Dict

import anchored_approval_binding
import audit_export


def _sha(value: Dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _bytes_sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def commit_review(
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
    """Consume replay evidence and append approval evidence as one local ledger commit."""
    ledger = pathlib.Path(ledger_path)
    if not ledger.exists():
        raise ValueError("anchored ledger does not exist")

    original_bytes = ledger.read_bytes()
    original_bytes_sha256 = _bytes_sha(original_bytes)
    original_state = audit_export.verify(ledger_path)
    anchored_prior_head = anchored_guard.get("anchored_prior_ledger_head_sha256")
    if original_state.get("head_hash") != anchored_prior_head:
        raise ValueError("live ledger head differs from externally anchored prior head")

    fd, staged_name = tempfile.mkstemp(
        prefix=f".{ledger.name}.tokenops-review-",
        suffix=".tmp",
        dir=str(ledger.parent),
    )
    os.close(fd)
    staged = pathlib.Path(staged_name)
    staged.write_bytes(original_bytes)

    try:
        approval = anchored_approval_binding.consume_and_build(
            manifest,
            policy,
            freshness_gate,
            anchored_guard,
            anchor_request,
            anchor_receipt,
            str(staged),
            expected_source_head_sha,
            created_at=created_at,
        )

        after_consumption = audit_export.verify(str(staged))
        consumption_head = approval.get("replay_consumption_entry_sha256")
        if after_consumption.get("head_hash") != consumption_head:
            raise ValueError("replay consumption is not the staged ledger head")
        if after_consumption.get("entries") != original_state.get("entries", 0) + 1:
            raise ValueError("unexpected staged ledger growth after replay consumption")
        if approval.get("anchored_replay_consumed") is not True:
            raise ValueError("anchored replay token was not consumed")
        if approval.get("execution_authorized") is not False:
            raise ValueError("approval unexpectedly authorizes execution")
        if approval.get("simulation_execution_permitted") is not False:
            raise ValueError("approval unexpectedly permits simulation execution")

        event = {
            "version": 1,
            "event_type": "tokenops_anchored_simulation_review_approval_committed",
            "network": approval.get("network"),
            "mint": approval.get("mint"),
            "operation": approval.get("operation"),
            "manifest_sha256": approval.get("manifest_sha256"),
            "source_head_sha": approval.get("source_head_sha"),
            "evidence_freshness_gate_sha256": approval.get("evidence_freshness_gate_sha256"),
            "external_anchor_continuity_sha256": approval.get("external_anchor_continuity_sha256"),
            "anchored_review_replay_guard_sha256": approval.get("anchored_review_replay_guard_sha256"),
            "review_replay_token_sha256": approval.get("review_replay_token_sha256"),
            "replay_consumption_entry_sha256": consumption_head,
            "anchored_approval_binding_sha256": approval.get("anchored_approval_binding_sha256"),
            "approval_count": approval.get("approval_count"),
            "required_approvals": approval.get("required_approvals"),
            "threshold_met": approval.get("threshold_met"),
            "external_immutable_anchor_verified": True,
            "ledger_continuity_verified": True,
            "anchored_replay_consumed": True,
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
        approval_entry = audit_export.append_entry(event, str(staged), created_at=created_at)
        if approval_entry.get("previous_hash") != consumption_head:
            raise ValueError("approval ledger entry is not directly chained to replay consumption")

        final_state = audit_export.verify(str(staged))
        if final_state.get("head_hash") != approval_entry.get("entry_hash"):
            raise ValueError("approval entry is not final staged ledger head")
        if final_state.get("entries") != original_state.get("entries", 0) + 2:
            raise ValueError("unexpected staged ledger growth after approval commit")

        # Optimistic concurrency guard: never overwrite a ledger that changed while
        # the staged review chain was being built.
        if not ledger.exists() or _bytes_sha(ledger.read_bytes()) != original_bytes_sha256:
            raise ValueError("live ledger changed during staged approval commit")

        receipt = {
            "version": 1,
            "record_type": "tokenops_atomic_anchored_approval_ledger_commit",
            "network": approval.get("network"),
            "mint": approval.get("mint"),
            "manifest_sha256": approval.get("manifest_sha256"),
            "source_head_sha": approval.get("source_head_sha"),
            "anchored_prior_ledger_head_sha256": anchored_prior_head,
            "original_ledger_bytes_sha256": original_bytes_sha256,
            "external_anchor_continuity_sha256": approval.get("external_anchor_continuity_sha256"),
            "anchored_review_replay_guard_sha256": approval.get("anchored_review_replay_guard_sha256"),
            "review_replay_token_sha256": approval.get("review_replay_token_sha256"),
            "replay_consumption_entry_sha256": consumption_head,
            "anchored_approval_binding_sha256": approval.get("anchored_approval_binding_sha256"),
            "approval_ledger_entry_sha256": approval_entry.get("entry_hash"),
            "final_ledger_head_sha256": final_state.get("head_hash"),
            "atomic_local_commit": True,
            "anchored_replay_consumed": True,
            "approval_evidence_appended": True,
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
        receipt["anchored_approval_ledger_commit_sha256"] = _sha(receipt)

        os.replace(staged, ledger)
        return receipt
    except Exception:
        try:
            staged.unlink(missing_ok=True)
        finally:
            raise
