#!/usr/bin/env python3
"""Non-broadcast THF transaction-intent manifest validator.

This is a review manifest only. It never builds instructions, serialized transactions,
signatures, or broadcast payloads.
"""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict
MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"; NETWORK="solana-mainnet-beta"
ALLOWED={"reward_epoch","vesting_settlement","burn","treasury_transfer"}
FORBIDDEN={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature","signatures",
"transaction","transaction_bytes","raw_transaction","serialized_transaction","instruction","instruction_bytes",
"secret","service_account_key"}
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
def scan(v,p="$"):
    if isinstance(v,dict):
        for k,x in v.items():
            if str(k).lower().replace("-","_") in FORBIDDEN: raise ValueError(f"forbidden field {p}.{k}")
            scan(x,f"{p}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): scan(x,f"{p}[{i}]")

def build_manifest(policy:Dict[str,Any],treasury:Dict[str,Any],intent:Dict[str,Any],
                   prerequisite_hashes:Dict[str,str])->Dict[str,Any]:
    scan(policy);scan(treasury);scan(intent);scan(prerequisite_hashes)
    if policy.get("mint")!=MINT or treasury.get("mint")!=MINT: raise ValueError("mint mismatch")
    if policy.get("network")!=NETWORK or treasury.get("network")!=NETWORK: raise ValueError("network mismatch")
    cls=intent.get("class")
    if cls not in ALLOWED: raise ValueError("unsupported intent class")
    amount=intent.get("amount_raw")
    if not isinstance(amount,int) or amount<=0: raise ValueError("amount_raw must be positive integer")
    for k,v in prerequisite_hashes.items():
        if not isinstance(v,str) or len(v)!=64: raise ValueError(f"{k} must be sha256")
    ap=treasury.get("approval_classes",{}).get(cls,{})
    threshold=ap.get("minimum_approvals")
    if not isinstance(threshold,int) or threshold<1: raise ValueError("invalid threshold")
    blockers=[]
    dc=policy.get("distribution_controls",{})
    if cls=="reward_epoch":
        for key,label in (("per_user_cap","per_user_cap_not_approved"),("epoch_budget_cap","epoch_budget_cap_not_approved"),
                          ("distribution_reserve_account","distribution_reserve_account_not_configured")):
            if dc.get(key) is None: blockers.append(label)
    if cls=="burn" and intent.get("post_burn_supply_raw") is not None:
        floor=int(policy["economics"]["approved_supply_floor_target_raw"])
        if int(intent["post_burn_supply_raw"])<floor: blockers.append("burn_would_cross_8b_supply_floor")
    if policy.get("signer_policy",{}).get("production_policy_status")!="approved":
        blockers.append("production_signer_policy_not_approved")
    result={"schema":"thf-tokenops-intent-review-manifest/v1","network":NETWORK,"mint":MINT,
      "policy_sha256":sha(policy),"treasury_policy_sha256":sha(treasury),
      "intent":{"class":cls,"amount_raw":amount,"intent_reference":intent.get("intent_reference"),
                "destination_reference_hash":intent.get("destination_reference_hash"),
                "post_burn_supply_raw":intent.get("post_burn_supply_raw")},
      "prerequisite_hashes":dict(sorted(prerequisite_hashes.items())),
      "minimum_multisig_approvals":threshold,"execution_model":ap.get("execution"),
      "blockers":sorted(set(blockers)),"review_ready":not blockers,
      "approval_collected":False,"signatures_collected":False,"instructions_created":False,
      "transaction_created":False,"transaction_serialized":False,"broadcast_allowed":False,
      "execution_authorized":False,"financial_effect":False,
      "exact_remaining_signer_action":"none_until_fail_closed_blockers_are_resolved" if blockers
       else f"user_controlled_approval_then_{threshold}_of_n_external_multisig_offline"}
    result["manifest_sha256"]=sha(result);return result
