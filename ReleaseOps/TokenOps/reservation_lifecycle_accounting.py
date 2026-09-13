#!/usr/bin/env python3
"""Deterministic THF reservation release/cancellation/replacement accounting evidence.

Review/accounting only. This module never constructs, signs, submits, broadcasts,
transfers, burns, settles, migrates treasury balances, changes authorities, or
executes DAO decisions.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Iterable, List, Tuple

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
CANONICAL_NETWORK = "solana-mainnet-beta"
RESERVATION_SCHEMA = "thf-tokenops-budget-reservation-reconciliation/v1"
TRANSITION_SCHEMA = "thf-tokenops-reservation-lifecycle-accounting/v1"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "raw_transaction", "serialized_transaction",
}

def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(payload).hexdigest()

def _scan(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_KEYS:
                raise ValueError(f"forbidden sensitive/signature field at {path}.{key}")
            _scan(item, f"{path}.{key}")
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            _scan(item, f"{path}[{idx}]")

def _positive_raw(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a positive integer raw-token amount")
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str) and value.isdigit():
        parsed = int(value)
    else:
        raise ValueError(f"{label} must be a positive integer raw-token amount")
    if parsed <= 0:
        raise ValueError(f"{label} must be positive")
    return parsed

def _verify_digest(obj: Dict[str, Any], field: str, label: str) -> str:
    digest = obj.get(field)
    if not isinstance(digest, str) or not HEX64.fullmatch(digest):
        raise ValueError(f"invalid {label} SHA-256")
    body = dict(obj)
    body.pop(field, None)
    if canonical_sha256(body) != digest:
        raise ValueError(f"{label} SHA-256 mismatch")
    return digest

def _verify_execution(execution: Dict[str, Any], label: str) -> None:
    for key in (
        "transaction_created", "transaction_signed", "transaction_submitted",
        "broadcast_allowed", "financial_effect", "settlement_executed",
        "burn_executed", "treasury_migrated", "dao_decision_executed",
        "private_key_used",
    ):
        if key in execution and execution.get(key) is not False:
            raise ValueError(f"unsafe {label} execution flag: {key}")
    if execution.get("wave_mawja_untouched") is not True:
        raise ValueError(f"{label} WAVE isolation flag is not preserved")

def _verify_reservation_evidence(evidence: Dict[str, Any]) -> Tuple[str, str, List[Dict[str, Any]], List[str]]:
    if evidence.get("schema") != RESERVATION_SCHEMA:
        raise ValueError("unexpected reservation reconciliation schema")
    if evidence.get("network") != CANONICAL_NETWORK or evidence.get("mint") != CANONICAL_MINT:
        raise ValueError("reservation reconciliation target mismatch")
    digest = _verify_digest(evidence, "reservation_reconciliation_sha256", "reservation reconciliation")
    envelope_sha = evidence.get("budget_envelope_sha256")
    if not isinstance(envelope_sha, str) or not HEX64.fullmatch(envelope_sha):
        raise ValueError("invalid budget-envelope SHA-256")
    _verify_execution(evidence.get("execution", {}), "reservation reconciliation")
    rows = list(evidence.get("reservations", []))
    if not rows:
        raise ValueError("reservation reconciliation contains no reservations")
    blockers = sorted(set(str(x) for x in evidence.get("blockers", [])))
    return digest, envelope_sha, rows, blockers

def _verify_prior_transition(prior: Dict[str, Any], reservation_sha: str, envelope_sha: str) -> Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    if prior.get("schema") != TRANSITION_SCHEMA:
        raise ValueError("unexpected prior lifecycle schema")
    if prior.get("network") != CANONICAL_NETWORK or prior.get("mint") != CANONICAL_MINT:
        raise ValueError("prior lifecycle target mismatch")
    if prior.get("source_reservation_reconciliation_sha256") != reservation_sha:
        raise ValueError("prior lifecycle detached from source reservation evidence")
    if prior.get("budget_envelope_sha256") != envelope_sha:
        raise ValueError("prior lifecycle detached from budget envelope")
    digest = _verify_digest(prior, "reservation_lifecycle_sha256", "reservation lifecycle")
    _verify_execution(prior.get("execution", {}), "prior lifecycle")
    return digest, list(prior.get("active_reservations", [])), list(prior.get("lifecycle_events", [])), sorted(set(str(x) for x in prior.get("blockers", [])))

def compile_reservation_lifecycle(reservation_evidence: Dict[str, Any], request: Dict[str, Any], prior_transition: Dict[str, Any] | None = None) -> Dict[str, Any]:
    _scan(reservation_evidence)
    _scan(request)
    if prior_transition is not None:
        _scan(prior_transition)

    reservation_sha, envelope_sha, source_rows, upstream_blockers = _verify_reservation_evidence(reservation_evidence)
    if request.get("network") != CANONICAL_NETWORK or request.get("mint") != CANONICAL_MINT:
        raise ValueError("lifecycle request target mismatch")
    if request.get("source_reservation_reconciliation_sha256") != reservation_sha:
        raise ValueError("lifecycle request detached from reservation reconciliation")
    if request.get("budget_envelope_sha256") != envelope_sha:
        raise ValueError("lifecycle request detached from budget envelope")

    active: Dict[str, Dict[str, Any]] = {}
    for row in source_rows:
        rid = str(row.get("reservation_id", "")).strip()
        subject = str(row.get("subject_id", "")).strip()
        wallet = str(row.get("wallet", "")).strip()
        amount = _positive_raw(row.get("amount_raw"), "source reservation amount_raw")
        if not rid or rid in active or not subject or not wallet:
            raise ValueError("invalid/duplicate source reservation")
        active[rid] = {"reservation_id": rid, "subject_id": subject, "wallet": wallet, "amount_raw": str(amount)}

    prior_sha = None
    events: List[Dict[str, Any]] = []
    blockers = list(upstream_blockers)
    if prior_transition is not None:
        prior_sha, prior_active, prior_events, prior_blockers = _verify_prior_transition(prior_transition, reservation_sha, envelope_sha)
        if request.get("expected_prior_reservation_lifecycle_sha256") != prior_sha:
            raise ValueError("lifecycle request prior-transition anchor mismatch")
        active = {}
        for row in prior_active:
            rid = str(row.get("reservation_id", "")).strip()
            if not rid or rid in active:
                raise ValueError("invalid/duplicate prior active reservation")
            active[rid] = {"reservation_id": rid, "subject_id": str(row.get("subject_id", "")).strip(), "wallet": str(row.get("wallet", "")).strip(), "amount_raw": str(_positive_raw(row.get("amount_raw"), "prior active amount_raw"))}
        events = list(prior_events)
        blockers.extend(prior_blockers)
    elif request.get("expected_prior_reservation_lifecycle_sha256") not in (None, ""):
        raise ValueError("unexpected prior-transition anchor without prior transition")

    seen_event_ids = {str(e.get("event_id", "")).strip() for e in events}
    if "" in seen_event_ids:
        raise ValueError("prior lifecycle contains blank event_id")

    new_events: List[Dict[str, Any]] = []
    for op in request.get("operations", []):
        event_id = str(op.get("event_id", "")).strip()
        action = str(op.get("action", "")).strip().lower()
        target_id = str(op.get("reservation_id", "")).strip()
        if not event_id or event_id in seen_event_ids:
            raise ValueError("duplicate/blank lifecycle event_id")
        if action not in {"release", "cancel", "replace"}:
            raise ValueError("unsupported lifecycle action")
        if target_id not in active:
            raise ValueError("lifecycle action targets non-active/unknown reservation")

        target = active[target_id]
        replacement = None
        if action == "replace":
            replacement_id = str(op.get("replacement_reservation_id", "")).strip()
            if not replacement_id or replacement_id in active:
                raise ValueError("invalid/duplicate replacement reservation_id")
            amount = _positive_raw(op.get("replacement_amount_raw"), "replacement_amount_raw")
            if amount > int(target["amount_raw"]):
                raise ValueError("replacement cannot exceed released reservation amount")
            replacement = {"reservation_id": replacement_id, "subject_id": target["subject_id"], "wallet": target["wallet"], "amount_raw": str(amount)}

        released_amount = target["amount_raw"]
        del active[target_id]
        if replacement is not None:
            active[replacement["reservation_id"]] = replacement

        event = {"event_id": event_id, "action": action, "reservation_id": target_id, "subject_id": target["subject_id"], "wallet": target["wallet"], "released_amount_raw": released_amount, "replacement": replacement}
        new_events.append(event)
        seen_event_ids.add(event_id)

    if not new_events:
        raise ValueError("at least one lifecycle operation is required")

    blockers = sorted(set(str(x) for x in blockers))
    active_rows = sorted(active.values(), key=lambda x: x["reservation_id"])
    all_events = events + new_events
    active_total = sum(int(x["amount_raw"]) for x in active_rows)
    original_total = sum(int(x["amount_raw"]) for x in source_rows)

    result: Dict[str, Any] = {
        "schema": TRANSITION_SCHEMA,
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "request_id": str(request.get("request_id", "")),
        "budget_envelope_sha256": envelope_sha,
        "source_reservation_reconciliation_sha256": reservation_sha,
        "prior_reservation_lifecycle_sha256": prior_sha,
        "active_reservations": active_rows,
        "lifecycle_events": all_events,
        "accounting": {"source_reserved_total_raw": str(original_total), "active_reserved_total_raw": str(active_total), "released_or_cancelled_net_raw": str(original_total - active_total), "active_reservation_count": len(active_rows), "lifecycle_event_count": len(all_events)},
        "lifecycle_review_eligible": len(blockers) == 0,
        "blockers": blockers,
        "execution": {"transaction_created": False, "transaction_signed": False, "transaction_submitted": False, "broadcast_allowed": False, "financial_effect": False, "settlement_executed": False, "burn_executed": False, "treasury_migrated": False, "dao_decision_executed": False, "private_key_used": False, "external_multisig_required": True, "wave_mawja_untouched": True},
    }
    result["reservation_lifecycle_sha256"] = canonical_sha256(result)
    return result
