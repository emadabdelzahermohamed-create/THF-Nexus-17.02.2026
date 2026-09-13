#!/usr/bin/env python3
"""THF reward-allocation accounting proof.

Produces deterministic accounting/simulation evidence only. It never creates transaction
instructions/bytes, signatures, claims, transfers, settlements, or financial effects.
"""
from __future__ import annotations
import hashlib, json, re
from typing import Any, Dict, List

MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK="solana-mainnet-beta"
B58=re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")
HEX64=re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature",
"signatures","transaction_bytes","instruction_bytes","signed_transaction","serialized_transaction",
"service_account_key","secret"}

def sha(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def scan(v:Any,p="$")->None:
    if isinstance(v,dict):
        for k,x in v.items():
            if str(k).lower().replace("-","_") in FORBIDDEN:
                raise ValueError(f"forbidden field {p}.{k}")
            scan(x,f"{p}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): scan(x,f"{p}[{i}]")

def build_allocation_accounting(reconciliation:Dict[str,Any], eligibility:Dict[str,Any])->Dict[str,Any]:
    scan(reconciliation); scan(eligibility)
    if reconciliation.get("network")!=NETWORK or reconciliation.get("mint")!=MINT:
        raise ValueError("reconciliation target mismatch")
    if eligibility.get("network")!=NETWORK or eligibility.get("mint")!=MINT:
        raise ValueError("eligibility target mismatch")
    if eligibility.get("schema")!="thf-tokenops-eligibility-evidence/v1":
        raise ValueError("eligibility schema mismatch")
    epoch_id=eligibility.get("epoch_id")
    if not isinstance(epoch_id,str) or not epoch_id.strip(): raise ValueError("epoch_id required")
    evidence_hash=eligibility.get("activity_evidence_set_sha256")
    if not isinstance(evidence_hash,str) or not HEX64.fullmatch(evidence_hash):
        raise ValueError("activity evidence set hash required")
    participants=eligibility.get("participants",[])
    if not isinstance(participants,list): raise ValueError("participants must be list")
    normalized=[]; seen=set(); total_weight=0
    for p in participants:
        account=p.get("reward_account_pubkey")
        if not isinstance(account,str) or not B58.fullmatch(account): raise ValueError("invalid reward account")
        if account in seen: raise ValueError("duplicate reward account")
        seen.add(account)
        weight=p.get("weight")
        if not isinstance(weight,int) or weight<=0: raise ValueError("weight must be positive int")
        user_evidence=p.get("eligibility_sha256")
        if not isinstance(user_evidence,str) or not HEX64.fullmatch(user_evidence):
            raise ValueError("eligibility_sha256 required")
        normalized.append({"reward_account_pubkey":account,"weight":weight,"eligibility_sha256":user_evidence})
        total_weight+=weight
    normalized.sort(key=lambda x:x["reward_account_pubkey"])
    dist=reconciliation.get("distribution",{})
    actionable_budget=dist.get("actionable_budget_raw"); per_user_cap=dist.get("per_user_cap")
    blockers=list(reconciliation.get("binding_blockers",[]))
    allocation_rows=[]; distributed=0
    remainder=actionable_budget if isinstance(actionable_budget,int) and actionable_budget>=0 else None
    can_simulate=(reconciliation.get("readiness")=="READY_FOR_OFFLINE_APPROVAL_REVIEW" and
                  isinstance(actionable_budget,int) and actionable_budget>=0 and
                  isinstance(per_user_cap,int) and per_user_cap>=0 and total_weight>0 and bool(normalized))
    if can_simulate:
        for p in normalized:
            pro_rata=(actionable_budget*p["weight"])//total_weight
            amount=min(pro_rata,per_user_cap)
            allocation_rows.append({"reward_account_pubkey":p["reward_account_pubkey"],
                "eligibility_sha256":p["eligibility_sha256"],"weight":p["weight"],
                "simulated_allocation_raw":amount})
            distributed+=amount
        remainder=actionable_budget-distributed
        if distributed<0 or remainder<0 or distributed+remainder!=actionable_budget:
            raise ValueError("allocation conservation failure")
    result={"schema":"thf-tokenops-reward-allocation-accounting/v1","network":NETWORK,"mint":MINT,
      "epoch_id":epoch_id,"inputs":{"reconciliation_sha256":reconciliation.get("reconciliation_sha256"),
        "eligibility_evidence_sha256":sha(eligibility),"activity_evidence_set_sha256":evidence_hash},
      "participant_count":len(normalized),"total_weight":total_weight,
      "budget_raw":actionable_budget,"per_user_cap_raw":per_user_cap,
      "simulation_performed":can_simulate,"simulated_rows":allocation_rows,
      "simulated_distributed_raw":distributed if can_simulate else None,
      "simulated_remainder_raw":remainder if can_simulate else None,
      "conservation_proven":bool(can_simulate and distributed+remainder==actionable_budget),
      "binding_blockers":sorted(set(blockers)),"settlement_authorized":False,"claim_authorized":False,
      "transaction_instructions_created":False,"transaction_bytes_created":False,
      "transaction_signed":False,"transaction_submitted":False,"broadcast_allowed":False,
      "financial_effect":False,"private_key_used":False,"wave_mawja_untouched":True}
    result["allocation_accounting_sha256"]=sha(result); return result
