#!/usr/bin/env python3
"""THF TokenOps offline reward-manifest generator.

Safety boundary: this module never creates, signs, simulates or broadcasts a Solana
transaction. It only produces deterministic accounting manifests for later review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, ROUND_DOWN
from pathlib import Path

BPS_DENOM = 10_000
DEFAULT_SHARE_BPS = 3_500


def canonical_bytes(obj: dict) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def build_manifest(inp: dict) -> dict:
    if inp.get("network") != "solana-mainnet-beta":
        raise ValueError("network must be solana-mainnet-beta")
    mint = inp.get("mint")
    if mint != "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv":
        raise ValueError("unexpected mint")

    revenue_minor = int(inp["epoch_revenue_minor"])
    share_bps = int(inp.get("revenue_share_bps", DEFAULT_SHARE_BPS))
    if revenue_minor < 0 or not (0 <= share_bps <= BPS_DENOM):
        raise ValueError("invalid revenue/share")
    revenue_share_minor = revenue_minor * share_bps // BPS_DENOM

    token_budget_raw = int(inp["approved_token_budget_raw"])
    epoch_budget_cap_raw = int(inp["epoch_budget_cap_raw"])
    per_user_cap_raw = int(inp["per_user_cap_raw"])
    if min(token_budget_raw, epoch_budget_cap_raw, per_user_cap_raw) < 0:
        raise ValueError("negative budget/cap")
    distributable = min(token_budget_raw, epoch_budget_cap_raw)

    eligible = []
    rejected = []
    for row in inp.get("participants", []):
        uid = str(row["participant_id"])
        wallet = str(row.get("wallet", ""))
        score = Decimal(str(row.get("activity_score", "0")))
        evidence = bool(row.get("activity_evidence_verified"))
        sybil = bool(row.get("anti_sybil_pass"))
        if not wallet or score <= 0 or not evidence or not sybil:
            rejected.append({"participant_id": uid, "reason": "eligibility_gate"})
            continue
        eligible.append((uid, wallet, score))

    total_score = sum((x[2] for x in eligible), Decimal(0))
    allocations = []
    allocated = 0
    if total_score > 0 and distributable > 0:
        provisional = []
        for uid, wallet, score in eligible:
            raw = int((Decimal(distributable) * score / total_score).to_integral_value(rounding=ROUND_DOWN))
            raw = min(raw, per_user_cap_raw)
            provisional.append([uid, wallet, score, raw])
        allocated = sum(x[3] for x in provisional)
        # Do not redistribute cap-created remainder: conservative accounting keeps it in treasury.
        for uid, wallet, score, raw in sorted(provisional, key=lambda x: (x[0], x[1])):
            allocations.append({
                "participant_id": uid,
                "wallet": wallet,
                "activity_score": str(score),
                "allocation_raw": str(raw),
            })

    manifest = {
        "schema": "thf-tokenops-reward-manifest/v1",
        "network": inp["network"],
        "mint": mint,
        "epoch_id": str(inp["epoch_id"]),
        "revenue": {
            "currency": str(inp["revenue_currency"]),
            "epoch_revenue_minor": str(revenue_minor),
            "revenue_share_bps": share_bps,
            "active_user_share_minor": str(revenue_share_minor),
            "note": "Revenue accounting and token budget are deliberately separated; token price is not inferred.",
        },
        "treasury_budget": {
            "approved_token_budget_raw": str(token_budget_raw),
            "epoch_budget_cap_raw": str(epoch_budget_cap_raw),
            "effective_distributable_raw": str(distributable),
            "per_user_cap_raw": str(per_user_cap_raw),
            "allocated_raw": str(allocated),
            "unallocated_raw": str(distributable - allocated),
        },
        "eligibility": {
            "anti_sybil_required": True,
            "activity_evidence_required": True,
            "eligible_count": len(eligible),
            "rejected": sorted(rejected, key=lambda x: x["participant_id"]),
        },
        "allocations": allocations,
        "execution": {
            "transaction_created": False,
            "transaction_signed": False,
            "transaction_submitted": False,
            "requires_external_approval": True,
        },
    }
    digest = hashlib.sha256(canonical_bytes(manifest)).hexdigest()
    return {**manifest, "manifest_sha256": digest}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    inp = json.loads(args.input.read_text())
    manifest = build_manifest(inp)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(manifest))
    print(f"THF_REWARD_MANIFEST=PASS sha256={manifest['manifest_sha256']} allocations={len(manifest['allocations'])}")
    print("TRANSACTION_CREATED=FALSE")
    print("TRANSACTION_SIGNED=FALSE")
    print("TRANSACTION_SUBMITTED=FALSE")


if __name__ == "__main__":
    main()
