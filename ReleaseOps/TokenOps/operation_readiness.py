#!/usr/bin/env python3
"""Per-operation fail-closed readiness compiler for THF TokenOps.

This module is planning/evidence-only. It never creates Solana instructions,
transactions, signatures, or broadcast payloads and never accepts private-key
material. It converts the global authoritative readiness state plus public
read-only treasury evidence into an operation-specific control matrix.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List

from ReleaseOps.TokenOps.financial_control_plane import (
    DECIMALS,
    MINT,
    NETWORK,
    SUPPLY_FLOOR_RAW,
    TOKEN_PROGRAM,
    scan_sensitive,
    validate_treasury_registry,
)

SCHEMA = "thf-tokenops-operation-readiness/v1"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


# These are policy/evidence prerequisites, not signer approvals.  They are kept
# intentionally explicit so a new blocker cannot silently disappear from an
# operation's gate.
OPERATION_REQUIREMENTS: Dict[str, Dict[str, Any]] = {
    "reward_epoch": {
        "approval_class": "reward_epoch",
        "required_roles": ["distribution_reserve"],
        "blockers": [
            "distribution_delivery_model_not_approved",
            "distribution_reserve_not_approved",
            "epoch_budget_cap_not_approved",
            "per_user_cap_not_approved",
            "revenue_value_basis_not_approved",
            "treasury_accounts_and_evidence_missing",
            "production_signer_policy_not_approved",
        ],
    },
    "lock_reward": {
        "approval_class": "reward_epoch",
        "required_roles": ["lock_reward_reserve"],
        "blockers": [
            "lock_rewards_terms_not_approved",
            "lock_terms_not_approved",
            "treasury_accounts_and_evidence_missing",
            "production_signer_policy_not_approved",
        ],
    },
    "vesting_settlement": {
        "approval_class": "vesting_settlement",
        "required_roles": ["vesting_reserve"],
        "blockers": [
            "vesting_terms_not_approved",
            "treasury_accounts_and_evidence_missing",
            "production_signer_policy_not_approved",
        ],
    },
    "burn": {
        "approval_class": "burn",
        "required_roles": ["burn_reserve"],
        "blockers": [
            "treasury_accounts_and_evidence_missing",
            "production_signer_policy_not_approved",
        ],
    },
    "treasury_transfer": {
        "approval_class": "treasury_transfer",
        "required_roles_any": ["dao_treasury", "operations"],
        "blockers": [
            "treasury_accounts_and_evidence_missing",
            "production_signer_policy_not_approved",
        ],
    },
}


def _minimum_approvals(treasury_policy: Dict[str, Any], approval_class: str) -> int:
    cls = (treasury_policy.get("approval_classes") or {}).get(approval_class)
    if not isinstance(cls, dict):
        raise ValueError(f"missing approval class: {approval_class}")
    n = cls.get("minimum_approvals")
    if not isinstance(n, int) or n <= 0:
        raise ValueError(f"invalid approval threshold: {approval_class}")
    if cls.get("execution") != "external_multisig":
        raise ValueError(f"unsupported execution model: {approval_class}")
    return n


def _assert_identity(readiness: Dict[str, Any], treasury_policy: Dict[str, Any], registry: Dict[str, Any]) -> None:
    expected = {"network": NETWORK, "mint": MINT}
    for label, obj in (("readiness", readiness), ("treasury_policy", treasury_policy), ("treasury_registry", registry)):
        for key, value in expected.items():
            if obj.get(key) != value:
                raise ValueError(f"{label}:{key}_mismatch")


def build_operation_matrix(
    readiness: Dict[str, Any],
    treasury_policy: Dict[str, Any],
    registry: Dict[str, Any],
    *,
    observed_slot: int,
    current_supply_raw: int,
    max_slot_lag: int = 5000,
) -> Dict[str, Any]:
    """Compile deterministic per-operation readiness from public evidence only."""
    scan_sensitive(readiness)
    scan_sensitive(treasury_policy)
    scan_sensitive(registry)
    _assert_identity(readiness, treasury_policy, registry)

    if not isinstance(observed_slot, int) or observed_slot <= 0:
        raise ValueError("observed_slot must be a positive integer")
    if not isinstance(current_supply_raw, int) or current_supply_raw < 0:
        raise ValueError("current_supply_raw must be a nonnegative integer")

    treasury = validate_treasury_registry(registry, observed_slot=observed_slot, max_slot_lag=max_slot_lag)
    global_blockers = sorted(set(str(x) for x in readiness.get("blockers", [])))
    role_balances = {k: int(v) for k, v in (treasury.get("role_balances_raw") or {}).items()}

    operations: Dict[str, Any] = {}
    signer_candidates: List[str] = []

    for name, requirement in OPERATION_REQUIREMENTS.items():
        approval_class = requirement["approval_class"]
        threshold = _minimum_approvals(treasury_policy, approval_class)
        open_blockers = sorted(x for x in requirement.get("blockers", []) if x in global_blockers)
        evidence_blockers: List[str] = []

        if treasury.get("status") != "PASS":
            evidence_blockers.append("treasury_registry_not_verified")

        for role in requirement.get("required_roles", []):
            if role_balances.get(role, 0) <= 0:
                evidence_blockers.append(f"treasury_role_missing_or_empty:{role}")

        any_roles = requirement.get("required_roles_any", [])
        if any_roles and not any(role_balances.get(role, 0) > 0 for role in any_roles):
            evidence_blockers.append("treasury_role_missing_or_empty:any_of:" + ",".join(any_roles))

        # Burn review capacity is bounded by BOTH the approved supply floor and
        # verified burn-reserve holdings.  It is never an authorization.
        review_cap_raw = None
        if name == "burn":
            headroom = max(0, current_supply_raw - SUPPLY_FLOOR_RAW)
            burn_balance = role_balances.get("burn_reserve", 0)
            review_cap_raw = str(min(headroom, burn_balance)) if treasury.get("status") == "PASS" else None
            if current_supply_raw < SUPPLY_FLOOR_RAW:
                evidence_blockers.append("supply_below_approved_floor")

        blockers = sorted(set(open_blockers + evidence_blockers))
        if blockers:
            status = "FAIL_CLOSED"
            signer_action = "NONE"
        else:
            status = "AWAITING_USER_CONTROLLED_MULTISIG_APPROVAL"
            signer_action = f"USER_CONTROLLED_MULTISIG_APPROVAL_REQUIRED:{threshold}:{approval_class}"
            signer_candidates.append(signer_action)

        operations[name] = {
            "status": status,
            "approval_class": approval_class,
            "minimum_approvals": threshold,
            "policy_blockers": open_blockers,
            "evidence_blockers": sorted(set(evidence_blockers)),
            "required_roles": requirement.get("required_roles", []),
            "required_roles_any": any_roles,
            "review_cap_raw": review_cap_raw,
            "exact_signer_action": signer_action,
            "execution_authorized": False,
            "signed": False,
            "submitted": False,
            "broadcast": False,
            "financial_effect": False,
            "transaction_bytes_created": False,
            "instruction_bytes_created": False,
        }

    unknown_global = sorted(
        b for b in global_blockers
        if not any(b in req.get("blockers", []) for req in OPERATION_REQUIREMENTS.values())
    )
    # policy-mutation governance is deliberately global, rather than attached
    # to routine financial intents. It keeps policy changes fail-closed without
    # falsely requiring a policy mutation for every ordinary reward/burn review.
    known_global_only = {"policy_mutation_governance_not_approved"}
    truly_unmapped = sorted(b for b in unknown_global if b not in known_global_only)

    overall_status = "FAIL_CLOSED" if any(v["status"] == "FAIL_CLOSED" for v in operations.values()) or truly_unmapped else "AWAITING_USER_CONTROLLED_MULTISIG_APPROVAL"
    exact_signer_action = "NONE" if overall_status == "FAIL_CLOSED" else ";".join(sorted(set(signer_candidates)))

    result = {
        "schema": SCHEMA,
        "network": NETWORK,
        "mint": MINT,
        "token_program": TOKEN_PROGRAM,
        "decimals": DECIMALS,
        "observed_slot": observed_slot,
        "current_supply_raw": str(current_supply_raw),
        "supply_floor_raw": str(SUPPLY_FLOOR_RAW),
        "status": overall_status,
        "global_blockers": global_blockers,
        "global_policy_only_blockers": sorted(b for b in unknown_global if b in known_global_only),
        "unmapped_global_blockers": truly_unmapped,
        "treasury_reconciliation": treasury,
        "operations": operations,
        "exact_signer_action_now": exact_signer_action,
        "execution_authorized": False,
        "signed": False,
        "submitted": False,
        "broadcast": False,
        "financial_effect": False,
        "private_key_required": False,
        "wave_touched": False,
    }
    result["matrix_sha256"] = _sha256(result)
    return result


def summarize_matrix(matrix: Dict[str, Any]) -> Dict[str, Any]:
    """Small deterministic summary suitable for CI/logs without sensitive data."""
    ops = matrix.get("operations") or {}
    result = {
        "schema": "thf-tokenops-operation-readiness-summary/v1",
        "status": matrix.get("status"),
        "operation_statuses": {name: data.get("status") for name, data in sorted(ops.items())},
        "operation_blocker_counts": {
            name: len(set(data.get("policy_blockers", []) + data.get("evidence_blockers", [])))
            for name, data in sorted(ops.items())
        },
        "unmapped_global_blocker_count": len(matrix.get("unmapped_global_blockers", [])),
        "exact_signer_action_now": matrix.get("exact_signer_action_now", "NONE"),
        "execution_authorized": False,
        "broadcast": False,
        "financial_effect": False,
    }
    result["summary_sha256"] = _sha256(result)
    return result
