#!/usr/bin/env python3
"""Deterministic, non-broadcast THF TokenOps epoch commitment helpers.

This module creates review/evidence objects only. It never signs, serializes,
submits, or broadcasts a Solana transaction and never accepts key material.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK = "solana-mainnet-beta"
SHARE_BPS = 3500
FORBIDDEN = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signatures", "signed_transaction", "raw_transaction",
    "serialized_transaction", "transaction_bytes", "instruction_bytes",
    "access_token", "refresh_token", "service_account_key",
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha256(value: Any) -> str:
    data = value if isinstance(value, bytes) else canonical_json(value)
    return hashlib.sha256(data).hexdigest()


def reject_sensitive(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN:
                raise ValueError(f"forbidden sensitive field at {path}.{key}")
            reject_sensitive(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_sensitive(child, f"{path}[{index}]")


def _unique_subjects(rows: List[Dict[str, Any]]) -> None:
    refs = [row.get("subject_ref") for row in rows]
    if any(not isinstance(ref, str) or not ref.strip() for ref in refs):
        raise ValueError("subject_ref must be a non-empty opaque reference")
    if len(set(refs)) != len(refs):
        raise ValueError("duplicate subject_ref")


def deterministic_capped_allocation(
    budget_raw: int,
    per_user_cap_raw: int,
    eligible: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Allocate deterministically while preserving the cap and conservation.

    Proportional floor allocation is followed by at most one largest-remainder
    residual pass. A large cap-induced residual is intentionally left
    unallocated instead of being silently redistributed with changed economics.
    That residual becomes a review blocker in the epoch commitment.
    """
    reject_sensitive(eligible)
    if budget_raw < 0 or per_user_cap_raw < 0:
        raise ValueError("budget and cap must be nonnegative")
    _unique_subjects(eligible)
    units = []
    for row in eligible:
        u = row.get("activity_units")
        if not isinstance(u, int) or u < 0:
            raise ValueError("activity_units must be a nonnegative integer")
        units.append(u)
    total_units = sum(units)
    if total_units == 0 or budget_raw == 0 or per_user_cap_raw == 0:
        return {
            "allocations": [{"subject_ref": r["subject_ref"], "amount_raw": 0} for r in sorted(eligible, key=lambda x: x["subject_ref"])],
            "allocated_raw": 0,
            "unallocated_raw": budget_raw,
            "conservation": True,
        }

    work = []
    for row in eligible:
        numerator = budget_raw * row["activity_units"]
        floor_share, remainder = divmod(numerator, total_units)
        work.append({
            "subject_ref": row["subject_ref"],
            "amount_raw": min(floor_share, per_user_cap_raw),
            "remainder": remainder,
        })

    allocated = sum(x["amount_raw"] for x in work)
    remaining = budget_raw - allocated

    # Normal proportional rounding residue is < number of subjects. We perform
    # one deterministic largest-remainder pass only; cap-induced excess remains
    # explicitly unallocated and therefore cannot mutate the approved formula.
    for row in sorted(work, key=lambda x: (-x["remainder"], x["subject_ref"])):
        if remaining <= 0:
            break
        if row["amount_raw"] < per_user_cap_raw:
            row["amount_raw"] += 1
            remaining -= 1

    allocations = [
        {"subject_ref": x["subject_ref"], "amount_raw": x["amount_raw"]}
        for x in sorted(work, key=lambda x: x["subject_ref"])
    ]
    allocated = sum(x["amount_raw"] for x in allocations)
    return {
        "allocations": allocations,
        "allocated_raw": allocated,
        "unallocated_raw": budget_raw - allocated,
        "conservation": allocated + (budget_raw - allocated) == budget_raw,
    }


def build_epoch_commitment(
    policy: Dict[str, Any],
    treasury_validation: Dict[str, Any],
    epoch_id: str,
    recognized_revenue_minor: int,
    eligible: List[Dict[str, Any]],
    evidence_sha256: Iterable[str],
) -> Dict[str, Any]:
    """Build a deterministic review packet for the approved 35% policy."""
    reject_sensitive(policy)
    reject_sensitive(treasury_validation)
    reject_sensitive(eligible)
    if recognized_revenue_minor < 0:
        raise ValueError("recognized_revenue_minor must be nonnegative")
    if not isinstance(epoch_id, str) or not epoch_id.strip():
        raise ValueError("epoch_id must be non-empty")
    _unique_subjects(eligible)

    blockers = []
    if policy.get("network") != NETWORK or policy.get("mint") != MINT:
        blockers.append("canonical_identity_mismatch")
    economics = policy.get("economics") or {}
    if economics.get("active_user_revenue_share_bps") != SHARE_BPS:
        blockers.append("approved_share_policy_mismatch")
    controls = policy.get("distribution_controls") or {}
    required = ("per_user_cap_raw", "epoch_budget_cap_raw", "distribution_reserve_account", "delivery_model")
    for field in required:
        if controls.get(field) is None:
            blockers.append(f"{field}_not_approved")
    if controls.get("delivery_model") not in (None, "claim", "push", "hybrid"):
        blockers.append("unsupported_delivery_model")
    if treasury_validation.get("status") != "PASS":
        blockers.append("treasury_registry_not_verified")
    if not eligible:
        blockers.append("eligible_population_empty")
    if eligible and sum(int(x.get("activity_units", -1)) for x in eligible if isinstance(x.get("activity_units"), int)) == 0:
        blockers.append("eligible_activity_units_zero")
    for row in eligible:
        if not isinstance(row.get("activity_units"), int) or row["activity_units"] < 0:
            blockers.append("invalid_activity_units")
            break

    evidence = sorted(set(evidence_sha256))
    if not evidence:
        blockers.append("evidence_chain_empty")
    if any(not isinstance(x, str) or len(x) != 64 or any(c not in "0123456789abcdef" for c in x) for x in evidence):
        raise ValueError("invalid evidence sha256")

    approved_pool = recognized_revenue_minor * SHARE_BPS // 10000
    allocation = {"allocations": [], "allocated_raw": 0, "unallocated_raw": approved_pool, "conservation": True}
    effective_budget = None
    if not blockers:
        per_user_cap = int(controls["per_user_cap_raw"])
        epoch_cap = int(controls["epoch_budget_cap_raw"])
        reserve_raw = int((treasury_validation.get("role_balances_raw") or {}).get("distribution_reserve", "0"))
        if per_user_cap < 0 or epoch_cap < 0 or reserve_raw < 0:
            blockers.append("negative_financial_control")
        else:
            effective_budget = min(approved_pool, epoch_cap, reserve_raw)
            allocation = deterministic_capped_allocation(effective_budget, per_user_cap, eligible)
            if allocation["unallocated_raw"]:
                blockers.append("budget_not_fully_allocated_due_to_caps_or_zero_activity")

    packet = {
        "schema": "thf-tokenops-epoch-commitment/v1",
        "network": NETWORK,
        "mint": MINT,
        "epoch_id": epoch_id,
        "approved_share_bps": SHARE_BPS,
        "recognized_revenue_minor": recognized_revenue_minor,
        "approved_pool_minor": approved_pool,
        "effective_budget_raw": effective_budget,
        "allocation": allocation,
        "evidence_sha256": evidence,
        "status": "FAIL_CLOSED" if blockers else "REVIEW_READY_NOT_EXECUTION_READY",
        "blockers": sorted(set(blockers)),
        "execution_authorized": False,
        "signed": False,
        "submitted": False,
        "broadcast": False,
        "financial_effect": False,
        "transaction_bytes_created": False,
        "instruction_bytes_created": False,
    }
    packet["commitment_sha256"] = sha256(packet)
    return packet


def build_double_entry_preview(epoch_commitment: Dict[str, Any]) -> Dict[str, Any]:
    """Produce a balanced accounting preview, never a posted ledger entry."""
    reject_sensitive(epoch_commitment)
    amount = int((epoch_commitment.get("allocation") or {}).get("allocated_raw", 0))
    entries = [
        {"account": "active_user_rewards_expense_preview", "debit_raw": amount, "credit_raw": 0},
        {"account": "distribution_reserve_liability_preview", "debit_raw": 0, "credit_raw": amount},
    ]
    debits = sum(x["debit_raw"] for x in entries)
    credits = sum(x["credit_raw"] for x in entries)
    return {
        "schema": "thf-tokenops-accounting-preview/v1",
        "epoch_commitment_sha256": epoch_commitment.get("commitment_sha256"),
        "entries": entries,
        "debits_raw": debits,
        "credits_raw": credits,
        "balanced": debits == credits,
        "posted": False,
        "financial_effect": False,
    }
