#!/usr/bin/env python3
"""Bind THF reward allocation to immutable epoch/accounting evidence.
Planning only: never signs, broadcasts, settles, or handles private keys.
"""
from __future__ import annotations
import hashlib, json

SCHEMA="thf-tokenops-reward-epoch-commitment/v1"

def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"))
def digest(v): return hashlib.sha256(_canon(v).encode()).hexdigest()
def _sha(v): return isinstance(v,str) and len(v)==64 and all(c in "0123456789abcdef" for c in v.lower())

def commit(*,allocation:dict, revenue_evidence_sha256:str, accounting_ledger_sha256:str,
           policy_sha256:str, source_commit_sha:str)->dict:
    blockers=[]
    if allocation.get("status")!="ALLOCATION_PLAN_READY": blockers.append("ALLOCATION_NOT_READY")
    if allocation.get("active_user_bps")!=3500: blockers.append("ACTIVE_USER_SHARE_MISMATCH")
    if allocation.get("sign") is not False or allocation.get("broadcast") is not False or allocation.get("financial_execution") is not False:
        blockers.append("UNSAFE_ALLOCATION_FLAGS")
    for name,value in (("REVENUE_EVIDENCE_SHA256",revenue_evidence_sha256),("ACCOUNTING_LEDGER_SHA256",accounting_ledger_sha256),("POLICY_SHA256",policy_sha256)):
        if not _sha(value): blockers.append(name+"_INVALID")
    if not isinstance(source_commit_sha,str) or len(source_commit_sha)!=40: blockers.append("SOURCE_COMMIT_SHA_INVALID")
    out={"schema":SCHEMA,"epoch_id":allocation.get("epoch_id"),
         "allocation_plan_sha256":allocation.get("allocation_plan_sha256"),
         "eligibility_commitment_sha256":allocation.get("eligibility_commitment_sha256"),
         "revenue_evidence_sha256":revenue_evidence_sha256,
         "accounting_ledger_sha256":accounting_ledger_sha256,"policy_sha256":policy_sha256,
         "source_commit_sha":source_commit_sha,"active_user_bps":3500,
         "allocated_units":allocation.get("allocated_units"),"remainder_units":allocation.get("remainder_units"),
         "blockers":sorted(set(blockers)),"contains_private_keys":False,"sign":False,"broadcast":False,
         "financial_execution":False,"status":"BLOCKED" if blockers else "COMMITTED_FOR_SIMULATION"}
    out["reward_epoch_commitment_sha256"]=digest(out)
    return out
