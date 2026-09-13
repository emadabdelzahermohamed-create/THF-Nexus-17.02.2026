#!/usr/bin/env python3
"""Deterministic THF cross-epoch accounting roll-forward gate.

Accounting/review evidence only. Never constructs, signs, submits, broadcasts,
transfers, burns, settles, migrates treasury balances, changes authorities, or
executes DAO decisions.
"""
from __future__ import annotations
import hashlib, json, re
from typing import Any, Dict

CANONICAL_MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
CANONICAL_NETWORK="solana-mainnet-beta"
SNAPSHOT_SCHEMA="thf-tokenops-reservation-epoch-close-snapshot/v1"
ROLLFORWARD_SCHEMA="thf-tokenops-cross-epoch-accounting-rollforward/v1"
HEX64=re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature","signed_transaction","raw_transaction","serialized_transaction"}

def canonical_sha256(value:Any)->str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def _scan(v:Any,path="$" )->None:
    if isinstance(v,dict):
        for k,x in v.items():
            n=str(k).lower().replace("-","_")
            if n in FORBIDDEN_KEYS: raise ValueError(f"forbidden sensitive/signature field at {path}.{k}")
            _scan(x,f"{path}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): _scan(x,f"{path}[{i}]")

def _raw(v:Any,label:str)->int:
    if isinstance(v,bool): raise ValueError(f"{label} must be integer raw amount")
    if isinstance(v,int): n=v
    elif isinstance(v,str) and v.isdigit(): n=int(v)
    else: raise ValueError(f"{label} must be integer raw amount")
    if n<0: raise ValueError(f"invalid {label}")
    return n

def _hex(v:Any,label:str)->str:
    if not isinstance(v,str) or not HEX64.fullmatch(v): raise ValueError(f"invalid {label} SHA-256")
    return v

def _verify_digest(obj:Dict[str,Any],field:str,label:str)->str:
    d=_hex(obj.get(field),label); body=dict(obj); body.pop(field,None)
    if canonical_sha256(body)!=d: raise ValueError(f"{label} SHA-256 mismatch")
    return d

def _safe_execution(ex:Dict[str,Any],label:str)->None:
    for k in ("transaction_created","transaction_signed","transaction_submitted","broadcast_allowed","financial_effect","settlement_executed","burn_executed","treasury_migrated","dao_decision_executed","private_key_used"):
        if k in ex and ex.get(k) is not False: raise ValueError(f"unsafe {label} execution flag: {k}")
    if ex.get("wave_mawja_untouched") is not True: raise ValueError(f"{label} WAVE isolation flag is not preserved")

def _verify_close(s:Dict[str,Any])->str:
    if s.get("schema")!=SNAPSHOT_SCHEMA or s.get("network")!=CANONICAL_NETWORK or s.get("mint")!=CANONICAL_MINT: raise ValueError("prior epoch-close target/schema mismatch")
    d=_verify_digest(s,"epoch_close_snapshot_sha256","epoch-close snapshot")
    _safe_execution(s.get("execution",{}),"prior epoch-close")
    a=s.get("accounting",{})
    if _raw(a.get("source_reserved_total_raw"),"source reserved total") != _raw(a.get("active_reserved_total_raw"),"active reserved total") + _raw(a.get("released_or_cancelled_net_raw"),"released/cancelled total"): raise ValueError("prior epoch-close accounting invariant mismatch")
    return d

def compile_cross_epoch_rollforward(prior_close:Dict[str,Any],next_budget:Dict[str,Any],request:Dict[str,Any])->Dict[str,Any]:
    _scan(prior_close); _scan(next_budget); _scan(request)
    prior_sha=_verify_close(prior_close)
    if request.get("network")!=CANONICAL_NETWORK or request.get("mint")!=CANONICAL_MINT: raise ValueError("roll-forward request target mismatch")
    if request.get("prior_epoch_close_snapshot_sha256")!=prior_sha: raise ValueError("stale/forked prior epoch-close head")
    prior_epoch=str(prior_close.get("epoch_id","")).strip(); next_epoch=str(request.get("next_epoch_id","")).strip()
    if not prior_epoch or not next_epoch or prior_epoch==next_epoch: raise ValueError("invalid epoch transition")
    budget_sha=_verify_digest(next_budget,"budget_envelope_sha256","next budget envelope")
    if next_budget.get("network")!=CANONICAL_NETWORK or next_budget.get("mint")!=CANONICAL_MINT: raise ValueError("next budget target mismatch")
    if request.get("next_budget_envelope_sha256")!=budget_sha: raise ValueError("roll-forward detached from next budget envelope")
    if str(next_budget.get("epoch_id","")).strip()!=next_epoch: raise ValueError("next budget epoch mismatch")
    carry=_raw(prior_close.get("accounting",{}).get("active_reserved_total_raw"),"carry-forward active reserved total")
    new_budget=_raw(next_budget.get("accounting",{}).get("approved_budget_raw"),"next approved budget")
    opening=carry+new_budget
    blockers=sorted(set(str(x) for x in prior_close.get("blockers",[])) | set(str(x) for x in next_budget.get("blockers",[])))
    result={"schema":ROLLFORWARD_SCHEMA,"network":CANONICAL_NETWORK,"mint":CANONICAL_MINT,"prior_epoch_id":prior_epoch,"next_epoch_id":next_epoch,"request_id":str(request.get("request_id","")),"prior_epoch_close_snapshot_sha256":prior_sha,"next_budget_envelope_sha256":budget_sha,"accounting":{"carry_forward_active_reserved_raw":str(carry),"next_approved_budget_raw":str(new_budget),"next_opening_accounting_total_raw":str(opening)},"rollforward_review_eligible":len(blockers)==0,"blockers":blockers,"execution":{"transaction_created":False,"transaction_signed":False,"transaction_submitted":False,"broadcast_allowed":False,"financial_effect":False,"settlement_executed":False,"burn_executed":False,"treasury_migrated":False,"dao_decision_executed":False,"private_key_used":False,"external_multisig_required":True,"wave_mawja_untouched":True}}
    result["cross_epoch_rollforward_sha256"]=canonical_sha256(result)
    return result
