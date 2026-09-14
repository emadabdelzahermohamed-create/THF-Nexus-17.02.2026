#!/usr/bin/env python3
"""THF TokenOps read-only audit + fail-closed planning controls.

This module intentionally cannot sign, serialize, submit, broadcast, transfer, burn,
change authorities, migrate treasury, settle vesting, or execute governance.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import urllib.error
import urllib.request
from typing import Any, Dict, Iterable, List, Optional, Tuple

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK = "solana-mainnet-beta"
TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
DECIMALS = 8
SUPPLY_FLOOR_RAW = 8_000_000_000 * 10**DECIMALS
SUPPLY_CEILING_RAW = 10_000_000_000 * 10**DECIMALS
SHARE_BPS = 3500
PUBLIC_RPC = "https://api.mainnet-beta.solana.com"
SCHEMA = "thf-tokenops-readonly-audit/v1"

FORBIDDEN_FIELDS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signatures", "signed_transaction", "raw_transaction",
    "serialized_transaction", "transaction_bytes", "instruction_bytes",
    "service_account_key", "access_token", "refresh_token",
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha256(value: Any) -> str:
    if isinstance(value, bytes):
        data = value
    elif isinstance(value, str):
        data = value.encode()
    else:
        data = canonical_json(value)
    return hashlib.sha256(data).hexdigest()


def scan_for_secrets(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_FIELDS:
                raise ValueError(f"forbidden sensitive field at {path}.{key}")
            scan_for_secrets(item, f"{path}.{key}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            scan_for_secrets(item, f"{path}[{i}]")


def scrub_endpoint(url: str) -> str:
    try:
        from urllib.parse import urlsplit
        p = urlsplit(url)
        host = p.hostname or "unknown"
        port = f":{p.port}" if p.port else ""
        return f"{p.scheme or 'https'}://{host}{port}/<redacted>"
    except Exception:
        return "<redacted-rpc-endpoint>"


def rpc(endpoint: str, method: str, params: list, timeout: int = 20) -> Dict[str, Any]:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(endpoint, data=payload, headers={"content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            obj = json.loads(response.read().decode())
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"RPC transport error via {scrub_endpoint(endpoint)}: {type(exc).__name__}") from exc
    if "error" in obj:
        code = obj.get("error", {}).get("code")
        raise RuntimeError(f"RPC method {method} failed via {scrub_endpoint(endpoint)} code={code}")
    return obj


def choose_rpc() -> Tuple[str, List[str]]:
    candidates = []
    if os.getenv("SOLANA_RPC_URL"):
        candidates.append(os.environ["SOLANA_RPC_URL"])
    candidates.append(PUBLIC_RPC)
    errors: List[str] = []
    for endpoint in candidates:
        try:
            rpc(endpoint, "getHealth", [])
            return endpoint, errors
        except Exception as exc:
            errors.append(str(exc))
    raise RuntimeError("; ".join(errors) or "no RPC endpoint available")


def audit_mainnet() -> Dict[str, Any]:
    endpoint, prior_errors = choose_rpc()
    slot_obj = rpc(endpoint, "getSlot", [{"commitment": "confirmed"}])
    slot = int(slot_obj["result"])
    acct = rpc(endpoint, "getAccountInfo", [MINT, {"encoding": "jsonParsed", "commitment": "confirmed"}])["result"]["value"]
    if not acct:
        raise RuntimeError("canonical mint account not found")
    owner = acct.get("owner")
    parsed = acct.get("data", {}).get("parsed", {})
    info = parsed.get("info", {})
    supply = rpc(endpoint, "getTokenSupply", [MINT, {"commitment": "confirmed"}])["result"]["value"]
    supply_raw = int(supply["amount"])
    decimals = int(supply["decimals"])

    recent: Dict[str, Any]
    try:
        sigs = rpc(endpoint, "getSignaturesForAddress", [MINT, {"limit": 20, "commitment": "confirmed"}])["result"]
        recent = {
            "status": "ok",
            "count": len(sigs),
            "entries": [
                {"slot": x.get("slot"), "blockTime": x.get("blockTime"), "err": x.get("err"), "memo": x.get("memo")}
                for x in sigs
            ],
        }
    except Exception as exc:
        recent = {"status": "unavailable", "reason": str(exc)}

    concentration: Dict[str, Any]
    try:
        largest = rpc(endpoint, "getTokenLargestAccounts", [MINT, {"commitment": "confirmed"}])["result"]["value"]
        top_raw = [int(x["amount"]) for x in largest]
        concentration = {
            "status": "ok",
            "account_count": len(largest),
            "top_accounts": [
                {"address": x.get("address"), "amount_raw": x.get("amount"), "decimals": x.get("decimals"), "uiAmountString": x.get("uiAmountString")}
                for x in largest
            ],
            "top1_bps": (top_raw[0] * 10000 // supply_raw) if top_raw and supply_raw else None,
            "top5_bps": (sum(top_raw[:5]) * 10000 // supply_raw) if supply_raw else None,
            "top20_bps": (sum(top_raw[:20]) * 10000 // supply_raw) if supply_raw else None,
        }
    except Exception as exc:
        concentration = {"status": "unavailable", "reason": str(exc)}

    result = {
        "schema": SCHEMA,
        "observed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "network": NETWORK,
        "mint": MINT,
        "rpc_endpoint": scrub_endpoint(endpoint),
        "rpc_fallback_errors": prior_errors,
        "slot": slot,
        "program_id": owner,
        "decimals": decimals,
        "supply_raw": str(supply_raw),
        "supply_ui": supply.get("uiAmountString"),
        "mint_authority": info.get("mintAuthority"),
        "freeze_authority": info.get("freezeAuthority"),
        "is_initialized": info.get("isInitialized"),
        "recent_address_activity": recent,
        "holder_concentration": concentration,
        "execution": {
            "read_only": True,
            "transaction_created": False,
            "transaction_signed": False,
            "transaction_submitted": False,
            "broadcast": False,
            "financial_effect": False,
            "private_key_used": False,
            "wave_touched": False,
        },
    }
    result["audit_sha256"] = sha256(result)
    return result


def invariant_gate(audit: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "network": audit.get("network") == NETWORK,
        "mint": audit.get("mint") == MINT,
        "program_id": audit.get("program_id") == TOKEN_PROGRAM,
        "decimals": int(audit.get("decimals", -1)) == DECIMALS,
        "mint_authority_disabled": audit.get("mint_authority") is None,
        "freeze_authority_disabled": audit.get("freeze_authority") is None,
        "supply_floor": int(audit.get("supply_raw", 0)) >= SUPPLY_FLOOR_RAW,
        "supply_ceiling": int(audit.get("supply_raw", 0)) <= SUPPLY_CEILING_RAW,
        "read_only": audit.get("execution", {}).get("read_only") is True,
        "no_financial_effect": audit.get("execution", {}).get("financial_effect") is False,
        "wave_untouched": audit.get("execution", {}).get("wave_touched") is False,
    }
    failed = sorted(k for k, v in checks.items() if not v)
    status = "PASS" if not failed else "FAIL_CLOSED"
    return {"status": status, "checks": checks, "failed": failed, "gate_sha256": sha256(checks)}


def readiness(policy: Dict[str, Any], treasury: Dict[str, Any], audit: Dict[str, Any]) -> Dict[str, Any]:
    scan_for_secrets(policy)
    scan_for_secrets(treasury)
    blockers: List[str] = []
    dc = policy["distribution_controls"]
    vest = policy["vesting_locking"]
    signer = policy["signer_policy"]
    if dc.get("per_user_cap_raw") is None: blockers.append("per_user_cap_not_approved")
    if dc.get("epoch_budget_cap_raw") is None: blockers.append("epoch_budget_cap_not_approved")
    if dc.get("distribution_reserve_account") is None: blockers.append("distribution_reserve_not_approved")
    if dc.get("delivery_model") is None: blockers.append("distribution_delivery_model_not_approved")
    if dc.get("revenue_value_basis_status") != "approved": blockers.append("revenue_value_basis_not_approved")
    if dc.get("revenue_value_basis_status") == "approved" and not re.fullmatch(r"[0-9a-f]{64}", str(dc.get("revenue_value_basis_evidence_sha256") or "")):
        blockers.append("revenue_value_basis_evidence_missing")
    if signer.get("production_policy_status") != "approved": blockers.append("production_signer_policy_not_approved")
    if vest.get("vesting_terms_status") != "approved": blockers.append("vesting_terms_not_approved")
    if vest.get("lock_terms_status") != "approved": blockers.append("lock_terms_not_approved")
    if vest.get("lock_rewards_terms_status") != "approved": blockers.append("lock_rewards_terms_not_approved")
    if not treasury.get("treasury_accounts"): blockers.append("treasury_accounts_and_evidence_missing")
    gov = treasury.get("policy_mutation_governance", {})
    if gov.get("status") != "approved": blockers.append("policy_mutation_governance_not_approved")
    gate = invariant_gate(audit)
    blockers.extend(f"onchain_invariant:{x}" for x in gate["failed"])
    supply_raw = int(audit["supply_raw"])
    burn_headroom = max(0, supply_raw - SUPPLY_FLOOR_RAW)
    result = {
        "schema": "thf-tokenops-readiness/v1",
        "network": NETWORK,
        "mint": MINT,
        "audit_sha256": audit["audit_sha256"],
        "policy_sha256": sha256(policy),
        "treasury_policy_sha256": sha256(treasury),
        "status": "FAIL_CLOSED" if blockers else "REVIEW_READY_NOT_EXECUTION_READY",
        "blockers": sorted(set(blockers)),
        "distribution": {
            "approved_revenue_share_bps": SHARE_BPS,
            "actionable_budget_raw": None,
            "per_user_cap_raw": dc.get("per_user_cap_raw"),
            "epoch_budget_cap_raw": dc.get("epoch_budget_cap_raw"),
            "revenue_value_basis_status": dc.get("revenue_value_basis_status"),
            "revenue_value_basis_evidence_sha256": dc.get("revenue_value_basis_evidence_sha256"),
            "execution_authorized": False,
        },
        "burn": {
            "supply_floor_raw": str(SUPPLY_FLOOR_RAW),
            "theoretical_headroom_raw": str(burn_headroom),
            "verified_treasury_owned_burnable_raw": None,
            "review_cap_raw": None,
            "execution_authorized": False,
        },
        "vesting_locking": {"settlement_authorized": False, "lock_rewards_authorized": False},
        "dao": {"execution_authorized": False},
        "exact_remaining_signer_action": "none_until_fail_closed_blockers_are_resolved",
        "execution": {
            "transaction_manifest_kind": "non_broadcast_intent_only",
            "transaction_bytes_created": False,
            "instructions_created": False,
            "signed": False,
            "submitted": False,
            "broadcast": False,
            "financial_effect": False,
            "private_key_used": False,
            "wave_touched": False,
        },
    }
    result["readiness_sha256"] = sha256(result)
    return result


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    obj = json.loads(path.read_text())
    scan_for_secrets(obj)
    return obj


def write_json(path: pathlib.Path, obj: Dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/tokenops")
    ap.add_argument("--policy", default="ReleaseOps/TokenOps/policy.json")
    ap.add_argument("--treasury", default="ReleaseOps/TokenOps/treasury_policy.json")
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    policy = load_json(pathlib.Path(args.policy))
    treasury = load_json(pathlib.Path(args.treasury))
    audit = audit_mainnet()
    gate = invariant_gate(audit)
    ready = readiness(policy, treasury, audit)
    write_json(out / "token-audit.json", audit)
    write_json(out / "invariant-gate.json", gate)
    write_json(out / "financial-readiness.json", ready)
    manifest = {
        "schema": "thf-tokenops-evidence-manifest/v1",
        "files": {
            "token-audit.json": sha256((out / "token-audit.json").read_bytes()),
            "invariant-gate.json": sha256((out / "invariant-gate.json").read_bytes()),
            "financial-readiness.json": sha256((out / "financial-readiness.json").read_bytes()),
        },
        "financial_effect": False,
        "broadcast": False,
        "wave_touched": False,
    }
    write_json(out / "evidence-manifest.json", manifest)
    if gate["status"] != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
