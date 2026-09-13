#!/usr/bin/env python3
"""Deterministic THF reward-epoch allocation simulator.

Safe by construction:
- hash/public-reference inputs only
- current authoritative policy stays fail-closed while caps/reserve/signer policy are absent
- produces no Solana instruction/transaction/signature material
- never authorizes financial effect or broadcast
"""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict, List

MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK="solana-mainnet-beta"
FORBIDDEN={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature","signatures",
"transaction","transaction_bytes","raw_transaction","serialized_transaction","instruction","instruction_bytes",
"secret","service_account_key","health_data","biometric_data"}
SCHEMA="thf-tokenops-allocation-epoch-simulation/v1"

def sha(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def scan(v:Any,p="$")->None:
    if isinstance(v,dict):
        for k,x in v.items():
            n=str(k).lower().replace("-","_")
            if n in FORBIDDEN: raise ValueError(f"forbidden field {p}.{k}")
            scan(x,f"{p}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): scan(x,f"{p}[{i}]")

def _policy(policy:Dict[str,Any])->Dict[str,Any]:
    scan(policy)
    if policy.get("network")!=NETWORK or policy.get("mint")!=MINT: raise ValueError("policy target mismatch")
    e=policy.get("economics",{})
    if e.get("active_user_revenue_share")!=0.35: raise ValueError("35% policy drift")
    dc=policy.get("distribution_controls",{})
    return dc

def simulate_epoch(policy:Dict[str,Any], epoch_id:str, gross_revenue_raw:int,
                   eligible_users:List[Dict[str,Any]])->Dict[str,Any]:
    dc=_policy(policy); scan(eligible_users)
    if not epoch_id or gross_revenue_raw<0: raise ValueError("invalid epoch/revenue")
    seen=set()
    normalized=[]
    for row in eligible_users:
        subject=row.get("subject_hash")
        weight=row.get("activity_weight")
        evidence=row.get("activity_evidence_hash")
        if not isinstance(subject,str) or len(subject)!=64: raise ValueError("subject_hash must be sha256")
        if subject in seen: raise ValueError("duplicate subject")
        seen.add(subject)
        if not isinstance(evidence,str) or len(evidence)!=64: raise ValueError("activity_evidence_hash must be sha256")
        if not isinstance(weight,int) or weight<=0: raise ValueError("activity_weight must be positive integer")
        normalized.append({"subject_hash":subject,"activity_weight":weight,"activity_evidence_hash":evidence})
    normalized.sort(key=lambda x:x["subject_hash"])

    theoretical=(gross_revenue_raw*35)//100
    blockers=[]
    per_user=dc.get("per_user_cap")
    epoch_cap=dc.get("epoch_budget_cap")
    reserve=dc.get("distribution_reserve_account")
    if per_user is None: blockers.append("per_user_cap_not_approved")
    if epoch_cap is None: blockers.append("epoch_budget_cap_not_approved")
    if reserve is None: blockers.append("distribution_reserve_account_not_configured")
    if policy.get("signer_policy",{}).get("production_policy_status")!="approved":
        blockers.append("production_signer_policy_not_approved")
    if not dc.get("anti_sybil_required"): blockers.append("anti_sybil_requirement_missing")
    if not dc.get("activity_evidence_required"): blockers.append("activity_evidence_requirement_missing")
    if not dc.get("treasury_balance_required"): blockers.append("treasury_balance_requirement_missing")

    budget=min(theoretical,int(epoch_cap)) if epoch_cap is not None else None
    allocations=[]
    conservation=None
    if budget is not None and per_user is not None and normalized:
        total_weight=sum(r["activity_weight"] for r in normalized)
        assigned=0
        cap=int(per_user)
        for r in normalized:
            amount=min(cap,(budget*r["activity_weight"])//total_weight)
            allocations.append({**r,"simulated_amount_raw":amount})
            assigned+=amount
        conservation={"budget_raw":budget,"assigned_raw":assigned,"unassigned_raw":budget-assigned,
                      "assigned_le_budget":assigned<=budget}
    result={"schema":SCHEMA,"network":NETWORK,"mint":MINT,"epoch_id":epoch_id,
      "policy_sha256":sha(policy),"eligible_set_sha256":sha(normalized),
      "gross_revenue_raw":gross_revenue_raw,"share_bps":3500,
      "theoretical_35_percent_budget_raw":theoretical,"approved_epoch_budget_raw":budget,
      "candidate_count":len(normalized),"simulated_allocations":allocations if not blockers else [],
      "conservation":conservation if not blockers else None,"blockers":sorted(set(blockers)),
      "simulation_ready":not blockers,"allocation_authorized":False,"execution_authorized":False,
      "broadcast_allowed":False,"financial_effect":False,"transaction_material_created":False,
      "exact_remaining_action":"approve_authoritative_caps_reserve_and_signer_policy_before_actionable_allocation"
        if blockers else "review_simulation_then_user_controlled_approval_and_external_multisig_offline"}
    result["simulation_sha256"]=sha(result)
    return result
