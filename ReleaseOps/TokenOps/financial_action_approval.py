#!/usr/bin/env python3
"""Fail-closed authorization classifier for THF TokenOps financial actions.

This module never signs, broadcasts, transfers, burns, changes authorities, migrates
funds, settles vesting, or executes governance. It only classifies proposed actions
and emits the exact approval evidence required before an external signer may act.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Dict, Tuple

SCHEMA = "thf-tokenops-financial-action-approval/v1"

@dataclass(frozen=True)
class Rule:
    irreversible: bool
    financial_effect: bool
    signer_required: bool
    multisig_required: bool
    governance_evidence_required: bool
    simulation_required: bool

RULES: Dict[str, Rule] = {
    "read_chain_state": Rule(False, False, False, False, False, False),
    "simulate_transaction": Rule(False, False, False, False, False, False),
    "prepare_unsigned_manifest": Rule(False, False, False, False, False, True),
    "transfer": Rule(True, True, True, True, False, True),
    "burn": Rule(True, True, True, True, True, True),
    "authority_change": Rule(True, True, True, True, True, True),
    "treasury_migration": Rule(True, True, True, True, True, True),
    "vesting_settlement": Rule(True, True, True, True, False, True),
    "dao_execution": Rule(True, True, True, True, True, True),
}

REQUIRED_EVIDENCE: Tuple[str, ...] = (
    "source_commit_sha",
    "policy_sha256",
    "transaction_manifest_sha256",
    "simulation_evidence_sha256",
)


def classify(action: str) -> dict:
    if action not in RULES:
        return {"schema": SCHEMA, "action": action, "allowed_autonomously": False,
                "status": "BLOCKED_UNKNOWN_ACTION", "missing": ["recognized_action"]}
    rule = RULES[action]
    return {"schema": SCHEMA, "action": action, **asdict(rule),
            "allowed_autonomously": not rule.financial_effect,
            "status": "SAFE_AUTONOMOUS" if not rule.financial_effect else "REQUIRES_USER_CONTROLLED_APPROVAL"}


def evaluate(action: str, evidence: dict | None = None) -> dict:
    evidence = evidence or {}
    result = classify(action)
    if result.get("status") == "BLOCKED_UNKNOWN_ACTION" or result["allowed_autonomously"]:
        return result
    required = list(REQUIRED_EVIDENCE)
    if result["governance_evidence_required"]:
        required.append("governance_decision_evidence_sha256")
    if result["multisig_required"]:
        required.append("user_controlled_multisig_approval")
    missing = [k for k in required if not evidence.get(k)]
    result["required_evidence"] = required
    result["missing"] = missing
    # Even with complete evidence, automation remains non-executing. External signer is mandatory.
    result["status"] = "READY_FOR_EXTERNAL_SIGNER_REVIEW" if not missing else "BLOCKED_MISSING_APPROVAL_EVIDENCE"
    result["allowed_autonomously"] = False
    result["broadcast"] = False
    result["private_key_used"] = False
    return result


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=sorted(RULES))
    ap.add_argument("--evidence-json")
    args = ap.parse_args()
    evidence = json.loads(args.evidence_json) if args.evidence_json else {}
    print(json.dumps(evaluate(args.action, evidence), sort_keys=True, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
