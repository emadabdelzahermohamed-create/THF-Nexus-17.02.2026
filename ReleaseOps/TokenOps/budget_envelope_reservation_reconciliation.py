#!/usr/bin/env python3
"""Bind THF reward/vesting budget envelopes to reservation/reconciliation evidence.

Review/accounting only. Never constructs or signs a Solana transaction and never
submits, broadcasts, transfers, burns, settles, migrates treasury balances,
changes authorities, or executes DAO decisions.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Iterable, List, Tuple

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
CANONICAL_NETWORK = "solana-mainnet-beta"
EXPECTED_ENVELOPE_SCHEMA = "thf-tokenops-reward-vesting-budget-envelope/v1"
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


def _verify_envelope(envelope: Dict[str, Any]) -> str:
    if envelope.get("schema") != EXPECTED_ENVELOPE_SCHEMA:
        raise ValueError("unexpected budget-envelope schema")
    if envelope.get("network") != CANONICAL_NETWORK or envelope.get("mint") != CANONICAL_MINT:
        raise ValueError("budget-envelope target mismatch")
    digest = envelope.get("envelope_sha256")
    if not isinstance(digest, str) or not HEX64.fullmatch(digest):
        raise ValueError("invalid budget-envelope SHA-256")
    body = dict(envelope)
    body.pop("envelope_sha256", None)
    if canonical_sha256(body) != digest:
        raise ValueError("budget-envelope SHA-256 mismatch")
    execution = envelope.get("execution", {})
    unsafe_true = (
        "transaction_created", "transaction_signed", "transaction_submitted",
        "broadcast_allowed", "financial_effect", "settlement_executed",
        "burn_executed", "treasury_migrated", "dao_decision_executed",
        "private_key_used",
    )
    for key in unsafe_true:
        if execution.get(key) is not False:
            raise ValueError(f"unsafe budget-envelope execution flag: {key}")
    if execution.get("wave_mawja_untouched") is not True:
        raise ValueError("WAVE isolation flag is not preserved")
    return digest


def _allocations(envelope: Dict[str, Any]) -> Dict[Tuple[str, str], int]:
    result: Dict[Tuple[str, str], int] = {}
    for row in envelope.get("entries", []):
        subject = str(row.get("subject_id", "")).strip()
        wallet = str(row.get("wallet", "")).strip()
        if not subject or not wallet:
            raise ValueError("budget envelope contains blank subject/wallet")
        key = (subject, wallet)
        if key in result:
            raise ValueError("budget envelope contains duplicate subject/wallet")
        result[key] = _positive_raw(row.get("amount_raw"), "envelope entry amount_raw")
    if not result:
        raise ValueError("budget envelope contains no allocations")
    declared_total = _positive_raw(
        envelope.get("budget_controls", {}).get("total_requested_raw"),
        "budget_controls.total_requested_raw",
    )
    if sum(result.values()) != declared_total:
        raise ValueError("budget-envelope allocation total mismatch")
    return result


def _verify_prior(prior: Dict[str, Any], envelope_sha: str) -> List[Dict[str, Any]]:
    if prior.get("schema") != "thf-tokenops-budget-reservation-reconciliation/v1":
        raise ValueError("unexpected prior reservation schema")
    if prior.get("network") != CANONICAL_NETWORK or prior.get("mint") != CANONICAL_MINT:
        raise ValueError("prior reservation target mismatch")
    if prior.get("budget_envelope_sha256") != envelope_sha:
        raise ValueError("prior reservation detached from budget envelope")
    digest = prior.get("reservation_reconciliation_sha256")
    if not isinstance(digest, str) or not HEX64.fullmatch(digest):
        raise ValueError("invalid prior reservation SHA-256")
    body = dict(prior)
    body.pop("reservation_reconciliation_sha256", None)
    if canonical_sha256(body) != digest:
        raise ValueError("prior reservation SHA-256 mismatch")
    execution = prior.get("execution", {})
    for key in (
        "transaction_created", "transaction_signed", "transaction_submitted",
        "broadcast_allowed", "financial_effect", "settlement_executed",
        "private_key_used",
    ):
        if execution.get(key) is not False:
            raise ValueError(f"unsafe prior reservation execution flag: {key}")
    return list(prior.get("reservations", []))


def compile_reservation_reconciliation(
    envelope: Dict[str, Any],
    request: Dict[str, Any],
    prior_evidence: Iterable[Dict[str, Any]] = (),
) -> Dict[str, Any]:
    _scan(envelope)
    _scan(request)
    for prior in prior_evidence:
        _scan(prior)

    envelope_sha = _verify_envelope(envelope)
    allocations = _allocations(envelope)
    if request.get("network") != CANONICAL_NETWORK or request.get("mint") != CANONICAL_MINT:
        raise ValueError("reservation request target mismatch")
    if request.get("budget_envelope_sha256") != envelope_sha:
        raise ValueError("reservation request detached from budget envelope")

    used: Dict[Tuple[str, str], int] = {key: 0 for key in allocations}
    seen_ids = set()
    prior_rows: List[Dict[str, Any]] = []
    for prior in prior_evidence:
        for row in _verify_prior(prior, envelope_sha):
            rid = str(row.get("reservation_id", "")).strip()
            key = (str(row.get("subject_id", "")).strip(), str(row.get("wallet", "")).strip())
            if not rid or rid in seen_ids:
                raise ValueError("duplicate/blank prior reservation_id")
            if key not in allocations:
                raise ValueError("prior reservation is not present in budget envelope")
            amount = _positive_raw(row.get("amount_raw"), "prior reservation amount_raw")
            seen_ids.add(rid)
            used[key] += amount
            prior_rows.append({
                "reservation_id": rid,
                "subject_id": key[0],
                "wallet": key[1],
                "amount_raw": str(amount),
            })

    requested_rows: List[Dict[str, Any]] = []
    for row in request.get("reservations", []):
        rid = str(row.get("reservation_id", "")).strip()
        key = (str(row.get("subject_id", "")).strip(), str(row.get("wallet", "")).strip())
        if not rid or rid in seen_ids:
            raise ValueError("duplicate/blank reservation_id")
        if key not in allocations:
            raise ValueError("reservation is not present in budget envelope")
        amount = _positive_raw(row.get("amount_raw"), "reservation amount_raw")
        seen_ids.add(rid)
        used[key] += amount
        requested_rows.append({
            "reservation_id": rid,
            "subject_id": key[0],
            "wallet": key[1],
            "amount_raw": str(amount),
        })

    if not requested_rows:
        raise ValueError("at least one reservation is required")

    blockers = list(envelope.get("blockers", []))
    if envelope.get("review_eligible") is not True:
        blockers.append("budget_envelope_not_review_eligible")

    allocation_status = []
    for key in sorted(allocations):
        allocated = allocations[key]
        reserved = used[key]
        remaining = allocated - reserved
        if remaining < 0:
            blockers.append(f"budget_allocation_exceeded:{key[0]}")
        allocation_status.append({
            "subject_id": key[0],
            "wallet": key[1],
            "allocated_raw": str(allocated),
            "reserved_raw": str(reserved),
            "remaining_raw": str(max(remaining, 0)),
            "within_allocation": remaining >= 0,
        })

    envelope_total = sum(allocations.values())
    reserved_total = sum(used.values())
    if reserved_total > envelope_total:
        blockers.append("budget_envelope_total_exceeded")

    blockers = sorted(set(str(x) for x in blockers))
    result: Dict[str, Any] = {
        "schema": "thf-tokenops-budget-reservation-reconciliation/v1",
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "intent": envelope.get("intent"),
        "request_id": str(request.get("request_id", "")),
        "budget_envelope_sha256": envelope_sha,
        "bound_admission_sha256": envelope.get("bound_admission_sha256"),
        "policy_completion_evidence_sha256": envelope.get("policy_completion_evidence_sha256"),
        "prior_reservation_count": len(prior_rows),
        "new_reservation_count": len(requested_rows),
        "reservations": sorted(prior_rows + requested_rows, key=lambda x: x["reservation_id"]),
        "allocation_status": allocation_status,
        "accounting": {
            "budget_total_raw": str(envelope_total),
            "reserved_total_raw": str(reserved_total),
            "remaining_budget_raw": str(max(envelope_total - reserved_total, 0)),
            "overcommitted": reserved_total > envelope_total or any(not x["within_allocation"] for x in allocation_status),
        },
        "reservation_review_eligible": len(blockers) == 0,
        "blockers": blockers,
        "execution": {
            "transaction_created": False,
            "transaction_signed": False,
            "transaction_submitted": False,
            "broadcast_allowed": False,
            "financial_effect": False,
            "settlement_executed": False,
            "private_key_used": False,
            "external_multisig_required": True,
            "wave_mawja_untouched": True,
        },
    }
    result["reservation_reconciliation_sha256"] = canonical_sha256(result)
    return result
