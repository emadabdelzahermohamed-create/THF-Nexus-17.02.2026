#!/usr/bin/env python3
"""Deterministic THF reward/vesting budget-envelope compiler.

Review/accounting only. This module never constructs a Solana transaction and never
signs, submits, broadcasts, transfers, burns, changes authorities, settles rewards
or vesting, migrates treasury balances, or executes governance decisions.
"""
from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal, ROUND_DOWN
from typing import Any, Dict, List

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
CANONICAL_NETWORK = "solana-mainnet-beta"
EXPECTED_BOUND_GATE = "THF_TOKENOPS_POLICY_COMPLETION_BOUND_UNSIGNED_ADMISSION_V1"
BPS_DENOM = 10_000
ACTIVE_USER_SHARE_BPS = 3_500
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "raw_transaction", "serialized_transaction"
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


def _nonnegative_raw(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be an integer raw-token amount")
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str) and value.isdigit():
        parsed = int(value)
    else:
        raise ValueError(f"{label} must be an integer raw-token amount")
    if parsed < 0:
        raise ValueError(f"{label} cannot be negative")
    return parsed


def _configured_cap(value: Any, label: str) -> int | None:
    if value is None:
        return None
    parsed = _nonnegative_raw(value, label)
    if parsed <= 0:
        raise ValueError(f"{label} must be positive when configured")
    return parsed


def _verify_bound_admission(bound: Dict[str, Any]) -> str:
    if bound.get("gate") != EXPECTED_BOUND_GATE:
        raise ValueError("unexpected bound-admission gate")
    if bound.get("network") != CANONICAL_NETWORK or bound.get("mint") != CANONICAL_MINT:
        raise ValueError("bound-admission target mismatch")
    digest = bound.get("bound_admission_sha256")
    if not isinstance(digest, str) or not HEX64.fullmatch(digest):
        raise ValueError("invalid bound-admission SHA-256")
    body = dict(bound)
    body.pop("bound_admission_sha256", None)
    if canonical_sha256(body) != digest:
        raise ValueError("bound-admission SHA-256 mismatch")
    for key in (
        "simulation_execution_permitted", "execution_authorized", "transaction_created",
        "transaction_signed", "transaction_submitted", "broadcast_allowed", "financial_effect",
        "private_key_used",
    ):
        if bound.get(key) is not False:
            raise ValueError(f"unsafe bound-admission flag: {key}")
    if bound.get("wave_mawja_untouched") is not True:
        raise ValueError("WAVE isolation flag is not preserved")
    return digest


def _normalize_entries(intent: str, entries: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], int, List[str]]:
    normalized: List[Dict[str, Any]] = []
    blockers: List[str] = []
    total = 0
    seen = set()
    for row in entries:
        subject = str(row.get("subject_id", "")).strip()
        wallet = str(row.get("wallet", "")).strip()
        if not subject or not wallet:
            raise ValueError("each entry requires subject_id and wallet")
        identity = (subject, wallet)
        if identity in seen:
            raise ValueError("duplicate subject_id/wallet entry")
        seen.add(identity)
        amount = _nonnegative_raw(row.get("amount_raw"), "entry.amount_raw")
        if amount <= 0:
            raise ValueError("entry.amount_raw must be positive")
        item: Dict[str, Any] = {
            "subject_id": subject,
            "wallet": wallet,
            "amount_raw": str(amount),
        }
        if intent == "vesting_settlement":
            start = int(row.get("start_unix"))
            cliff = int(row.get("cliff_unix", start))
            end = int(row.get("end_unix"))
            if not (0 <= start <= cliff <= end):
                raise ValueError("invalid vesting timeline")
            item.update({"start_unix": start, "cliff_unix": cliff, "end_unix": end})
        total += amount
        normalized.append(item)
    normalized.sort(key=lambda x: (x["subject_id"], x["wallet"], x["amount_raw"]))
    return normalized, total, blockers


def compile_budget_envelope(
    bound_admission: Dict[str, Any],
    authoritative_policy: Dict[str, Any],
    treasury_policy: Dict[str, Any],
    request: Dict[str, Any],
) -> Dict[str, Any]:
    for value in (bound_admission, authoritative_policy, treasury_policy, request):
        _scan(value)

    bound_sha = _verify_bound_admission(bound_admission)
    if request.get("network") != CANONICAL_NETWORK or request.get("mint") != CANONICAL_MINT:
        raise ValueError("request target mismatch")
    if request.get("bound_admission_sha256") != bound_sha:
        raise ValueError("request/bound-admission SHA-256 mismatch")
    if authoritative_policy.get("network") != CANONICAL_NETWORK or authoritative_policy.get("mint") != CANONICAL_MINT:
        raise ValueError("authoritative policy target mismatch")
    if treasury_policy.get("network") != CANONICAL_NETWORK or treasury_policy.get("mint") != CANONICAL_MINT:
        raise ValueError("treasury policy target mismatch")

    economics = authoritative_policy.get("economics", {})
    share = Decimal(str(economics.get("active_user_revenue_share")))
    if share != Decimal("0.35"):
        raise ValueError("authoritative active-user revenue share must remain exactly 35%")
    if str(economics.get("approved_supply_floor_target_ui")) != "8000000000":
        raise ValueError("authoritative burn supply floor/target must remain 8B THF")

    intent = str(request.get("intent", ""))
    if intent not in {"reward_epoch", "vesting_settlement"}:
        raise ValueError("unsupported budget-envelope intent")
    approval_class = treasury_policy.get("approval_classes", {}).get(intent)
    if not isinstance(approval_class, dict) or approval_class.get("execution") != "external_multisig":
        raise ValueError("missing external-multisig approval class")

    entries, total_requested, blockers = _normalize_entries(intent, list(request.get("entries", [])))
    controls = authoritative_policy.get("distribution_controls", {})
    per_user_cap = _configured_cap(controls.get("per_user_cap"), "distribution_controls.per_user_cap")
    epoch_budget_cap = _configured_cap(controls.get("epoch_budget_cap"), "distribution_controls.epoch_budget_cap")

    if per_user_cap is None:
        blockers.append("anti_whale_per_user_cap_not_authoritatively_configured")
    if epoch_budget_cap is None:
        blockers.append("epoch_budget_cap_not_authoritatively_configured")
    if bound_admission.get("simulation_review_eligible") is not True:
        blockers.append("bound_admission_not_review_eligible")
        blockers.extend(f"bound_admission:{x}" for x in bound_admission.get("blockers", []))

    if per_user_cap is not None:
        for item in entries:
            if int(item["amount_raw"]) > per_user_cap:
                blockers.append(f"per_user_cap_exceeded:{item['subject_id']}")
    if epoch_budget_cap is not None and total_requested > epoch_budget_cap:
        blockers.append("epoch_budget_cap_exceeded")

    revenue: Dict[str, Any] | None = None
    if intent == "reward_epoch":
        revenue_minor = _nonnegative_raw(request.get("epoch_revenue_minor"), "epoch_revenue_minor")
        active_share_minor = revenue_minor * ACTIVE_USER_SHARE_BPS // BPS_DENOM
        revenue = {
            "epoch_revenue_minor": str(revenue_minor),
            "active_user_share_bps": ACTIVE_USER_SHARE_BPS,
            "active_user_share_minor": str(active_share_minor),
            "token_price_inferred": False,
            "note": "Revenue accounting is separate from token-denominated budget accounting.",
        }

    blockers = sorted(set(blockers))
    result: Dict[str, Any] = {
        "schema": "thf-tokenops-reward-vesting-budget-envelope/v1",
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "intent": intent,
        "request_id": str(request.get("request_id", "")),
        "bound_admission_sha256": bound_sha,
        "policy_completion_evidence_sha256": bound_admission.get("policy_completion_evidence_sha256"),
        "economics": {
            "active_user_revenue_share_bps": ACTIVE_USER_SHARE_BPS,
            "approved_supply_floor_target_ui": "8000000000",
            "burn_source_policy": economics.get("burn_source_policy"),
        },
        "budget_controls": {
            "per_user_cap_raw": None if per_user_cap is None else str(per_user_cap),
            "epoch_budget_cap_raw": None if epoch_budget_cap is None else str(epoch_budget_cap),
            "total_requested_raw": str(total_requested),
            "caps_authoritatively_configured": per_user_cap is not None and epoch_budget_cap is not None,
        },
        "approval_requirement": {
            "minimum_approvals": int(approval_class.get("minimum_approvals", 0)),
            "execution": "external_multisig",
            "approval_satisfied_here": False,
        },
        "revenue": revenue,
        "entries": entries,
        "review_eligible": len(blockers) == 0,
        "blockers": blockers,
        "execution": {
            "transaction_created": False,
            "transaction_signed": False,
            "transaction_submitted": False,
            "broadcast_allowed": False,
            "financial_effect": False,
            "settlement_executed": False,
            "burn_executed": False,
            "treasury_migrated": False,
            "dao_decision_executed": False,
            "private_key_used": False,
            "wave_mawja_untouched": True,
        },
    }
    result["envelope_sha256"] = canonical_sha256(result)
    return result
