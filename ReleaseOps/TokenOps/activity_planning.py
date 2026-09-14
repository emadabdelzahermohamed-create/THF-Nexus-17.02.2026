#!/usr/bin/env python3
"""Read-only recent activity classifier + deterministic non-binding TokenOps planning.

No transaction instructions/bytes, signatures, private keys, signing, submission or
broadcast capability exists in this module.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

import tokenops_guard as G

TOKEN_TYPES = {
    "mintTo", "mintToChecked", "burn", "burnChecked", "transfer", "transferChecked",
    "setAuthority", "freezeAccount", "thawAccount", "closeAccount", "initializeMint", "initializeMint2"
}


def _walk_instructions(tx: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    message = (((tx.get("transaction") or {}).get("message") or {}))
    for ix in message.get("instructions") or []:
        if isinstance(ix, dict):
            yield ix
    meta = tx.get("meta") or {}
    for group in meta.get("innerInstructions") or []:
        for ix in group.get("instructions") or []:
            if isinstance(ix, dict):
                yield ix


def _canonical_event(ix: Mapping[str, Any]) -> Dict[str, Any] | None:
    parsed = ix.get("parsed")
    if not isinstance(parsed, dict):
        return None
    typ = parsed.get("type")
    if typ not in TOKEN_TYPES:
        return None
    info = parsed.get("info") if isinstance(parsed.get("info"), dict) else {}
    program = ix.get("programId") or ix.get("program")
    mint = info.get("mint")
    account = info.get("account")
    relevant = mint == G.MINT or (typ == "setAuthority" and account == G.MINT)
    if not relevant:
        return None
    event: Dict[str, Any] = {"type": typ}
    if mint:
        event["mint"] = mint
    if typ == "setAuthority":
        event["authority_type"] = info.get("authorityType")
        event["new_authority"] = info.get("newAuthority")
    amount = info.get("amount")
    token_amount = info.get("tokenAmount")
    if amount is not None:
        event["amount_raw"] = str(amount)
    elif isinstance(token_amount, dict) and token_amount.get("amount") is not None:
        event["amount_raw"] = str(token_amount.get("amount"))
    return event


def classify_recent_activity(limit: int = 20) -> Dict[str, Any]:
    endpoint, prior_errors = G.choose_rpc()
    sig_rows = G.rpc(endpoint, "getSignaturesForAddress", [G.MINT, {"limit": limit, "commitment": "confirmed"}])["result"]
    entries: List[Dict[str, Any]] = []
    totals = {"mint_events": 0, "burn_events": 0, "transfer_events": 0, "authority_events": 0, "unclassified_transactions": 0}
    for row in sig_rows:
        sig = row.get("signature")
        item: Dict[str, Any] = {"slot": row.get("slot"), "blockTime": row.get("blockTime"), "err": row.get("err")}
        if not sig:
            item["classification_status"] = "missing_signature_from_rpc"
            entries.append(item)
            continue
        try:
            tx = G.rpc(endpoint, "getTransaction", [sig, {"encoding": "jsonParsed", "commitment": "confirmed", "maxSupportedTransactionVersion": 0}])["result"]
            events = [] if not tx else [e for ix in _walk_instructions(tx) if (e := _canonical_event(ix)) is not None]
            item["classification_status"] = "ok"
            item["events"] = events
            if not events:
                totals["unclassified_transactions"] += 1
            for event in events:
                typ = event["type"]
                if typ.startswith("mintTo"): totals["mint_events"] += 1
                elif typ.startswith("burn"): totals["burn_events"] += 1
                elif typ.startswith("transfer"): totals["transfer_events"] += 1
                elif typ == "setAuthority": totals["authority_events"] += 1
        except Exception as exc:
            item["classification_status"] = "unavailable"
            item["reason"] = str(exc)
        entries.append(item)
    result = {
        "schema": "thf-tokenops-recent-activity-classification/v1",
        "network": G.NETWORK,
        "mint": G.MINT,
        "rpc_endpoint": G.scrub_endpoint(endpoint),
        "rpc_fallback_errors": prior_errors,
        "transaction_count": len(entries),
        "entries": entries,
        "summary": totals,
        "note": "Signature values are intentionally not stored; classification is read-only and transaction-by-transaction.",
        "financial_effect": False,
        "broadcast": False,
        "wave_touched": False,
    }
    result["classification_sha256"] = G.sha256(result)
    return result


def distribution_budget(gross_revenue_raw: int, epoch_budget_cap_raw: int | None = None) -> int:
    if gross_revenue_raw < 0:
        raise ValueError("gross revenue must be non-negative")
    budget = gross_revenue_raw * G.SHARE_BPS // 10_000
    if epoch_budget_cap_raw is not None:
        if epoch_budget_cap_raw < 0:
            raise ValueError("epoch cap must be non-negative")
        budget = min(budget, epoch_budget_cap_raw)
    return budget


def simulate_allocation(gross_revenue_raw: int, eligible_weights: Mapping[str, int], per_user_cap_raw: int,
                        epoch_budget_cap_raw: int) -> Dict[str, Any]:
    if per_user_cap_raw < 0 or epoch_budget_cap_raw < 0:
        raise ValueError("caps must be non-negative")
    if not eligible_weights:
        raise ValueError("eligible set is empty")
    if any((not isinstance(w, int)) or w < 0 for w in eligible_weights.values()):
        raise ValueError("weights must be non-negative integers")
    total_weight = sum(eligible_weights.values())
    if total_weight <= 0:
        raise ValueError("total weight must be positive")
    budget = distribution_budget(gross_revenue_raw, epoch_budget_cap_raw)
    alloc = {user: min(per_user_cap_raw, budget * weight // total_weight) for user, weight in sorted(eligible_weights.items())}
    allocated = sum(alloc.values())
    if allocated > budget:
        raise AssertionError("allocation exceeds budget")
    result = {
        "schema": "thf-tokenops-allocation-simulation/v1",
        "approved_share_bps": G.SHARE_BPS,
        "gross_revenue_raw": gross_revenue_raw,
        "budget_raw": budget,
        "per_user_cap_raw": per_user_cap_raw,
        "epoch_budget_cap_raw": epoch_budget_cap_raw,
        "allocations_raw": alloc,
        "allocated_raw": allocated,
        "unallocated_raw": budget - allocated,
        "conservation_pass": allocated + (budget - allocated) == budget,
        "binding": False,
        "execution_authorized": False,
        "transaction_bytes_created": False,
        "broadcast": False,
    }
    result["simulation_sha256"] = G.sha256(result)
    return result


def build_intent_manifest(kind: str, amount_raw: int, evidence_hashes: Sequence[str], treasury_policy: Mapping[str, Any]) -> Dict[str, Any]:
    if kind not in {"reward_epoch", "vesting_settlement", "burn", "treasury_transfer"}:
        raise ValueError("unsupported intent kind")
    if amount_raw < 0:
        raise ValueError("negative amount")
    if not evidence_hashes or any(not isinstance(x, str) or len(x) != 64 for x in evidence_hashes):
        raise ValueError("evidence hashes must be SHA-256 hex strings")
    cls = treasury_policy.get("approval_classes", {}).get(kind)
    if not cls:
        raise ValueError("missing authoritative approval class")
    result = {
        "schema": "thf-tokenops-nonbroadcast-intent/v1",
        "network": G.NETWORK,
        "mint": G.MINT,
        "kind": kind,
        "amount_raw": str(amount_raw),
        "evidence_sha256": sorted(set(evidence_hashes)),
        "required_multisig_approvals": int(cls["minimum_approvals"]),
        "execution_model": cls["execution"],
        "review_only": True,
        "binding": False,
        "execution_authorized": False,
        "transaction_instructions_created": False,
        "transaction_bytes_created": False,
        "signed": False,
        "submitted": False,
        "broadcast": False,
        "financial_effect": False,
    }
    result["intent_sha256"] = G.sha256(result)
    return result


def integration_contracts(policy: Mapping[str, Any], treasury_policy: Mapping[str, Any]) -> Dict[str, Any]:
    G.scan_for_secrets(policy)
    G.scan_for_secrets(treasury_policy)
    common = {"network": G.NETWORK, "mint": G.MINT, "policy_sha256": G.sha256(policy), "treasury_policy_sha256": G.sha256(treasury_policy)}
    result = {
        "schema": "thf-tokenops-vault-forge-core-contracts/v1",
        **common,
        "contracts": {
            "Vault": {
                "allowed_inputs": ["public_treasury_account_refs", "balance_evidence_hashes", "ownership_evidence_hashes", "multisig_policy_hash"],
                "allowed_outputs": ["inventory_snapshot_hash", "custody_readiness_status"],
                "binding_financial_action": False,
            },
            "Forge": {
                "allowed_inputs": ["nonbroadcast_intent_hash", "simulation_hash", "review_manifest_hash"],
                "allowed_outputs": ["plan_validation_hash", "simulation_summary_hash"],
                "binding_financial_action": False,
            },
            "Core": {
                "allowed_inputs": ["activity_evidence_hash", "eligible_user_set_hash", "epoch_revenue_hash"],
                "allowed_outputs": ["reward_budget_hash", "allocation_review_hash", "accounting_receipt_hash"],
                "binding_financial_action": False,
            },
        },
        "private_key_input_allowed": False,
        "signature_input_allowed": False,
        "transaction_bytes_allowed": False,
        "broadcast_allowed": False,
        "financial_effect": False,
    }
    result["contracts_sha256"] = G.sha256(result)
    return result
