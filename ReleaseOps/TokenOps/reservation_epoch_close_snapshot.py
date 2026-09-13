#!/usr/bin/env python3
"""Deterministic append-only THF reservation lifecycle journal / epoch-close snapshot.

Accounting/review evidence only. Never constructs, signs, submits, broadcasts,
transfers, burns, settles, migrates treasury balances, changes authorities, or
executes DAO decisions.
"""
from __future__ import annotations
import hashlib, json, re
from typing import Any, Dict, List, Tuple

CANONICAL_MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
CANONICAL_NETWORK="solana-mainnet-beta"
LIFECYCLE_SCHEMA="thf-tokenops-reservation-lifecycle-accounting/v1"
SNAPSHOT_SCHEMA="thf-tokenops-reservation-epoch-close-snapshot/v1"
HEX64=re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature","signed_transaction","raw_transaction","serialized_transaction"}

def canonical_sha256(value: Any)->str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def _scan(value: Any,path="$" )->None:
    if isinstance(value,dict):
        for k,v in value.items():
            n=str(k).lower().replace("-","_")
            if n in FORBIDDEN_KEYS: raise ValueError(f"forbidden sensitive/signature field at {path}.{k}")
            _scan(v,f"{path}.{k}")
    elif isinstance(value,list):
        for i,v in enumerate(value): _scan(v,f"{path}[{i}]")

def _hex(value: Any,label:str)->str:
    if not isinstance(value,str) or not HEX64.fullmatch(value): raise ValueError(f"invalid {label} SHA-256")
    return value

def _raw(value: Any,label:str,allow_zero=True)->int:
    if isinstance(value,bool): raise ValueError(f"{label} must be integer raw amount")
    if isinstance(value,int): n=value
    elif isinstance(value,str) and value.isdigit(): n=int(value)
    else: raise ValueError(f"{label} must be integer raw amount")
    if n<0 or (not allow_zero and n==0): raise ValueError(f"invalid {label}")
    return n

def _verify_digest(obj:Dict[str,Any],field:str,label:str)->str:
    d=_hex(obj.get(field),label)
    body=dict(obj); body.pop(field,None)
    if canonical_sha256(body)!=d: raise ValueError(f"{label} SHA-256 mismatch")
    return d

def _verify_execution(ex:Dict[str,Any],label:str)->None:
    for key in ("transaction_created","transaction_signed","transaction_submitted","broadcast_allowed","financial_effect","settlement_executed","burn_executed","treasury_migrated","dao_decision_executed","private_key_used"):
        if key in ex and ex.get(key) is not False: raise ValueError(f"unsafe {label} execution flag: {key}")
    if ex.get("wave_mawja_untouched") is not True: raise ValueError(f"{label} WAVE isolation flag is not preserved")

def _verify_lifecycle(lc:Dict[str,Any])->Tuple[str,str,str,List[str],List[str],List[Dict[str,Any]],Dict[str,Any]]:
    if lc.get("schema")!=LIFECYCLE_SCHEMA: raise ValueError("unexpected lifecycle schema")
    if lc.get("network")!=CANONICAL_NETWORK or lc.get("mint")!=CANONICAL_MINT: raise ValueError("lifecycle target mismatch")
    digest=_verify_digest(lc,"reservation_lifecycle_sha256","reservation lifecycle")
    envelope=_hex(lc.get("budget_envelope_sha256"),"budget envelope")
    reservation=_hex(lc.get("source_reservation_reconciliation_sha256"),"reservation reconciliation")
    prior=lc.get("prior_reservation_lifecycle_sha256")
    if prior is not None: _hex(prior,"prior lifecycle")
    _verify_execution(lc.get("execution",{}),"lifecycle")
    events=list(lc.get("lifecycle_events",[]))
    event_ids=[]
    for e in events:
        eid=str(e.get("event_id","")).strip()
        if not eid or eid in event_ids: raise ValueError("blank/duplicate lifecycle event_id")
        if e.get("action") not in ("release","cancel","replace"): raise ValueError("unsupported lifecycle action in evidence")
        event_ids.append(eid)
    active=list(lc.get("active_reservations",[]))
    active_ids=[]; active_total=0
    for row in active:
        rid=str(row.get("reservation_id","")).strip()
        if not rid or rid in active_ids: raise ValueError("blank/duplicate active reservation_id")
        if not str(row.get("subject_id","")).strip() or not str(row.get("wallet","")).strip(): raise ValueError("invalid active reservation")
        active_ids.append(rid); active_total += _raw(row.get("amount_raw"),"active reservation amount",False)
    acct=dict(lc.get("accounting",{}))
    source_total=_raw(acct.get("source_reserved_total_raw"),"source reserved total")
    stated_active=_raw(acct.get("active_reserved_total_raw"),"active reserved total")
    released=_raw(acct.get("released_or_cancelled_net_raw"),"released/cancelled total")
    if stated_active!=active_total or source_total!=stated_active+released: raise ValueError("lifecycle accounting invariant mismatch")
    if acct.get("active_reservation_count")!=len(active) or acct.get("lifecycle_event_count")!=len(events): raise ValueError("lifecycle count invariant mismatch")
    return digest,envelope,reservation,sorted(set(str(x) for x in lc.get("blockers",[]))),event_ids,active,acct

def _verify_prior(snapshot:Dict[str,Any])->str:
    if snapshot.get("schema")!=SNAPSHOT_SCHEMA: raise ValueError("unexpected prior epoch snapshot schema")
    if snapshot.get("network")!=CANONICAL_NETWORK or snapshot.get("mint")!=CANONICAL_MINT: raise ValueError("prior snapshot target mismatch")
    d=_verify_digest(snapshot,"epoch_close_snapshot_sha256","epoch-close snapshot")
    _verify_execution(snapshot.get("execution",{}),"prior snapshot")
    return d

def compile_epoch_close_snapshot(lifecycle:Dict[str,Any],request:Dict[str,Any],prior_snapshot:Dict[str,Any]|None=None)->Dict[str,Any]:
    _scan(lifecycle); _scan(request)
    if prior_snapshot is not None: _scan(prior_snapshot)
    lifecycle_sha,envelope_sha,reservation_sha,blockers,event_ids,active,acct=_verify_lifecycle(lifecycle)
    if request.get("network")!=CANONICAL_NETWORK or request.get("mint")!=CANONICAL_MINT: raise ValueError("snapshot request target mismatch")
    epoch_id=str(request.get("epoch_id","")).strip()
    if not epoch_id: raise ValueError("epoch_id is required")
    if request.get("source_reservation_lifecycle_sha256")!=lifecycle_sha: raise ValueError("snapshot request detached from lifecycle head")
    if request.get("budget_envelope_sha256")!=envelope_sha or request.get("source_reservation_reconciliation_sha256")!=reservation_sha: raise ValueError("snapshot request detached from upstream accounting")
    prior_snapshot_sha=None
    if prior_snapshot is None:
        if request.get("expected_prior_epoch_close_snapshot_sha256") not in (None,""): raise ValueError("unexpected prior snapshot anchor")
        if lifecycle.get("prior_reservation_lifecycle_sha256") is not None: raise ValueError("non-genesis lifecycle requires prior epoch snapshot")
    else:
        prior_snapshot_sha=_verify_prior(prior_snapshot)
        if request.get("expected_prior_epoch_close_snapshot_sha256")!=prior_snapshot_sha: raise ValueError("stale/forked prior snapshot head")
        for field in ("epoch_id","budget_envelope_sha256","source_reservation_reconciliation_sha256"):
            expected=epoch_id if field=="epoch_id" else (envelope_sha if field=="budget_envelope_sha256" else reservation_sha)
            if prior_snapshot.get(field)!=expected: raise ValueError(f"prior snapshot {field} mismatch")
        if lifecycle.get("prior_reservation_lifecycle_sha256")!=prior_snapshot.get("source_reservation_lifecycle_sha256"): raise ValueError("lifecycle fork/stale head detected")
        prev_ids=list(prior_snapshot.get("lifecycle_event_ids",[]))
        if event_ids[:len(prev_ids)]!=prev_ids or len(event_ids)<=len(prev_ids): raise ValueError("lifecycle event journal is not append-only")
        if prior_snapshot.get("journal_event_count")!=len(prev_ids): raise ValueError("prior snapshot journal count mismatch")
    active_digest=canonical_sha256(sorted(active,key=lambda x:str(x.get("reservation_id",""))))
    result={
        "schema":SNAPSHOT_SCHEMA,"network":CANONICAL_NETWORK,"mint":CANONICAL_MINT,"epoch_id":epoch_id,"request_id":str(request.get("request_id","")),
        "budget_envelope_sha256":envelope_sha,"source_reservation_reconciliation_sha256":reservation_sha,"source_reservation_lifecycle_sha256":lifecycle_sha,
        "prior_epoch_close_snapshot_sha256":prior_snapshot_sha,"lifecycle_event_ids":event_ids,"journal_event_count":len(event_ids),"active_reservations_sha256":active_digest,
        "accounting":{"source_reserved_total_raw":str(_raw(acct["source_reserved_total_raw"],"source reserved total")),"active_reserved_total_raw":str(_raw(acct["active_reserved_total_raw"],"active reserved total")),"released_or_cancelled_net_raw":str(_raw(acct["released_or_cancelled_net_raw"],"released/cancelled total")),"active_reservation_count":len(active),"lifecycle_event_count":len(event_ids)},
        "epoch_close_review_eligible":len(blockers)==0,"blockers":blockers,
        "execution":{"transaction_created":False,"transaction_signed":False,"transaction_submitted":False,"broadcast_allowed":False,"financial_effect":False,"settlement_executed":False,"burn_executed":False,"treasury_migrated":False,"dao_decision_executed":False,"private_key_used":False,"external_multisig_required":True,"wave_mawja_untouched":True},
    }
    result["epoch_close_snapshot_sha256"]=canonical_sha256(result)
    return result
