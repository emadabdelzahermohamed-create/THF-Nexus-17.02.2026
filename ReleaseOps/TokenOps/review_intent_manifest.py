#!/usr/bin/env python3
"""Deterministic non-executable THF TokenOps review-intent manifest.

Binds a requested financial operation to the exact operation-readiness and evidence-chain
packets. It can never construct Solana instructions/transactions, sign, submit, broadcast,
or create financial effect. A manifest is REVIEW_READY only when the upstream operation
is awaiting user-controlled multisig approval and the evidence chain passes; otherwise it
is FAIL_CLOSED.

This module consumes only already-generated public TokenOps evidence packets. It does not
accept signer material, secrets, transaction bytes, instruction bytes, or arbitrary RPC
credentials as inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict

try:
    from ReleaseOps.TokenOps.financial_control_plane import MINT, NETWORK, TOKEN_PROGRAM
except ModuleNotFoundError:  # Direct CLI execution from ReleaseOps/TokenOps/.
    from financial_control_plane import MINT, NETWORK, TOKEN_PROGRAM

SCHEMA = "thf-tokenops-review-intent-manifest/v1"
ALLOWED_OPERATIONS = {"reward_epoch", "lock_reward", "vesting_settlement", "burn", "treasury_transfer"}


def _canonical(v: Any) -> bytes:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _sha(v: Any) -> str:
    return hashlib.sha256(_canonical(v)).hexdigest()


def _valid_sha(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
        return True
    except ValueError:
        return False


def build_review_intent(operation_matrix: Dict[str, Any], evidence_chain: Dict[str, Any], operation: str) -> Dict[str, Any]:
    if operation not in ALLOWED_OPERATIONS:
        raise ValueError("unsupported operation")
    if operation_matrix.get("network") != NETWORK or operation_matrix.get("mint") != MINT:
        raise ValueError("operation matrix canonical identity mismatch")
    if operation_matrix.get("token_program") != TOKEN_PROGRAM:
        raise ValueError("operation matrix token program mismatch")
    op = (operation_matrix.get("operations") or {}).get(operation)
    if not isinstance(op, dict):
        raise ValueError("operation missing from matrix")

    blockers = []
    if evidence_chain.get("status") != "PASS":
        blockers.append("evidence_chain_not_pass")
    evidence_root = evidence_chain.get("evidence_root_sha256")
    if not _valid_sha(evidence_root):
        blockers.append("evidence_root_invalid")
    matrix_sha = operation_matrix.get("matrix_sha256")
    if not _valid_sha(matrix_sha):
        blockers.append("operation_matrix_sha_invalid")
    if operation_matrix.get("execution_authorized") is not False:
        blockers.append("matrix_execution_safety_violation")
    if op.get("execution_authorized") is not False or op.get("financial_effect") is not False:
        blockers.append("operation_execution_safety_violation")
    upstream_status = str(op.get("status") or "MISSING")
    if upstream_status != "AWAITING_USER_CONTROLLED_MULTISIG_APPROVAL":
        blockers.append("operation_not_review_ready")

    status = "REVIEW_READY_NOT_EXECUTION_READY" if not blockers else "FAIL_CLOSED"
    exact_signer_action = op.get("exact_signer_action", "NONE") if status.startswith("REVIEW_READY") else "NONE"
    result: Dict[str, Any] = {
        "schema": SCHEMA,
        "network": NETWORK,
        "mint": MINT,
        "token_program": TOKEN_PROGRAM,
        "operation": operation,
        "status": status,
        "blockers": sorted(set(blockers)),
        "upstream_operation_status": upstream_status,
        "minimum_approvals": op.get("minimum_approvals"),
        "approval_class": op.get("approval_class"),
        "review_cap_raw": op.get("review_cap_raw"),
        "operation_matrix_sha256": matrix_sha,
        "evidence_root_sha256": evidence_root,
        "source_commit_sha": (evidence_chain.get("root_material") or {}).get("source_commit_sha"),
        "exact_signer_action": exact_signer_action,
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
    result["manifest_sha256"] = _sha(result)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--operation-matrix", required=True)
    ap.add_argument("--evidence-chain", required=True)
    ap.add_argument("--operation", required=True, choices=sorted(ALLOWED_OPERATIONS))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    matrix = json.loads(Path(args.operation_matrix).read_text())
    chain = json.loads(Path(args.evidence_chain).read_text())
    packet = build_review_intent(matrix, chain, args.operation)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(packet, sort_keys=True, indent=2) + "\n")
    print("REVIEW_INTENT_STATUS=" + packet["status"])
    print("REVIEW_INTENT_OPERATION=" + packet["operation"])
    print("REVIEW_INTENT_MANIFEST_SHA256=" + packet["manifest_sha256"])
    print("REVIEW_INTENT_SIGNER_ACTION=" + packet["exact_signer_action"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
