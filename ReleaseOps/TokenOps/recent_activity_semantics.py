#!/usr/bin/env python3
"""Classify recent canonical THF mint-address activity without persisting signatures.

Read-only by construction: this module performs only Solana RPC reads and emits
metadata summaries. It cannot create, sign, serialize, submit, or broadcast a
transaction and never writes signatures into evidence.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
from collections import Counter
from typing import Any, Dict, Iterable, List

from tokenops_guard import MINT, choose_rpc, rpc, scan_for_secrets, sha256

SCHEMA = "thf-tokenops-recent-activity-semantics/v1"
TOKEN_TYPES = {
    "mintTo", "mintToChecked", "burn", "burnChecked", "setAuthority",
    "transfer", "transferChecked", "initializeMint", "initializeMint2",
    "closeAccount", "approve", "approveChecked", "revoke", "syncNative",
}


def parsed_instruction_types(tx: Dict[str, Any]) -> List[str]:
    """Return token instruction types found in outer + inner instructions."""
    found: List[str] = []
    result = tx.get("result") or tx
    transaction = result.get("transaction") or {}
    message = transaction.get("message") or {}
    instruction_sets: List[Iterable[Dict[str, Any]]] = [message.get("instructions") or []]
    meta = result.get("meta") or {}
    for inner in meta.get("innerInstructions") or []:
        instruction_sets.append(inner.get("instructions") or [])
    for instructions in instruction_sets:
        for ins in instructions:
            parsed = ins.get("parsed") if isinstance(ins, dict) else None
            if not isinstance(parsed, dict):
                continue
            kind = parsed.get("type")
            if isinstance(kind, str) and kind in TOKEN_TYPES:
                found.append(kind)
    return found


def summarize_transactions(transactions: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    counts: Counter[str] = Counter()
    records: List[Dict[str, Any]] = []
    for tx in transactions:
        result = tx.get("result") or tx
        kinds = sorted(parsed_instruction_types(tx))
        counts.update(kinds)
        meta = result.get("meta") or {}
        records.append({
            "slot": result.get("slot"),
            "block_time": result.get("blockTime"),
            "instruction_types": kinds,
            "transaction_failed": meta.get("err") is not None,
        })
    summary = {
        "transactions_analyzed": len(records),
        "instruction_type_counts": dict(sorted(counts.items())),
        "mint_instruction_count": counts["mintTo"] + counts["mintToChecked"],
        "burn_instruction_count": counts["burn"] + counts["burnChecked"],
        "set_authority_instruction_count": counts["setAuthority"],
        "transfer_instruction_count": counts["transfer"] + counts["transferChecked"],
        "records": records,
        "signatures_persisted": False,
    }
    scan_for_secrets(summary)
    return summary


def audit_recent_activity(limit: int = 10) -> Dict[str, Any]:
    endpoint, prior_errors = choose_rpc()
    observed = dt.datetime.now(dt.timezone.utc).isoformat()
    try:
        sig_rows = rpc(endpoint, "getSignaturesForAddress", [MINT, {"limit": limit, "commitment": "confirmed"}])["result"]
    except Exception as exc:
        result = {
            "schema": SCHEMA, "observed_at_utc": observed, "mint": MINT,
            "status": "unavailable", "requested_limit": limit,
            "signature_count_observed": None, "transactions_analyzed": 0,
            "analysis_complete": False, "reason": type(exc).__name__,
            "rpc_fallback_error_count": len(prior_errors),
            "signatures_persisted": False, "financial_effect": False,
            "broadcast": False, "wave_touched": False,
        }
        result["evidence_sha256"] = sha256(result)
        return result

    transactions: List[Dict[str, Any]] = []
    failures: List[Dict[str, Any]] = []
    for row in sig_rows:
        signature = row.get("signature")
        if not signature:
            failures.append({"slot": row.get("slot"), "reason": "missing_signature_in_rpc_response"})
            continue
        try:
            tx = rpc(endpoint, "getTransaction", [signature, {
                "encoding": "jsonParsed", "commitment": "confirmed", "maxSupportedTransactionVersion": 0,
            }])
            if tx.get("result") is None:
                failures.append({"slot": row.get("slot"), "reason": "transaction_not_available"})
            else:
                transactions.append(tx)
        except Exception as exc:
            failures.append({"slot": row.get("slot"), "reason": type(exc).__name__})

    semantic = summarize_transactions(transactions)
    complete = len(failures) == 0 and len(transactions) == len(sig_rows)
    result = {
        "schema": SCHEMA,
        "observed_at_utc": observed,
        "mint": MINT,
        "status": "ok" if complete else "degraded",
        "requested_limit": limit,
        "signature_count_observed": len(sig_rows),
        "analysis_complete": complete,
        "rpc_fallback_error_count": len(prior_errors),
        "analysis_failures": failures,
        **semantic,
        "financial_effect": False,
        "broadcast": False,
        "wave_touched": False,
    }
    scan_for_secrets(result)
    result["evidence_sha256"] = sha256(result)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/tokenops-v3/recent-activity-semantics.json")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()
    if not 1 <= args.limit <= 20:
        raise SystemExit("--limit must be between 1 and 20")
    result = audit_recent_activity(args.limit)
    path = pathlib.Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("RECENT_ACTIVITY_SEMANTICS_STATUS=" + result["status"])
    print("RECENT_ACTIVITY_ANALYSIS_COMPLETE=" + str(result.get("analysis_complete")))
    print("RECENT_MINT_INSTRUCTION_COUNT=" + str(result.get("mint_instruction_count")))
    print("RECENT_BURN_INSTRUCTION_COUNT=" + str(result.get("burn_instruction_count")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
