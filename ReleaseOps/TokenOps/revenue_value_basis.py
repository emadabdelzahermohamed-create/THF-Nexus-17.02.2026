#!/usr/bin/env python3
"""Deterministic, evidence-bound revenue-to-THF planning for TokenOps.

This module is deliberately non-executing. It validates an approved value-basis
record and can derive a review-only THF_RAW budget for the approved 35% revenue
share. It never fetches a price, selects an exchange rate, builds transaction
bytes, signs, broadcasts, or changes financial state.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from typing import Any, Dict, Optional

NETWORK = "solana-mainnet-beta"
MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
TARGET_UNIT = "THF_RAW"
SHARE_BPS = 3500

FORBIDDEN_FIELDS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signatures", "signed_transaction", "raw_transaction",
    "serialized_transaction", "transaction_bytes", "instruction_bytes",
    "service_account_key", "access_token", "refresh_token",
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha256(value: Any) -> str:
    if isinstance(value, bytes):
        data = value
    elif isinstance(value, str):
        data = value.encode()
    else:
        data = canonical_json(value)
    return hashlib.sha256(data).hexdigest()


def scan_sensitive(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_FIELDS:
                raise ValueError(f"forbidden sensitive field at {path}.{key}")
            scan_sensitive(item, f"{path}.{key}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            scan_sensitive(item, f"{path}[{i}]")


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _parse_utc(value: Any) -> Optional[dt.datetime]:
    if not isinstance(value, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(dt.timezone.utc)


def validate_basis_evidence(
    policy: Dict[str, Any],
    evidence: Optional[Dict[str, Any]],
    *,
    now_utc: Optional[dt.datetime] = None,
) -> Dict[str, Any]:
    """Validate that policy approval is bound to one immutable value-basis record."""
    scan_sensitive(policy)
    if evidence is not None:
        scan_sensitive(evidence)

    dc = policy.get("distribution_controls") or {}
    blockers = []
    status = dc.get("revenue_value_basis_status")
    expected_hash = dc.get("revenue_value_basis_evidence_sha256")

    if status != "approved":
        blockers.append("revenue_value_basis_not_approved")
    if not _valid_sha(expected_hash):
        blockers.append("policy_value_basis_evidence_hash_missing")
    if evidence is None:
        blockers.append("value_basis_evidence_missing")
        actual_hash = None
    else:
        actual_hash = sha256(evidence)
        if _valid_sha(expected_hash) and actual_hash != expected_hash:
            blockers.append("value_basis_evidence_hash_mismatch")
        if evidence.get("schema") != "thf-tokenops-revenue-value-basis/v1":
            blockers.append("unsupported_value_basis_schema")
        if evidence.get("network") != NETWORK:
            blockers.append("network_mismatch")
        if evidence.get("mint") != MINT:
            blockers.append("mint_mismatch")
        if evidence.get("token_program") != TOKEN_PROGRAM:
            blockers.append("token_program_mismatch")
        if evidence.get("target_unit") != TARGET_UNIT:
            blockers.append("target_unit_must_be_thf_raw")
        source_unit = evidence.get("source_unit")
        if not isinstance(source_unit, str) or not source_unit:
            blockers.append("source_unit_missing")
        method = evidence.get("method")
        if source_unit == TARGET_UNIT:
            if method != "identity_thf_raw":
                blockers.append("identity_method_required_for_thf_raw")
        else:
            if method != "approved_rational_conversion":
                blockers.append("approved_rational_conversion_required")
            numerator = evidence.get("thf_raw_numerator")
            denominator = evidence.get("source_minor_denominator")
            if not isinstance(numerator, int) or numerator <= 0:
                blockers.append("invalid_thf_raw_numerator")
            if not isinstance(denominator, int) or denominator <= 0:
                blockers.append("invalid_source_minor_denominator")
            if not _valid_sha(evidence.get("conversion_source_evidence_sha256")):
                blockers.append("conversion_source_evidence_missing")

        if not _valid_sha(evidence.get("governance_approval_evidence_sha256")):
            blockers.append("governance_approval_evidence_missing")

        observed = _parse_utc(evidence.get("observed_at_utc"))
        expires = _parse_utc(evidence.get("expires_at_utc"))
        if observed is None:
            blockers.append("invalid_observed_at_utc")
        if expires is None:
            blockers.append("invalid_expires_at_utc")
        if observed is not None and expires is not None and expires <= observed:
            blockers.append("invalid_evidence_validity_window")
        now = now_utc or dt.datetime.now(dt.timezone.utc)
        if now.tzinfo is None:
            raise ValueError("now_utc must be timezone-aware")
        now = now.astimezone(dt.timezone.utc)
        if observed is not None and now < observed:
            blockers.append("value_basis_not_yet_valid")
        if expires is not None and now > expires:
            blockers.append("value_basis_evidence_expired")

    result = {
        "schema": "thf-tokenops-value-basis-validation/v1",
        "status": "PASS_REVIEW_ONLY" if not blockers else "FAIL_CLOSED",
        "network": NETWORK,
        "mint": MINT,
        "token_program": TOKEN_PROGRAM,
        "policy_status": status,
        "expected_evidence_sha256": expected_hash,
        "actual_evidence_sha256": actual_hash,
        "blockers": sorted(set(blockers)),
        "execution_authorized": False,
        "transaction_bytes_created": False,
        "signed": False,
        "submitted": False,
        "broadcast": False,
        "financial_effect": False,
    }
    result["validation_sha256"] = sha256(result)
    return result


def derive_35pct_thf_budget(
    policy: Dict[str, Any],
    evidence: Dict[str, Any],
    revenue_amount_minor: int,
    *,
    now_utc: Optional[dt.datetime] = None,
) -> Dict[str, Any]:
    """Derive a deterministic review-only THF_RAW budget with integer arithmetic."""
    if not isinstance(revenue_amount_minor, int) or revenue_amount_minor < 0:
        raise ValueError("revenue_amount_minor must be a nonnegative integer")
    validation = validate_basis_evidence(policy, evidence, now_utc=now_utc)
    source_share_minor = revenue_amount_minor * SHARE_BPS // 10000
    budget_raw = None
    conversion_remainder_numerator = None

    if validation["status"] == "PASS_REVIEW_ONLY":
        if evidence["source_unit"] == TARGET_UNIT:
            budget_raw = source_share_minor
            conversion_remainder_numerator = 0
        else:
            numerator = int(evidence["thf_raw_numerator"])
            denominator = int(evidence["source_minor_denominator"])
            product = source_share_minor * numerator
            budget_raw = product // denominator
            conversion_remainder_numerator = product % denominator

    result = {
        "schema": "thf-tokenops-35pct-budget-derivation/v1",
        "status": "REVIEW_READY_NOT_EXECUTION_READY" if budget_raw is not None else "FAIL_CLOSED",
        "network": NETWORK,
        "mint": MINT,
        "token_program": TOKEN_PROGRAM,
        "approved_share_bps": SHARE_BPS,
        "revenue_amount_minor": revenue_amount_minor,
        "source_unit": evidence.get("source_unit"),
        "share_in_source_minor": source_share_minor,
        "proposed_thf_budget_raw": budget_raw,
        "conversion_remainder_numerator": conversion_remainder_numerator,
        "value_basis_validation_sha256": validation["validation_sha256"],
        "value_basis_evidence_sha256": validation["actual_evidence_sha256"],
        "blockers": validation["blockers"],
        "rounding_policy": "integer_floor_no_redistribution",
        "execution_authorized": False,
        "transaction_bytes_created": False,
        "signed": False,
        "submitted": False,
        "broadcast": False,
        "financial_effect": False,
    }
    result["derivation_sha256"] = sha256(result)
    return result
