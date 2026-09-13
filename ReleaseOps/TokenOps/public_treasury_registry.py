#!/usr/bin/env python3
"""Public-only THF treasury registry validation.

This module never discovers or guesses treasury addresses. It validates explicit public entries and
keeps treasury inventory non-authoritative until governance evidence and read-only balance evidence exist.
"""
from __future__ import annotations
import hashlib,json,re
from typing import Any,Dict

MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"; NETWORK="solana-mainnet-beta"
B58=re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")
HEX64=re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature","signatures",
"transaction_bytes","instruction_bytes","signed_transaction","serialized_transaction","service_account_key","secret"}

def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
def scan(v,p="$"):
    if isinstance(v,dict):
        for k,x in v.items():
            if str(k).lower().replace("-","_") in FORBIDDEN: raise ValueError(f"forbidden field {p}.{k}")
            scan(x,f"{p}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): scan(x,f"{p}[{i}]")

def validate_registry(registry:Dict[str,Any])->Dict[str,Any]:
    scan(registry)
    if registry.get("network")!=NETWORK or registry.get("mint")!=MINT: raise ValueError("target mismatch")
    if registry.get("schema")!="thf-tokenops-public-treasury-registry/v1": raise ValueError("schema mismatch")
    entries=registry.get("accounts")
    if not isinstance(entries,list): raise ValueError("accounts must be a list")
    rows=[]; seen=set(); blockers=[]
    for a in entries:
        token=a.get("token_account_pubkey"); owner=a.get("owner_pubkey")
        if not isinstance(token,str) or not B58.match(token): raise ValueError("invalid token account")
        if token in seen: raise ValueError("duplicate token account")
        seen.add(token)
        if not isinstance(owner,str) or not B58.match(owner): raise ValueError("invalid owner pubkey")
        gov=a.get("governance_approval_hash"); obs=a.get("balance_observation_hash")
        if not isinstance(gov,str) or not HEX64.match(gov): blockers.append(f"{token}:governance_approval_hash_missing")
        if not isinstance(obs,str) or not HEX64.match(obs): blockers.append(f"{token}:balance_observation_hash_missing")
        raw=a.get("observed_balance_raw")
        if not isinstance(raw,int) or raw<0: blockers.append(f"{token}:observed_balance_raw_missing")
        roles=a.get("roles",[])
        if not isinstance(roles,list) or not roles: blockers.append(f"{token}:roles_missing")
        allowed={"distribution_reserve","vesting_reserve","lock_reward_reserve","burn_reserve","operations_treasury"}
        if any(x not in allowed for x in roles): raise ValueError("unknown treasury role")
        rows.append({"token_account_pubkey":token,"owner_pubkey":owner,"roles":sorted(set(roles)),
            "governance_approval_hash":gov,"balance_observation_hash":obs,"observed_balance_raw":raw})
    rows.sort(key=lambda x:x["token_account_pubkey"])
    if not rows: blockers.append("authoritative_public_treasury_registry_empty")
    role_counts={}
    for r in rows:
        for role in r["roles"]: role_counts[role]=role_counts.get(role,0)+1
    if role_counts.get("distribution_reserve",0)!=1: blockers.append("exactly_one_distribution_reserve_required")
    ready=not blockers
    result={"schema":"thf-tokenops-public-treasury-registry-receipt/v1","network":NETWORK,"mint":MINT,
      "registry_sha256":sha(registry),"normalized_accounts":rows,"role_counts":role_counts,
      "total_verified_observed_balance_raw":sum((x["observed_balance_raw"] or 0) for x in rows) if ready else None,
      "authoritative_inventory_ready":ready,"blockers":sorted(blockers),
      "address_discovery_performed":False,"private_material_accepted":False,
      "transfer_authorized":False,"burn_authorized":False,"financial_effect":False,"wave_mawja_untouched":True}
    result["registry_receipt_sha256"]=sha(result); return result
