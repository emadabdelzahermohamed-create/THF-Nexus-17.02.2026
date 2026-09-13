#!/usr/bin/env python3
"""Public/read-only treasury evidence bundle validator for canonical THF token accounts."""
from __future__ import annotations
import hashlib,json,re
from typing import Any,Dict,List

NETWORK="solana-mainnet-beta"
MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
SCHEMA="thf-tokenops-treasury-evidence-bundle/v1"
B58=re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")
HEX64=re.compile(r"^[0-9a-f]{64}$")
SENSITIVE={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature","signatures",
"signed_transaction","raw_transaction","serialized_transaction","transaction_bytes","instruction_bytes","secret"}

def digest(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def scan(v:Any,path="$")->None:
    if isinstance(v,dict):
        for k,x in v.items():
            if str(k).lower().replace("-","_") in SENSITIVE: raise ValueError(f"sensitive field rejected: {path}.{k}")
            scan(x,f"{path}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): scan(x,f"{path}[{i}]")

def build_bundle(entries:List[Dict[str,Any]], audit:Dict[str,Any], max_slot_lag:int=1500)->Dict[str,Any]:
    scan(entries,"$.entries"); scan(audit,"$.audit")
    if audit.get("network")!=NETWORK or audit.get("mint")!=MINT: raise ValueError("audit target mismatch")
    if max_slot_lag<0: raise ValueError("negative slot lag")
    audit_slot=int(audit.get("rpc_slot",0))
    accepted=[]; rejected=[]
    seen=set(); total_raw=0
    allowed_roles={"distribution_reserve","burn_reserve","vesting_reserve","lock_reward_reserve","operating_treasury"}
    for i,e in enumerate(entries):
        errs=[]
        acct=e.get("token_account"); owner=e.get("owner")
        if not isinstance(acct,str) or not B58.fullmatch(acct): errs.append("invalid_token_account")
        if acct in seen: errs.append("duplicate_token_account")
        if acct: seen.add(acct)
        if not isinstance(owner,str) or not B58.fullmatch(owner): errs.append("invalid_owner")
        if e.get("network")!=NETWORK or e.get("mint")!=MINT: errs.append("canonical_target_mismatch")
        if e.get("role") not in allowed_roles: errs.append("unsupported_role")
        bal=e.get("balance_raw")
        if not isinstance(bal,int) or bal<0: errs.append("invalid_balance_raw")
        slot=e.get("observed_slot")
        if not isinstance(slot,int) or slot<=0: errs.append("invalid_observed_slot")
        elif audit_slot and slot>audit_slot: errs.append("observation_slot_ahead_of_audit")
        elif audit_slot and audit_slot-slot>max_slot_lag: errs.append("stale_observation")
        for h in ("ownership_evidence_sha256","balance_evidence_sha256"):
            if not isinstance(e.get(h),str) or not HEX64.fullmatch(e.get(h,"")): errs.append(f"invalid_{h}")
        if e.get("canonical_mint_verified") is not True: errs.append("canonical_mint_not_verified")
        if e.get("owner_control_verified") is not True: errs.append("owner_control_not_verified")
        record={"index":i,"token_account":acct,"role":e.get("role"),"errors":errs}
        if errs: rejected.append(record)
        else:
            accepted.append({k:e[k] for k in ("token_account","owner","role","balance_raw","observed_slot",
                "ownership_evidence_sha256","balance_evidence_sha256")})
            total_raw+=bal
    status="verified" if accepted and not rejected else ("incomplete" if entries else "missing")
    r={"schema":SCHEMA,"network":NETWORK,"mint":MINT,"audit_sha256":digest(audit),
       "audit_slot":audit_slot,"status":status,"accepted_count":len(accepted),"rejected_count":len(rejected),
       "verified_treasury_owned_balance_raw":total_raw if status=="verified" else None,
       "accepted_entries":accepted,"rejected_entries":rejected,
       "authoritative_for_financial_execution":False,"execution_authorized":False,"financial_effect":False,
       "transaction_bytes_created":False,"private_key_required":False,"wave_mawja_untouched":True}
    r["bundle_sha256"]=digest(r); return r
