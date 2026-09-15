#!/usr/bin/env python3
"""Deterministic THF active-user reward allocation planner.

Consumes a validated eligibility commitment and an integer epoch revenue amount.
Produces planning allocations only: no keys, signing, transaction construction or broadcast.
"""
from __future__ import annotations
import hashlib, json
from decimal import Decimal, ROUND_DOWN

SCHEMA="thf-tokenops-reward-allocation/v1"
ACTIVE_USER_BPS=3500
BPS=10000

def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"))
def digest(v): return hashlib.sha256(_canon(v).encode()).hexdigest()

def allocate(*,epoch_id:str,revenue_units:int,eligibility:dict,anti_whale_bps:int=100)->dict:
    if revenue_units < 0: raise ValueError("revenue_units must be non-negative")
    if not (1 <= anti_whale_bps <= ACTIVE_USER_BPS): raise ValueError("invalid anti_whale_bps")
    blockers=[]
    if eligibility.get("status")!="COMMITTED_FOR_TREASURY_PLANNING": blockers.append("ELIGIBILITY_NOT_COMMITTED")
    if eligibility.get("epoch_id")!=epoch_id: blockers.append("EPOCH_MISMATCH")
    rows=eligibility.get("rows",[]); total_weight=int(eligibility.get("total_weight",0))
    pool=(revenue_units*ACTIVE_USER_BPS)//BPS
    cap=(pool*anti_whale_bps)//ACTIVE_USER_BPS if pool else 0
    allocations=[]; allocated=0
    if pool and total_weight<=0: blockers.append("ZERO_TOTAL_WEIGHT")
    if not blockers and pool:
        for r in sorted(rows,key=lambda x:x["subject_id"]):
            raw=(pool*int(r["weight"]))//total_weight
            amount=min(raw,cap)
            allocations.append({"subject_id":r["subject_id"],"amount_units":amount,"capped":amount<raw})
            allocated+=amount
    remainder=pool-allocated
    out={"schema":SCHEMA,"epoch_id":epoch_id,"revenue_units":revenue_units,
         "active_user_bps":ACTIVE_USER_BPS,"active_user_pool_units":pool,
         "anti_whale_bps_of_active_pool":anti_whale_bps,"per_subject_cap_units":cap,
         "eligibility_commitment_sha256":eligibility.get("eligibility_commitment_sha256"),
         "allocations":allocations,"allocated_units":allocated,"remainder_units":remainder,
         "blockers":sorted(set(blockers)),"contains_private_keys":False,"sign":False,
         "broadcast":False,"financial_execution":False,
         "status":"BLOCKED" if blockers else "ALLOCATION_PLAN_READY"}
    out["allocation_plan_sha256"]=digest(out)
    return out
