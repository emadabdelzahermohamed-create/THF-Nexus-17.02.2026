#!/usr/bin/env python3
"""Deterministic fail-closed blocker-resolution contracts for THF TokenOps.

This module converts authoritative readiness blockers into exact evidence/approval
requirements. It never signs, serializes, submits, broadcasts, transfers, burns,
changes authorities, settles vesting, or executes governance.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Iterable, List

SCHEMA = "thf-tokenops-blocker-resolution/v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


CONTRACTS: Dict[str, Dict[str, Any]] = {
    "per_user_cap_not_approved": {
        "class": "governance_policy",
        "required_fields": ["per_user_cap_raw", "governance_approval_sha256"],
        "constraints": ["per_user_cap_raw must be integer > 0", "approval SHA-256 must be immutable evidence"],
    },
    "epoch_budget_cap_not_approved": {
        "class": "governance_policy",
        "required_fields": ["epoch_budget_cap_raw", "governance_approval_sha256"],
        "constraints": ["epoch_budget_cap_raw must be integer > 0", "epoch cap must not silently override the 35% value-basis budget"],
    },
    "distribution_reserve_not_approved": {
        "class": "treasury_evidence",
        "required_fields": ["token_account", "owner_pubkey", "balance_raw", "observed_slot", "ownership_evidence_sha256", "balance_evidence_sha256"],
        "constraints": ["public keys only", "canonical mint/program/decimals required", "private-key material forbidden"],
    },
    "distribution_delivery_model_not_approved": {
        "class": "governance_policy",
        "required_fields": ["delivery_model", "governance_approval_sha256"],
        "constraints": ["delivery_model must be claim, push, or explicitly specified alternative", "no autonomous execution"],
    },
    "revenue_value_basis_not_approved": {
        "class": "valuation_evidence",
        "required_fields": ["denomination", "method", "source_evidence_sha256", "governance_approval_sha256", "valid_from_utc", "valid_until_utc"],
        "constraints": ["no autonomous market-price selection", "THF_RAW permits identity conversion only", "external denomination requires approved rational conversion"],
    },
    "revenue_value_basis_evidence_missing": {
        "class": "valuation_evidence",
        "required_fields": ["revenue_value_basis_evidence_sha256"],
        "constraints": ["must be lowercase 64-hex SHA-256 bound to the approved value-basis record"],
    },
    "production_signer_policy_not_approved": {
        "class": "signer_governance",
        "required_fields": ["signer_model", "multisig_or_user_controlled", "ci_identity_model", "governance_approval_sha256"],
        "constraints": ["persistent service-account keys forbidden", "prefer WIF/OIDC short-lived CI identity", "final financial signer remains external/user-controlled"],
    },
    "vesting_terms_not_approved": {
        "class": "governance_policy",
        "required_fields": ["vesting_terms_sha256", "governance_approval_sha256"],
        "constraints": ["cliff/unlock schedule must be explicit", "settlement remains non-executable until approvals are satisfied"],
    },
    "lock_terms_not_approved": {
        "class": "governance_policy",
        "required_fields": ["lock_terms_sha256", "governance_approval_sha256"],
        "constraints": ["lock duration and unlock rules must be explicit", "no hidden penalty or discretionary mutation"],
    },
    "lock_rewards_terms_not_approved": {
        "class": "governance_policy",
        "required_fields": ["lock_rewards_terms_sha256", "reward_budget_cap_raw", "governance_approval_sha256"],
        "constraints": ["reward budget must be capped", "rewards must not bypass epoch or treasury solvency controls"],
    },
    "treasury_accounts_and_evidence_missing": {
        "class": "treasury_evidence",
        "required_fields": ["treasury_registry_sha256", "public_token_accounts", "ownership_evidence_sha256", "balance_evidence_sha256"],
        "constraints": ["public account evidence only", "canonical mint/program/decimals and initialized state required", "fresh observed slot required"],
    },
    "policy_mutation_governance_not_approved": {
        "class": "governance_charter",
        "required_fields": ["authority_model", "minimum_approvals", "governance_charter_sha256"],
        "constraints": ["authority model and threshold must be explicit", "policy mutation cannot self-authorize"],
    },
}


def build_resolution_packet(readiness: Dict[str, Any]) -> Dict[str, Any]:
    blockers = sorted(set(str(x) for x in readiness.get("blockers", [])))
    items: List[Dict[str, Any]] = []
    unknown: List[str] = []
    for blocker in blockers:
        base = blocker.split(":", 1)[0]
        contract = CONTRACTS.get(blocker) or CONTRACTS.get(base)
        if contract is None:
            unknown.append(blocker)
            items.append({
                "blocker": blocker,
                "class": "unmapped_fail_closed",
                "required_fields": [],
                "constraints": ["manual control-plane mapping required before readiness can improve"],
                "status": "OPEN",
            })
            continue
        items.append({"blocker": blocker, **contract, "status": "OPEN"})

    packet = {
        "schema": SCHEMA,
        "network": readiness.get("network"),
        "mint": readiness.get("mint"),
        "readiness_sha256": readiness.get("readiness_sha256"),
        "status": "FAIL_CLOSED" if blockers else "NO_OPEN_BLOCKERS",
        "blocker_count": len(blockers),
        "unknown_blockers": unknown,
        "items": items,
        "execution": {
            "review_only": True,
            "execution_authorized": False,
            "transaction_bytes_created": False,
            "instruction_bytes_created": False,
            "signed": False,
            "submitted": False,
            "broadcast": False,
            "financial_effect": False,
            "private_key_required": False,
            "wave_touched": False,
        },
    }
    packet["packet_sha256"] = _sha256(packet)
    return packet


def validate_evidence_record(record: Dict[str, Any]) -> List[str]:
    """Validate a generic evidence record without accepting secrets or signatures."""
    errors: List[str] = []
    forbidden = {"seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair", "signature", "transaction_bytes", "instruction_bytes"}
    for key in record:
        if str(key).lower().replace("-", "_") in forbidden:
            errors.append(f"forbidden_field:{key}")
    for key, value in record.items():
        if key.endswith("_sha256") and value is not None and not SHA256_RE.fullmatch(str(value)):
            errors.append(f"invalid_sha256:{key}")
    return sorted(errors)


def summarize_required_authorizations(packet: Dict[str, Any]) -> Dict[str, Any]:
    classes: Dict[str, int] = {}
    for item in packet.get("items", []):
        classes[item["class"]] = classes.get(item["class"], 0) + 1
    result = {
        "schema": "thf-tokenops-authorization-summary/v1",
        "blocker_count": packet.get("blocker_count", 0),
        "classes": dict(sorted(classes.items())),
        "signer_action_now": "NONE",
        "reason": "Fail-closed policy/evidence blockers must be resolved before any signer handoff.",
        "execution_authorized": False,
        "broadcast": False,
        "financial_effect": False,
    }
    result["summary_sha256"] = _sha256(result)
    return result
