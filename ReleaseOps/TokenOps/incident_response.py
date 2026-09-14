#!/usr/bin/env python3
"""Deterministic THF TokenOps incident/quarantine decision engine.

This module is intentionally control-plane only. It cannot construct transaction or
instruction bytes, sign, submit, broadcast, transfer, burn, migrate treasury, change
authorities, settle rewards/vesting, or execute governance.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any, Dict, List

try:
    from .tokenops_guard import MINT, NETWORK, scan_for_secrets, sha256
except ImportError:
    from tokenops_guard import MINT, NETWORK, scan_for_secrets, sha256

SCHEMA = "thf-tokenops-incident-response/v1"
CRITICAL_STATUSES = {"FAIL", "FAIL_CLOSED", "ERROR", "STALE", "INVALID"}
OPTIONAL_DEGRADED = {"UNAVAILABLE", "UNAVAILABLE_FAIL_CLOSED", "DEGRADED"}


def _status(obj: Dict[str, Any] | None) -> str:
    return str((obj or {}).get("status") or "MISSING").upper()


def _is_fail(obj: Dict[str, Any] | None) -> bool:
    return _status(obj) in CRITICAL_STATUSES or obj is None


def assess_incident(
    audit: Dict[str, Any],
    invariant_gate: Dict[str, Any],
    evidence_chain: Dict[str, Any],
    source_provenance: Dict[str, Any],
    financial_readiness: Dict[str, Any],
    treasury_reconciliation: Dict[str, Any] | None = None,
    holder_concentration: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    for value in (
        audit, invariant_gate, evidence_chain, source_provenance,
        financial_readiness, treasury_reconciliation, holder_concentration,
    ):
        if value is not None:
            scan_for_secrets(value)

    critical: List[str] = []
    degraded: List[str] = []

    if audit.get("network") != NETWORK:
        critical.append("canonical_network_drift")
    if audit.get("mint") != MINT:
        critical.append("canonical_mint_drift")
    execution = audit.get("execution", {})
    if execution.get("read_only") is not True or execution.get("financial_effect") is not False:
        critical.append("audit_execution_safety_violation")
    if execution.get("wave_touched") is not False:
        critical.append("wave_scope_violation")

    if _is_fail(invariant_gate):
        critical.extend("onchain_invariant:" + str(x) for x in invariant_gate.get("failed", []) or ["gate_not_pass"])
    if _is_fail(evidence_chain):
        critical.extend("evidence_chain:" + str(x) for x in evidence_chain.get("failed", []) or ["chain_not_pass"])
    if source_provenance.get("wave_in_inventory") is not False or source_provenance.get("wave_touched") is not False:
        critical.append("source_provenance_wave_scope_violation")
    if not source_provenance.get("tokenops_source_root_sha256"):
        critical.append("source_provenance_missing_root")

    # Financial readiness may legitimately remain FAIL_CLOSED because policy approvals
    # are absent. That is a readiness blocker, not by itself an incident.
    if _status(financial_readiness) not in {"FAIL_CLOSED", "REVIEW_READY_NOT_EXECUTION_READY"}:
        critical.append("financial_readiness_state_invalid")
    if financial_readiness.get("execution_authorized") is True:
        critical.append("unexpected_financial_execution_authorization")

    # A supplied reconciliation that explicitly reports inconsistency is critical.
    if treasury_reconciliation is not None:
        tr_status = _status(treasury_reconciliation)
        if tr_status in {"FAIL", "ERROR", "INVALID"}:
            critical.append("treasury_reconciliation_failure")
        elif tr_status == "FAIL_CLOSED":
            # Empty/unverified registry is a known readiness blocker. Treat explicit
            # balance/hash/ownership mismatches as incident signals when present.
            mismatches = (
                treasury_reconciliation.get("mismatches")
                or treasury_reconciliation.get("failed")
                or treasury_reconciliation.get("violations")
                or []
            )
            if mismatches:
                critical.append("treasury_reconciliation_mismatch")

    if holder_concentration is not None:
        hc = _status(holder_concentration)
        if hc in OPTIONAL_DEGRADED:
            degraded.append("holder_concentration_unavailable")
        elif hc in {"FAIL", "ERROR", "INVALID"}:
            degraded.append("holder_concentration_probe_failure")

    if critical:
        mode = "FAIL_CLOSED_CRITICAL"
        pause_review_intents = True
        recovery = "fresh_core_evidence_and_human_multisig_review"
    elif degraded:
        mode = "READ_ONLY_DEGRADED"
        pause_review_intents = False
        recovery = "restore_optional_read_only_observability"
    else:
        mode = "NORMAL_READ_ONLY"
        pause_review_intents = False
        recovery = "none"

    result: Dict[str, Any] = {
        "schema": SCHEMA,
        "network": NETWORK,
        "mint": MINT,
        "mode": mode,
        "critical_reasons": sorted(set(critical)),
        "degraded_reasons": sorted(set(degraded)),
        "pause_review_intent_generation": pause_review_intents,
        "reaudit_required": bool(critical),
        "recovery_requirement": recovery,
        "rollback": {
            "repository_checkpoint_rollback_may_be_recommended": bool(critical),
            "onchain_rollback_allowed": False,
            "automatic_recovery_allowed": False,
        },
        "execution_authorized": False,
        "transaction_bytes_created": False,
        "instruction_bytes_created": False,
        "signed": False,
        "submitted": False,
        "broadcast": False,
        "financial_effect": False,
        "private_key_used": False,
        "wave_touched": False,
    }
    result["input_evidence_sha256"] = {
        "audit": sha256(audit),
        "invariant_gate": sha256(invariant_gate),
        "evidence_chain": sha256(evidence_chain),
        "source_provenance": sha256(source_provenance),
        "financial_readiness": sha256(financial_readiness),
        "treasury_reconciliation": sha256(treasury_reconciliation) if treasury_reconciliation is not None else None,
        "holder_concentration": sha256(holder_concentration) if holder_concentration is not None else None,
    }
    scan_for_secrets(result)
    result["incident_assessment_sha256"] = sha256(result)
    return result


def _load(path: str) -> Dict[str, Any]:
    obj = json.loads(pathlib.Path(path).read_text())
    if not isinstance(obj, dict):
        raise ValueError(f"expected JSON object: {path}")
    return obj


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", required=True)
    ap.add_argument("--invariant-gate", required=True)
    ap.add_argument("--evidence-chain", required=True)
    ap.add_argument("--source-provenance", required=True)
    ap.add_argument("--financial-readiness", required=True)
    ap.add_argument("--treasury-reconciliation")
    ap.add_argument("--holder-concentration")
    ap.add_argument("--out", default="out/tokenops-incident/incident-assessment.json")
    args = ap.parse_args()
    result = assess_incident(
        _load(args.audit),
        _load(args.invariant_gate),
        _load(args.evidence_chain),
        _load(args.source_provenance),
        _load(args.financial_readiness),
        _load(args.treasury_reconciliation) if args.treasury_reconciliation else None,
        _load(args.holder_concentration) if args.holder_concentration else None,
    )
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("TOKENOPS_INCIDENT_MODE=" + result["mode"])
    print("TOKENOPS_INCIDENT_CRITICAL_COUNT=" + str(len(result["critical_reasons"])))
    print("TOKENOPS_INCIDENT_DEGRADED_COUNT=" + str(len(result["degraded_reasons"])))
    print("TOKENOPS_INCIDENT_ASSESSMENT_SHA256=" + result["incident_assessment_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
