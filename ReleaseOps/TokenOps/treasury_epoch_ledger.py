#!/usr/bin/env python3
"""Deterministic THF treasury epoch ledger and unsigned settlement manifests.

Accounting/planning only: never signs, broadcasts, transfers, burns, settles vesting,
or executes governance.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib, json

SCHEMA="thf-tokenops-epoch-ledger/v1"

def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"))
def digest(v): return hashlib.sha256(_canon(v).encode()).hexdigest()

@dataclass(frozen=True)
class EpochInput:
    epoch_id:str
    source_commit_sha:str
    revenue_atomic:int
    distribution_manifest_sha256:str
    policy_sha256:str


def build_epoch(inp:EpochInput, *, pool_atomic:int, allocated_atomic:int, unallocated_atomic:int)->dict:
    if min(inp.revenue_atomic,pool_atomic,allocated_atomic,unallocated_atomic)<0:
        raise ValueError("negative accounting value")
    if allocated_atomic+unallocated_atomic != pool_atomic:
        raise ValueError("pool reconciliation failed")
    if pool_atomic != (inp.revenue_atomic*3500)//10000:
        raise ValueError("35% active-user share mismatch")
    out={"schema":SCHEMA,**asdict(inp),"active_user_share_bps":3500,
         "pool_atomic":pool_atomic,"allocated_atomic":allocated_atomic,
         "unallocated_atomic":unallocated_atomic,"reconciled":True,
         "financial_execution":False,"broadcast":False}
    out["ledger_sha256"]=digest(out)
    return out


def unsigned_settlement_manifest(epoch:dict, allocations:list[dict], *, treasury_pubkey:str|None)->dict:
    if not epoch.get("reconciled") or epoch.get("financial_execution"):
        raise ValueError("epoch is not safe/reconciled")
    total=sum(int(x["amount_atomic"]) for x in allocations)
    if total != int(epoch["allocated_atomic"]):
        raise ValueError("allocation total mismatch")
    rows=sorted(({"wallet":str(x["wallet"]),"amount_atomic":int(x["amount_atomic"])} for x in allocations),
                key=lambda x:(x["wallet"],x["amount_atomic"]))
    out={"schema":"thf-tokenops-unsigned-settlement/v1","epoch_id":epoch["epoch_id"],
         "epoch_ledger_sha256":epoch["ledger_sha256"],"treasury_pubkey":treasury_pubkey,
         "allocations":rows,"total_atomic":total,"sign":False,"broadcast":False,
         "requires_user_controlled_multisig":True,
         "status":"BLOCKED_TREASURY_PUBKEY" if not treasury_pubkey else "READY_FOR_SIMULATION"}
    out["manifest_sha256"]=digest(out)
    return out


def accounting_delta(opening_atomic:int, inflow_atomic:int, outflow_atomic:int, closing_atomic:int)->dict:
    if min(opening_atomic,inflow_atomic,outflow_atomic,closing_atomic)<0: raise ValueError("negative balance")
    expected=opening_atomic+inflow_atomic-outflow_atomic
    return {"schema":"thf-tokenops-accounting-reconciliation/v1","opening_atomic":opening_atomic,
            "inflow_atomic":inflow_atomic,"outflow_atomic":outflow_atomic,"closing_atomic":closing_atomic,
            "expected_closing_atomic":expected,"reconciled":expected==closing_atomic,
            "financial_execution":False}
