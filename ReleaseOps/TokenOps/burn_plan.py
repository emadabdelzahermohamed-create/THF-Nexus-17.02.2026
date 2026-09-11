#!/usr/bin/env python3
"""Create a treasury-only THF burn plan. No Solana transaction is constructed."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
DECIMALS = 8
FLOOR_RAW = 8_000_000_000 * 10**DECIMALS


def canon(o):
    return (json.dumps(o, sort_keys=True, separators=(",", ":")) + "\n").encode()


def build(inp: dict) -> dict:
    if inp.get("network") != "solana-mainnet-beta" or inp.get("mint") != MINT:
        raise ValueError("unexpected network or mint")
    supply = int(inp["observed_supply_raw"])
    requested = int(inp["requested_burn_raw"])
    if requested < 0 or supply < FLOOR_RAW:
        raise ValueError("invalid supply/request")
    max_by_floor = max(0, supply - FLOOR_RAW)
    allowed = min(requested, max_by_floor)

    sources=[]
    remaining=allowed
    for row in sorted(inp.get("treasury_accounts", []), key=lambda x: x["token_account"]):
        if not row.get("treasury_control_verified"):
            continue
        bal=max(0, int(row.get("balance_raw", 0)))
        take=min(bal, remaining)
        if take:
            sources.append({"token_account":row["token_account"],"owner":row["owner"],"planned_burn_raw":str(take)})
            remaining-=take
        if remaining == 0:
            break

    planned=allowed-remaining
    out={
        "schema":"thf-tokenops-burn-plan/v1",
        "network":"solana-mainnet-beta",
        "mint":MINT,
        "observed_supply_raw":str(supply),
        "approved_floor_target_raw":str(FLOOR_RAW),
        "requested_burn_raw":str(requested),
        "max_burn_without_crossing_floor_raw":str(max_by_floor),
        "planned_burn_raw":str(planned),
        "unfulfilled_requested_burn_raw":str(requested-planned),
        "projected_supply_raw":str(supply-planned),
        "sources":sources,
        "constraints":{
            "treasury_controlled_balances_only":True,
            "third_party_holder_burn_forbidden":True,
            "external_signer_required":True,
        },
        "execution":{
            "transaction_created":False,
            "transaction_signed":False,
            "transaction_submitted":False,
            "burn_executed":False,
        }
    }
    out["plan_sha256"] = hashlib.sha256(canon(out)).hexdigest()
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("input",type=Path); ap.add_argument("output",type=Path); a=ap.parse_args()
    out=build(json.loads(a.input.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_bytes(canon(out))
    print(f"THF_BURN_PLAN=PASS sha256={out['plan_sha256']} planned_raw={out['planned_burn_raw']}")
    print("TRANSACTION_CREATED=FALSE\nTRANSACTION_SIGNED=FALSE\nTRANSACTION_SUBMITTED=FALSE\nBURN_EXECUTED=FALSE")

if __name__ == "__main__": main()
