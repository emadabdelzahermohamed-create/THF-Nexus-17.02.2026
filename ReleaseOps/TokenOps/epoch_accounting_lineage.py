#!/usr/bin/env python3
"""Deterministic THF multi-epoch accounting lineage gate.

Accounting/review evidence only. This module never constructs, signs, submits,
broadcasts, transfers, burns, settles, migrates treasury balances, changes
authorities, or executes DAO decisions.
"""
from __future__ import annotations
import hashlib, json, re
from typing import Any, Dict, Optional

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
CANONICAL_NETWORK = "solana-mainnet-beta"
SNAPSHOT_SCHEMA = "thf-tokenops-reservation-epoch-close-snapshot/v1"
ROLLFORWARD_SCHEMA = "thf-tokenops-cross-epoch-accounting-rollforward/v1"
LINEAGE_SCHEMA = "thf-tokenops-multi-epoch-accounting-lineage/v1"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS = {"seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair", "signature", "signed_transaction", "raw_transaction", "serialized_transaction"}

def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()

def _scan(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_KEYS:
                raise ValueError(f"forbidden sensitive/signature field at {path}.{key}")
            _scan(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _scan(item, f"{path}[{index}]")

def _hex(value: Any, label: str) -> str:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise ValueError(f"invalid {label} SHA-256")
    return value

def _raw(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be integer raw amount")
    if isinstance(value, int):
        number = value
    elif isinstance(value, str) and value.isdigit():
        number = int(value)
    else:
        raise ValueError(f"{label} must be integer raw amount")
    if number < 0:
        raise ValueError(f"invalid {label}")
    return number

def _verify_digest(obj: Dict[str, Any], field: str, label: str) -> str:
    digest = _hex(obj.get(field), label)
    body = dict(obj); body.pop(field, None)
    if canonical_sha256(body) != digest:
        raise ValueError(f"{label} SHA-256 mismatch")
    return digest

def _safe_execution(execution: Dict[str, Any], label: str) -> None:
    for key in ("transaction_created", "transaction_signed", "transaction_submitted", "broadcast_allowed", "financial_effect", "settlement_executed", "burn_executed", "treasury_migrated", "dao_decision_executed", "private_key_used"):
        if execution.get(key) is not False:
            raise ValueError(f"unsafe {label} execution flag: {key}")
    if execution.get("wave_mawja_untouched") is not True:
        raise ValueError(f"{label} WAVE isolation flag is not preserved")

def _verify_close(snapshot: Dict[str, Any]) -> str:
    if snapshot.get("schema") != SNAPSHOT_SCHEMA or snapshot.get("network") != CANONICAL_NETWORK or snapshot.get("mint") != CANONICAL_MINT:
        raise ValueError("epoch-close target/schema mismatch")
    digest = _verify_digest(snapshot, "epoch_close_snapshot_sha256", "epoch-close snapshot")
    _safe_execution(snapshot.get("execution", {}), "epoch-close")
    accounting = snapshot.get("accounting", {})
    source = _raw(accounting.get("source_reserved_total_raw"), "source reserved total")
    active = _raw(accounting.get("active_reserved_total_raw"), "active reserved total")
    released = _raw(accounting.get("released_or_cancelled_net_raw"), "released/cancelled total")
    if source != active + released:
        raise ValueError("epoch-close accounting invariant mismatch")
    return digest

def _verify_rollforward(rollforward: Dict[str, Any]) -> str:
    if rollforward.get("schema") != ROLLFORWARD_SCHEMA or rollforward.get("network") != CANONICAL_NETWORK or rollforward.get("mint") != CANONICAL_MINT:
        raise ValueError("roll-forward target/schema mismatch")
    digest = _verify_digest(rollforward, "cross_epoch_rollforward_sha256", "cross-epoch roll-forward")
    _safe_execution(rollforward.get("execution", {}), "roll-forward")
    accounting = rollforward.get("accounting", {})
    carry = _raw(accounting.get("carry_forward_active_reserved_raw"), "carry-forward total")
    budget = _raw(accounting.get("next_approved_budget_raw"), "next approved budget")
    opening = _raw(accounting.get("next_opening_accounting_total_raw"), "next opening total")
    if opening != carry + budget:
        raise ValueError("roll-forward accounting conservation mismatch")
    return digest

def _verify_previous(previous: Dict[str, Any]) -> str:
    if previous.get("schema") != LINEAGE_SCHEMA or previous.get("network") != CANONICAL_NETWORK or previous.get("mint") != CANONICAL_MINT:
        raise ValueError("previous lineage target/schema mismatch")
    digest = _verify_digest(previous, "lineage_checkpoint_sha256", "previous lineage checkpoint")
    _safe_execution(previous.get("execution", {}), "previous lineage")
    return digest

def compile_lineage_checkpoint(prior_close: Dict[str, Any], rollforward: Dict[str, Any], request: Dict[str, Any], previous: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Append one verified roll-forward to an immutable multi-epoch lineage."""
    _scan(prior_close); _scan(rollforward); _scan(request)
    if previous is not None: _scan(previous)
    close_sha = _verify_close(prior_close)
    rollforward_sha = _verify_rollforward(rollforward)
    if request.get("network") != CANONICAL_NETWORK or request.get("mint") != CANONICAL_MINT:
        raise ValueError("lineage request target mismatch")
    if request.get("prior_epoch_close_snapshot_sha256") != close_sha:
        raise ValueError("lineage detached from epoch-close snapshot")
    if request.get("cross_epoch_rollforward_sha256") != rollforward_sha:
        raise ValueError("lineage detached from roll-forward evidence")
    prior_epoch = str(prior_close.get("epoch_id", "")).strip()
    rf_prior = str(rollforward.get("prior_epoch_id", "")).strip()
    next_epoch = str(rollforward.get("next_epoch_id", "")).strip()
    if not prior_epoch or prior_epoch != rf_prior or not next_epoch or prior_epoch == next_epoch:
        raise ValueError("lineage epoch transition mismatch")
    if rollforward.get("prior_epoch_close_snapshot_sha256") != close_sha:
        raise ValueError("roll-forward does not consume supplied epoch-close head")
    carry = str(prior_close.get("accounting", {}).get("active_reserved_total_raw", ""))
    if carry != str(rollforward.get("accounting", {}).get("carry_forward_active_reserved_raw", "")):
        raise ValueError("roll-forward carry-forward does not match epoch-close active reservations")
    history = []; prior_lineage_sha = None
    blockers = set(str(x) for x in prior_close.get("blockers", [])) | set(str(x) for x in rollforward.get("blockers", []))
    if previous is not None:
        prior_lineage_sha = _verify_previous(previous)
        if request.get("previous_lineage_checkpoint_sha256") != prior_lineage_sha:
            raise ValueError("stale/forked previous lineage head")
        if str(previous.get("next_epoch_id", "")).strip() != prior_epoch:
            raise ValueError("non-contiguous epoch lineage")
        history = list(previous.get("history", []))
        blockers |= set(str(x) for x in previous.get("blockers", []))
    elif request.get("previous_lineage_checkpoint_sha256") not in (None, ""):
        raise ValueError("unexpected previous lineage head for genesis checkpoint")
    for item in history:
        if not isinstance(item, dict): raise ValueError("invalid lineage history item")
        _hex(item.get("epoch_close_snapshot_sha256"), "history epoch-close")
        _hex(item.get("cross_epoch_rollforward_sha256"), "history roll-forward")
    used_close = {item["epoch_close_snapshot_sha256"] for item in history}
    used_rollforward = {item["cross_epoch_rollforward_sha256"] for item in history}
    if close_sha in used_close or rollforward_sha in used_rollforward:
        raise ValueError("replayed epoch evidence")
    history.append({"prior_epoch_id": prior_epoch, "next_epoch_id": next_epoch, "epoch_close_snapshot_sha256": close_sha, "cross_epoch_rollforward_sha256": rollforward_sha})
    if len({item["prior_epoch_id"] for item in history}) != len(history): raise ValueError("duplicate prior epoch in lineage")
    if len({item["next_epoch_id"] for item in history}) != len(history): raise ValueError("duplicate next epoch in lineage")
    result = {"schema": LINEAGE_SCHEMA, "network": CANONICAL_NETWORK, "mint": CANONICAL_MINT, "request_id": str(request.get("request_id", "")), "previous_lineage_checkpoint_sha256": prior_lineage_sha, "prior_epoch_id": prior_epoch, "next_epoch_id": next_epoch, "epoch_close_snapshot_sha256": close_sha, "cross_epoch_rollforward_sha256": rollforward_sha, "history": history, "lineage_review_eligible": len(blockers) == 0, "blockers": sorted(blockers), "execution": {"transaction_created": False, "transaction_signed": False, "transaction_submitted": False, "broadcast_allowed": False, "financial_effect": False, "settlement_executed": False, "burn_executed": False, "treasury_migrated": False, "dao_decision_executed": False, "private_key_used": False, "external_multisig_required": True, "wave_mawja_untouched": True}}
    result["lineage_checkpoint_sha256"] = canonical_sha256(result)
    return result
