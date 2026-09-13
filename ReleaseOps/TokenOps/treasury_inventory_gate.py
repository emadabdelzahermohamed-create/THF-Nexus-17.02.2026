#!/usr/bin/env python3
"""THF treasury inventory/ownership evidence gate (read-only and hash-bound)."""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict,List
MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"; NETWORK="solana-mainnet-beta"
FORBIDDEN={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature","signatures",
"transaction_bytes","instruction_bytes","secret","service_account_key"}
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
def scan(v,p="$"):
    if isinstance(v,dict):
        for k,x in v.items():
            if str(k).lower().replace("-","_") in FORBIDDEN: raise ValueError(f"forbidden field {p}.{k}")
            scan(x,f"{p}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): scan(x,f"{p}[{i}]")

def build_inventory(policy:Dict[str,Any], accounts:List[Dict[str,Any]])->Dict[str,Any]:
    scan(policy);scan(accounts)
    if policy.get("network")!=NETWORK or policy.get("mint")!=MINT: raise ValueError("target mismatch")
    rows=[]; blockers=[]
    for a in accounts:
        pub=a.get("token_account_pubkey"); owner=a.get("owner_pubkey")
        att=a.get("ownership_attestation_hash"); bal=a.get("balance_raw")
        if not isinstance(pub,str) or len(pub)<32: raise ValueError("invalid token account")
        if not isinstance(owner,str) or len(owner)<32: raise ValueError("invalid owner")
        if not isinstance(att,str) or len(att)!=64: raise ValueError("ownership attestation must be sha256")
        if not isinstance(bal,int) or bal<0: raise ValueError("invalid balance")
        rows.append({"token_account_pubkey":pub,"owner_pubkey":owner,
                     "ownership_attestation_hash":att,"balance_raw":bal})
    rows.sort(key=lambda x:x["token_account_pubkey"])
    reserve=policy.get("distribution_controls",{}).get("distribution_reserve_account")
    if reserve is None: blockers.append("distribution_reserve_account_not_configured")
    elif reserve not in {x["token_account_pubkey"] for x in rows}: blockers.append("configured_reserve_not_in_inventory")
    if not rows: blockers.append("verified_treasury_inventory_missing")
    result={"schema":"thf-tokenops-treasury-inventory/v1","network":NETWORK,"mint":MINT,
      "policy_sha256":sha(policy),"inventory_sha256":sha(rows),"accounts":rows,
      "total_observed_balance_raw":sum(x["balance_raw"] for x in rows),"reserve_account":reserve,
      "blockers":blockers,"inventory_ready":not blockers,"ownership_binding":"attestation_hash_only",
      "custody_action_performed":False,"transfer_authorized":False,"burn_authorized":False,
      "financial_effect":False}
    result["receipt_sha256"]=sha(result);return result
