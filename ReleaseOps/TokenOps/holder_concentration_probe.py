#!/usr/bin/env python3
"""THF holder-concentration read-only probe with bounded RPC retries.

This module performs only Solana read calls. It never creates instructions or
transactions, never signs or broadcasts, and never handles private keys.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import time
from pathlib import Path
from typing import Any, Callable, Dict, List

from tokenops_guard import MINT, NETWORK, PUBLIC_RPC, TOKEN_PROGRAM, choose_rpc, rpc, scan_for_secrets, sha256

SCHEMA = "thf-tokenops-holder-concentration/v1"


def summarize_largest_accounts(accounts: List[Dict[str, Any]], supply_raw: int) -> Dict[str, Any]:
    amounts = [int(x.get("amount", 0)) for x in accounts]
    return {
        "account_count": len(accounts),
        "top1_bps": (amounts[0] * 10000 // supply_raw) if amounts and supply_raw else None,
        "top5_bps": (sum(amounts[:5]) * 10000 // supply_raw) if supply_raw else None,
        "top20_bps": (sum(amounts[:20]) * 10000 // supply_raw) if supply_raw else None,
        "top_accounts": [
            {
                "address": x.get("address"),
                "amount_raw": str(x.get("amount")),
                "decimals": x.get("decimals"),
                "uiAmountString": x.get("uiAmountString"),
            }
            for x in accounts
        ],
    }


def probe(
    *,
    attempts: int = 4,
    base_delay_seconds: float = 1.5,
    sleeper: Callable[[float], None] = time.sleep,
) -> Dict[str, Any]:
    endpoint, selection_errors = choose_rpc()
    observed_at = dt.datetime.now(dt.timezone.utc).isoformat()
    supply_obj = rpc(endpoint, "getTokenSupply", [MINT, {"commitment": "confirmed"}])["result"]["value"]
    supply_raw = int(supply_obj["amount"])
    errors: List[str] = []
    largest: List[Dict[str, Any]] | None = None
    used_attempts = 0
    for idx in range(max(1, attempts)):
        used_attempts = idx + 1
        try:
            largest = rpc(endpoint, "getTokenLargestAccounts", [MINT, {"commitment": "confirmed"}])["result"]["value"]
            break
        except Exception as exc:
            errors.append(f"attempt={idx + 1}:{type(exc).__name__}:{exc}")
            if idx + 1 < max(1, attempts):
                sleeper(base_delay_seconds * (2**idx))

    if largest is None:
        result: Dict[str, Any] = {
            "schema": SCHEMA,
            "status": "UNAVAILABLE_FAIL_CLOSED",
            "observed_at_utc": observed_at,
            "network": NETWORK,
            "mint": MINT,
            "token_program": TOKEN_PROGRAM,
            "supply_raw": str(supply_raw),
            "attempts": used_attempts,
            "rpc_selection_error_count": len(selection_errors),
            "probe_errors": errors,
            "concentration": None,
        }
    else:
        result = {
            "schema": SCHEMA,
            "status": "PASS_READ_ONLY",
            "observed_at_utc": observed_at,
            "network": NETWORK,
            "mint": MINT,
            "token_program": TOKEN_PROGRAM,
            "supply_raw": str(supply_raw),
            "attempts": used_attempts,
            "rpc_selection_error_count": len(selection_errors),
            "probe_errors": errors,
            "concentration": summarize_largest_accounts(largest, supply_raw),
        }
    result.update({
        "execution_authorized": False,
        "transaction_bytes_created": False,
        "instruction_bytes_created": False,
        "signed": False,
        "submitted": False,
        "broadcast": False,
        "financial_effect": False,
        "private_key_used": False,
        "wave_touched": False,
    })
    scan_for_secrets(result)
    result["probe_sha256"] = sha256(result)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/tokenops-holder/holder-concentration.json")
    ap.add_argument("--attempts", type=int, default=4)
    args = ap.parse_args()
    packet = probe(attempts=args.attempts)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(packet, sort_keys=True, indent=2) + "\n")
    print("HOLDER_CONCENTRATION_STATUS=" + packet["status"])
    print("HOLDER_CONCENTRATION_ATTEMPTS=" + str(packet["attempts"]))
    if packet["concentration"]:
        print("TOP1_BPS=" + str(packet["concentration"]["top1_bps"]))
        print("TOP5_BPS=" + str(packet["concentration"]["top5_bps"]))
        print("TOP20_BPS=" + str(packet["concentration"]["top20_bps"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
