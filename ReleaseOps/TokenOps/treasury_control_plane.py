#!/usr/bin/env python3
"""Deterministic, non-signing THF treasury planning primitives.

Produces auditable allocation plans only. It never signs, broadcasts or mutates chain state.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_DOWN
import hashlib, json

SCHEMA="thf-tokenops-treasury-control-plane/v1"
ACTIVE_USER_SHARE=Decimal("0.35")

@dataclass(frozen=True)
class Recipient:
    account_id:str
    wallet:str
    weight:str
    eligible:bool=True


def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"))
def digest(v): return hashlib.sha256(_canon(v).encode()).hexdigest()

def plan_distribution(revenue_atomic:int, recipients:list[Recipient], *, max_recipient_bps:int=500)->dict:
    if revenue_atomic < 0: raise ValueError("revenue_atomic must be non-negative")
    if not 0 < max_recipient_bps <= 10000: raise ValueError("invalid cap")
    pool=int((Decimal(revenue_atomic)*ACTIVE_USER_SHARE).to_integral_value(rounding=ROUND_DOWN))
    eligible=[r for r in recipients if r.eligible and Decimal(r.weight)>0]
    total=sum((Decimal(r.weight) for r in eligible),Decimal(0))
    rows=[]; allocated=0
    for r in sorted(eligible,key=lambda x:(x.account_id,x.wallet)):
        raw=0 if total==0 else int((Decimal(pool)*Decimal(r.weight)/total).to_integral_value(rounding=ROUND_DOWN))
        cap=(pool*max_recipient_bps)//10000
        amount=min(raw,cap); allocated+=amount
        rows.append({"account_id":r.account_id,"wallet":r.wallet,"amount_atomic":amount,"weight":r.weight,"capped":amount<raw})
    out={"schema":SCHEMA,"revenue_atomic":revenue_atomic,"active_user_share_bps":3500,"pool_atomic":pool,
         "max_recipient_bps":max_recipient_bps,"allocations":rows,"allocated_atomic":allocated,
         "unallocated_atomic":pool-allocated,"sign":False,"broadcast":False}
    out["manifest_sha256"]=digest(out)
    return out

def validate_vesting(total_atomic:int, released_atomic:int, cliff_unix:int, end_unix:int, now_unix:int)->dict:
    if min(total_atomic,released_atomic)<0 or released_atomic>total_atomic or end_unix<cliff_unix: raise ValueError("invalid vesting state")
    if now_unix<cliff_unix: vested=0
    elif now_unix>=end_unix: vested=total_atomic
    elif end_unix==cliff_unix: vested=total_atomic
    else: vested=(total_atomic*(now_unix-cliff_unix))//(end_unix-cliff_unix)
    return {"schema":"thf-tokenops-vesting-plan/v1","total_atomic":total_atomic,"vested_atomic":vested,
            "released_atomic":released_atomic,"claimable_atomic":max(0,vested-released_atomic),"settle":False,"broadcast":False}

def burn_gap(current_supply_atomic:int,target_supply_atomic:int)->dict:
    if min(current_supply_atomic,target_supply_atomic)<0: raise ValueError("negative supply")
    return {"schema":"thf-tokenops-burn-plan/v1","current_supply_atomic":current_supply_atomic,
            "target_supply_atomic":target_supply_atomic,"planned_gap_atomic":max(0,current_supply_atomic-target_supply_atomic),
            "execute":False,"broadcast":False,"requires_governance_and_multisig":True}
