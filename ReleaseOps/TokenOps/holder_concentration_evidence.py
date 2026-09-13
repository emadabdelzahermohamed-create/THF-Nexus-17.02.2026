#!/usr/bin/env python3
"""Normalize optional holder-concentration evidence without turning RPC degradation into a financial authorization."""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict, List

MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK="solana-mainnet-beta"
FORBIDDEN={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature","signatures",
           "transaction_bytes","instruction_bytes","signed_transaction","serialized_transaction","service_account_key"}

def sha(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def scan(v:Any,p:str="$")->None:
    if isinstance(v,dict):
        for k,x in v.items():
            if str(k).lower().replace("-","_") in FORBIDDEN:
                raise ValueError(f"forbidden field {p}.{k}")
            scan(x,f"{p}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): scan(x,f"{p}[{i}]")

def build_holder_evidence(audit:Dict[str,Any])->Dict[str,Any]:
    scan(audit)
    if audit.get("network")!=NETWORK or audit.get("mint")!=MINT:
        raise ValueError("target mismatch")
    supply=int(audit.get("supply_raw","0"))
    if supply<=0: raise ValueError("invalid supply")
    status=audit.get("largest_accounts_status")
    raw=audit.get("largest_accounts") or []
    rows:List[Dict[str,Any]]=[]
    if status=="ok":
        for item in raw:
            address=item.get("address")
            amount=item.get("amount")
            if not isinstance(address,str) or len(address)<32: raise ValueError("invalid token account")
            try: amount_i=int(amount)
            except Exception as e: raise ValueError("invalid holder amount") from e
            if amount_i<0: raise ValueError("negative holder amount")
            rows.append({"token_account_pubkey":address,"amount_raw":amount_i})
        rows.sort(key=lambda x:(-x["amount_raw"],x["token_account_pubkey"]))
    elif raw:
        raise ValueError("largest account rows supplied while status is not ok")
    def pct(n:int):
        if not rows: return None
        return round(sum(x["amount_raw"] for x in rows[:n])*100/supply,8)
    receipt={
      "schema":"thf-tokenops-holder-concentration-evidence/v1","network":NETWORK,"mint":MINT,
      "audit_sha256":sha(audit),"rpc_slot":audit.get("rpc_slot"),"source_status":status,
      "account_count_observed":len(rows),"top1_percent":pct(1),"top5_percent":pct(5),"top10_percent":pct(10),
      "holder_concentration_available":status=="ok" and bool(rows),
      "degraded_reason":None if status=="ok" and rows else "optional_largest_accounts_rpc_unavailable_or_empty",
      "anti_whale_policy_decision_authorized":False,"financial_effect":False,"broadcast_allowed":False,
      "wave_mawja_untouched":True
    }
    receipt["holder_evidence_sha256"]=sha(receipt)
    return receipt
