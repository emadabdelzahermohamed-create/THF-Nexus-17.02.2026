#!/usr/bin/env python3
"""Read-only Solana RPC capability matrix and failover selection for THF TokenOps.

Raw RPC URLs may contain credentials, so they are never serialized. Evidence only
contains scrubbed endpoint identities and method capability outcomes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

try:
    from .tokenops_guard import MINT, NETWORK, PUBLIC_RPC, rpc, scan_for_secrets, scrub_endpoint, sha256
except ImportError:  # direct script execution
    from tokenops_guard import MINT, NETWORK, PUBLIC_RPC, rpc, scan_for_secrets, scrub_endpoint, sha256

SCHEMA = "thf-tokenops-rpc-capability/v1"
METHODS = ("getHealth", "getSlot", "getTokenSupply", "getTokenLargestAccounts")


def rpc_candidates(env: Dict[str, str] | None = None) -> List[str]:
    env = os.environ if env is None else env
    raw: List[str] = []
    primary = (env.get("SOLANA_RPC_URL") or "").strip()
    if primary:
        raw.append(primary)
    fallbacks = env.get("SOLANA_RPC_FALLBACK_URLS") or ""
    for item in re.split(r"[;,\n]", fallbacks):
        item = item.strip()
        if item:
            raw.append(item)
    raw.append(PUBLIC_RPC)
    result: List[str] = []
    seen = set()
    for endpoint in raw:
        if endpoint not in seen:
            seen.add(endpoint)
            result.append(endpoint)
    return result


def method_params(method: str) -> list:
    if method == "getHealth":
        return []
    if method == "getSlot":
        return [{"commitment": "confirmed"}]
    if method in {"getTokenSupply", "getTokenLargestAccounts"}:
        return [MINT, {"commitment": "confirmed"}]
    raise ValueError(f"unsupported RPC capability method: {method}")


def select_first_capable(rows: Sequence[Dict[str, Any]], required_methods: Iterable[str]) -> int | None:
    required = tuple(required_methods)
    for row in rows:
        caps = row.get("capabilities", {})
        if all(caps.get(method, {}).get("ok") is True for method in required):
            return int(row["candidate_index"])
    return None


def probe_capabilities(
    candidates: Sequence[str] | None = None,
    methods: Sequence[str] = METHODS,
    timeout: int = 12,
) -> Tuple[Dict[str, Any], List[str]]:
    endpoints = list(candidates or rpc_candidates())
    rows: List[Dict[str, Any]] = []
    for index, endpoint in enumerate(endpoints):
        capabilities: Dict[str, Any] = {}
        for method in methods:
            try:
                response = rpc(endpoint, method, method_params(method), timeout=timeout)
                value = response.get("result")
                summary: Dict[str, Any] = {"ok": True}
                if method == "getSlot":
                    summary["slot"] = int(value)
                elif method == "getTokenSupply":
                    summary["amount_raw"] = str(value["value"]["amount"])
                    summary["decimals"] = int(value["value"]["decimals"])
                elif method == "getTokenLargestAccounts":
                    summary["account_count"] = len(value["value"])
                capabilities[method] = summary
            except Exception as exc:
                capabilities[method] = {"ok": False, "error": f"{type(exc).__name__}:{exc}"}
        rows.append({
            "candidate_index": index,
            "endpoint": scrub_endpoint(endpoint),
            "capabilities": capabilities,
        })

    holder_index = select_first_capable(rows, ("getTokenSupply", "getTokenLargestAccounts"))
    core_index = select_first_capable(rows, ("getHealth", "getSlot", "getTokenSupply"))
    packet: Dict[str, Any] = {
        "schema": SCHEMA,
        "observed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "network": NETWORK,
        "mint": MINT,
        "candidate_count": len(rows),
        "candidates": rows,
        "core_read_candidate_index": core_index,
        "holder_concentration_candidate_index": holder_index,
        "status": "PASS_READ_ONLY" if core_index is not None else "UNAVAILABLE_FAIL_CLOSED",
        "holder_concentration_status": "CAPABLE" if holder_index is not None else "UNAVAILABLE_FAIL_CLOSED",
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
    scan_for_secrets(packet)
    packet["probe_sha256"] = sha256(packet)
    return packet, endpoints


def select_capable_rpc(required_methods: Sequence[str], candidates: Sequence[str] | None = None) -> Tuple[str | None, Dict[str, Any]]:
    packet, endpoints = probe_capabilities(candidates=candidates)
    index = select_first_capable(packet["candidates"], required_methods)
    return (endpoints[index] if index is not None else None), packet


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/tokenops-rpc/rpc-capability.json")
    args = ap.parse_args()
    packet, _ = probe_capabilities()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(packet, sort_keys=True, indent=2) + "\n")
    print("RPC_CAPABILITY_STATUS=" + packet["status"])
    print("RPC_CANDIDATE_COUNT=" + str(packet["candidate_count"]))
    print("RPC_HOLDER_CONCENTRATION_STATUS=" + packet["holder_concentration_status"])
    print("RPC_CAPABILITY_SHA256=" + packet["probe_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
