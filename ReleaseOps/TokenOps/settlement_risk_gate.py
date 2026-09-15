#!/usr/bin/env python3
"""Deterministic pre-signer risk gate for THF treasury settlement plans.

Planning/review only. Never signs, broadcasts, transfers, burns or settles funds.
"""
from __future__ import annotations
import hashlib, json

SCHEMA="thf-tokenops-settlement-risk/v1"
def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"))
def digest(v): return hashlib.sha256(_canon(v).encode()).hexdigest()

def assess(*, epoch_id:str, manifest_sha256:str, allocations:list[dict], pool_atomic:int,
           max_recipient_bps:int, previously_settled_manifest_sha256s:set[str]|None=None)->dict:
    if pool_atomic < 0 or not (0 < max_recipient_bps <= 10000): raise ValueError("invalid policy")
    seen=set(); blockers=[]; rows=[]; total=0; max_allowed=(pool_atomic*max_recipient_bps)//10000
    for x in allocations:
        wallet=str(x.get("wallet","")).strip(); amount=int(x.get("amount_atomic",-1))
        if not wallet or amount < 0: blockers.append("INVALID_ALLOCATION"); continue
        if wallet in seen: blockers.append("DUPLICATE_RECIPIENT")
        seen.add(wallet); total += amount
        if amount > max_allowed: blockers.append("ANTI_WHALE_RECIPIENT_CAP_EXCEEDED")
        rows.append({"wallet":wallet,"amount_atomic":amount})
    if total > pool_atomic: blockers.append("ALLOCATION_EXCEEDS_POOL")
    prior=previously_settled_manifest_sha256s or set()
    if manifest_sha256 in prior: blockers.append("REPLAYED_SETTLEMENT_MANIFEST")
    out={"schema":SCHEMA,"epoch_id":epoch_id,"manifest_sha256":manifest_sha256,
         "pool_atomic":pool_atomic,"allocation_total_atomic":total,
         "max_recipient_bps":max_recipient_bps,"max_recipient_atomic":max_allowed,
         "recipient_count":len(seen),"blockers":sorted(set(blockers)),
         "sign":False,"broadcast":False,"financial_execution":False,
         "requires_user_controlled_multisig":True,
         "status":"BLOCKED" if blockers else "READY_FOR_SIMULATION"}
    out["risk_gate_sha256"]=digest(out)
    return out
