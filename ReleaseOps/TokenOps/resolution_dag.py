#!/usr/bin/env python3
"""Deterministic dependency plan for THF TokenOps fail-closed readiness blockers.

This module does not choose economic values or authorize financial execution. It
turns the authoritative blocker set into parallel evidence/governance workstreams
and an explicit dependency graph so independent work can continue safely.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Set

from blocker_resolution import CONTRACTS

SCHEMA = "thf-tokenops-resolution-dag/v1"


def _sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


DEPENDENCIES: Dict[str, List[str]] = {
    "distribution_reserve_not_approved": ["treasury_accounts_and_evidence_missing"],
    "lock_rewards_terms_not_approved": ["lock_terms_not_approved"],
}

WORKSTREAMS = {
    "governance_policy": "governance_policy_batch",
    "governance_charter": "governance_charter_batch",
    "signer_governance": "signer_governance_batch",
    "valuation_evidence": "valuation_evidence_batch",
    "treasury_evidence": "treasury_evidence_batch",
    "unmapped_fail_closed": "manual_mapping_batch",
}


def _blocker_base(blocker: str) -> str:
    return blocker.split(":", 1)[0]


def build_resolution_dag(readiness: Dict[str, Any]) -> Dict[str, Any]:
    blockers = sorted(set(str(x) for x in readiness.get("blockers", [])))
    blocker_set: Set[str] = set(blockers)
    nodes: List[Dict[str, Any]] = []
    batches: Dict[str, List[str]] = {}

    for blocker in blockers:
        base = _blocker_base(blocker)
        contract = CONTRACTS.get(blocker) or CONTRACTS.get(base)
        klass = contract.get("class") if contract else "unmapped_fail_closed"
        deps = [d for d in DEPENDENCIES.get(base, []) if d in blocker_set]
        workstream = WORKSTREAMS.get(str(klass), "manual_mapping_batch")
        requires_governance = str(klass) in {
            "governance_policy", "governance_charter", "signer_governance", "valuation_evidence"
        }
        requires_public_evidence = str(klass) in {"treasury_evidence", "valuation_evidence"}
        node = {
            "blocker": blocker,
            "class": klass,
            "workstream": workstream,
            "depends_on": sorted(deps),
            "ready_for_resolution_work": not deps,
            "requires_user_controlled_governance": requires_governance,
            "requires_public_evidence": requires_public_evidence,
            "required_fields": list(contract.get("required_fields", [])) if contract else [],
            "status": "OPEN",
        }
        nodes.append(node)
        batches.setdefault(workstream, []).append(blocker)

    parallel_batches = [
        {
            "workstream": name,
            "blockers": sorted(items),
            "all_dependency_free": all(
                not next(n for n in nodes if n["blocker"] == b)["depends_on"] for b in items
            ),
        }
        for name, items in sorted(batches.items())
    ]

    immediately_actionable = sorted(n["blocker"] for n in nodes if n["ready_for_resolution_work"])
    dependency_blocked = sorted(n["blocker"] for n in nodes if not n["ready_for_resolution_work"])
    unknown = sorted(n["blocker"] for n in nodes if n["class"] == "unmapped_fail_closed")

    result = {
        "schema": SCHEMA,
        "network": readiness.get("network"),
        "mint": readiness.get("mint"),
        "readiness_sha256": readiness.get("readiness_sha256"),
        "status": "FAIL_CLOSED" if blockers else "NO_OPEN_BLOCKERS",
        "blocker_count": len(blockers),
        "unknown_blockers": unknown,
        "nodes": nodes,
        "parallel_batches": parallel_batches,
        "immediately_actionable_resolution_work": immediately_actionable,
        "dependency_blocked_resolution_work": dependency_blocked,
        "signer_action_now": "NONE",
        "execution_authorized": False,
        "transaction_bytes_created": False,
        "instruction_bytes_created": False,
        "signed": False,
        "submitted": False,
        "broadcast": False,
        "financial_effect": False,
        "wave_touched": False,
    }
    result["resolution_dag_sha256"] = _sha256(result)
    return result


def summarize_resolution_dag(dag: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        "schema": "thf-tokenops-resolution-dag-summary/v1",
        "status": dag.get("status"),
        "blocker_count": dag.get("blocker_count", 0),
        "parallel_batch_count": len(dag.get("parallel_batches", [])),
        "immediately_actionable_count": len(dag.get("immediately_actionable_resolution_work", [])),
        "dependency_blocked_count": len(dag.get("dependency_blocked_resolution_work", [])),
        "unknown_blocker_count": len(dag.get("unknown_blockers", [])),
        "signer_action_now": "NONE",
        "execution_authorized": False,
        "financial_effect": False,
    }
    result["summary_sha256"] = _sha256(result)
    return result
