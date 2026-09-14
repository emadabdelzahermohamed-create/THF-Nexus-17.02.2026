#!/usr/bin/env python3
"""Fail-closed governance packet compiler for THF TokenOps policy changes.

Planning/evidence only. This module never mutates policy files, creates Solana
instructions/transactions, signs, submits, broadcasts, or handles private keys.
It turns a proposed public policy delta into a deterministic review packet that
can only advance to external user-controlled governance after authoritative
policy-mutation governance itself has been approved.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List

from ReleaseOps.TokenOps.financial_control_plane import MINT, NETWORK, scan_sensitive

SCHEMA = "thf-tokenops-policy-change-control/v1"
PROPOSAL_SCHEMA = "thf-tokenops-policy-change-proposal/v1"

ALLOWED_POLICY_FILES = {
    "ReleaseOps/TokenOps/policy.json",
    "ReleaseOps/TokenOps/treasury_policy.json",
    "ReleaseOps/TokenOps/integration_contracts.json",
}

# Fields whose relaxation could directly weaken financial safety. A proposal
# may describe them, but the compiler marks them high impact and never applies.
HIGH_IMPACT_TERMS = {
    "active_user_revenue_share_bps",
    "supply_floor_ui",
    "minimum_approvals",
    "production_signer_policy",
    "per_user_cap_raw",
    "epoch_budget_cap_raw",
    "distribution_reserve",
    "delivery_model",
    "revenue_value_basis",
    "vesting_terms",
    "lock_terms",
    "lock_rewards_terms",
}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value.lower())


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for k, v in value.items():
            yield str(k)
            yield from _walk_keys(v)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def _validate_governance(policy: Dict[str, Any]) -> Dict[str, Any]:
    gov = policy.get("policy_mutation_governance") or {}
    status = gov.get("status")
    threshold = gov.get("minimum_approvals")
    authority_model = gov.get("authority_model")
    evidence = gov.get("evidence_sha256")

    blockers: List[str] = []
    if status != "approved":
        blockers.append("policy_mutation_governance_not_approved")
    if not isinstance(threshold, int) or threshold <= 0:
        blockers.append("policy_mutation_minimum_approvals_missing")
    if authority_model != "external_multisig":
        blockers.append("policy_mutation_authority_model_not_external_multisig")
    if not _is_sha256(evidence):
        blockers.append("policy_mutation_evidence_missing")

    return {
        "status": "PASS" if not blockers else "FAIL_CLOSED",
        "minimum_approvals": threshold if isinstance(threshold, int) and threshold > 0 else None,
        "authority_model": authority_model,
        "evidence_sha256": evidence if _is_sha256(evidence) else None,
        "blockers": blockers,
    }


def compile_policy_change_packet(
    treasury_policy: Dict[str, Any], proposal: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate and compile a deterministic non-executable governance packet."""
    scan_sensitive(treasury_policy)
    scan_sensitive(proposal)

    if treasury_policy.get("network") != NETWORK or treasury_policy.get("mint") != MINT:
        raise ValueError("treasury_policy identity mismatch")
    if proposal.get("schema") != PROPOSAL_SCHEMA:
        raise ValueError("unsupported proposal schema")
    if proposal.get("network") != NETWORK or proposal.get("mint") != MINT:
        raise ValueError("proposal identity mismatch")

    target = proposal.get("target_file")
    if target not in ALLOWED_POLICY_FILES:
        raise ValueError("target file outside TokenOps policy allowlist")
    if proposal.get("action") != "review_only_policy_delta":
        raise ValueError("proposal action must be review_only_policy_delta")

    before_sha = proposal.get("before_sha256")
    evidence = proposal.get("rationale_evidence_sha256")
    delta = proposal.get("delta")
    if not _is_sha256(before_sha):
        raise ValueError("before_sha256 required")
    if not _is_sha256(evidence):
        raise ValueError("rationale_evidence_sha256 required")
    if not isinstance(delta, dict) or not delta:
        raise ValueError("non-empty public delta required")

    gov = _validate_governance(treasury_policy)
    changed_keys = sorted(set(_walk_keys(delta)))
    high_impact = sorted(set(changed_keys) & HIGH_IMPACT_TERMS)
    blockers = list(gov["blockers"])

    # This control plane deliberately never makes a proposal executable. Even
    # when governance becomes approved, final policy application remains an
    # explicit human-reviewed repository change after external multisig proof.
    if blockers:
        status = "FAIL_CLOSED"
        next_action = "NONE"
    else:
        status = "AWAITING_USER_CONTROLLED_POLICY_MULTISIG_APPROVAL"
        next_action = f"USER_CONTROLLED_POLICY_MULTISIG_APPROVAL_REQUIRED:{gov['minimum_approvals']}"

    packet: Dict[str, Any] = {
        "schema": SCHEMA,
        "network": NETWORK,
        "mint": MINT,
        "target_file": target,
        "before_sha256": before_sha,
        "rationale_evidence_sha256": evidence,
        "proposal_id": proposal.get("proposal_id"),
        "delta_sha256": _sha(delta),
        "changed_keys": changed_keys,
        "high_impact_terms": high_impact,
        "governance": gov,
        "status": status,
        "blockers": blockers,
        "exact_next_action": next_action,
        "policy_mutation_applied": False,
        "execution_authorized": False,
        "transaction_bytes_created": False,
        "instruction_bytes_created": False,
        "signed": False,
        "submitted": False,
        "broadcast": False,
        "financial_effect": False,
        "private_key_required": False,
        "wave_touched": False,
    }
    packet["packet_sha256"] = _sha(packet)
    return packet


def build_current_failclosed_proof(treasury_policy: Dict[str, Any]) -> Dict[str, Any]:
    """Produce a deterministic proof for the currently unapproved governance state."""
    proposal = {
        "schema": PROPOSAL_SCHEMA,
        "network": NETWORK,
        "mint": MINT,
        "proposal_id": "ci-policy-mutation-failclosed-proof",
        "target_file": "ReleaseOps/TokenOps/policy.json",
        "action": "review_only_policy_delta",
        "before_sha256": "0" * 64,
        "rationale_evidence_sha256": "1" * 64,
        "delta": {"per_user_cap_raw": "PROPOSED_VALUE_NOT_APPLIED"},
    }
    return compile_policy_change_packet(treasury_policy, proposal)
