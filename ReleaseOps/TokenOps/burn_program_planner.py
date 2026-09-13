#!/usr/bin/env python3
"""THF treasury-owned burn program review planner.

Planning evidence only. No burn instruction, transaction, signature or broadcast is produced.
"""
from __future__ import annotations
import hashlib,json,re
from typing import Any,Dict
MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv";NETWORK="solana-mainnet-beta";DECIMALS=8
FLOOR_RAW=8_000_000_000*10**DECIMALS
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

def build_burn_program(reconciliation:Dict[str,Any], proposal:Dict[str,Any])->Dict[str,Any]:
    scan(reconciliation);scan(proposal)
    if reconciliation.get("network")!=NETWORK or reconciliation.get("mint")!=MINT: raise ValueError("target mismatch")
    if proposal.get("schema")!="thf-tokenops-burn-program-proposal/v1": raise ValueError("proposal schema mismatch")
    gov=proposal.get("governance_proposal_sha256")
    if not isinstance(gov,str) or not HEX64.fullmatch(gov): raise ValueError("governance proposal hash required")
    requested=proposal.get("requested_total_burn_raw"); epochs=proposal.get("epochs")
    if not isinstance(requested,int) or requested<0: raise ValueError("invalid requested burn")
    if not isinstance(epochs,int) or epochs<=0: raise ValueError("invalid epoch count")
    burn=reconciliation.get("burn",{}); current=int(burn.get("current_supply_raw",0))
    headroom=int(burn.get("theoretical_headroom_raw",0)); verified=burn.get("verified_burn_reserve_raw")
    review_cap=burn.get("review_cap_raw"); threshold=reconciliation.get("approval_thresholds",{}).get("burn")
    blockers=list(reconciliation.get("binding_blockers",[]))
    if threshold!=3: blockers.append("burn_multisig_threshold_not_3")
    if reconciliation.get("readiness")!="READY_FOR_OFFLINE_APPROVAL_REVIEW": blockers.append("financial_reconciliation_not_ready")
    if verified is None or review_cap is None: blockers.append("verified_treasury_burn_reserve_missing")
    proposed_total=None; per_epoch=None; projected_supply=None
    if not blockers:
        proposed_total=min(requested,int(review_cap),headroom); per_epoch=proposed_total//epochs; projected_supply=current-proposed_total
        if projected_supply<FLOOR_RAW: raise ValueError("8B floor violation")
    result={"schema":"thf-tokenops-burn-program-review/v1","network":NETWORK,"mint":MINT,
      "inputs":{"reconciliation_sha256":reconciliation.get("reconciliation_sha256"),
        "proposal_sha256":sha(proposal),"governance_proposal_sha256":gov},
      "requested_total_burn_raw":requested,"review_cap_raw":review_cap,
      "reviewable_total_burn_raw":proposed_total,"epochs":epochs,
      "base_per_epoch_review_amount_raw":per_epoch,"projected_supply_raw":projected_supply,
      "approved_floor_raw":FLOOR_RAW,"required_multisig_approvals":threshold,
      "blockers":sorted(set(blockers)),"review_ready":not blockers,"execution_authorized":False,
      "transaction_instructions_created":False,"transaction_bytes_created":False,
      "transaction_signed":False,"transaction_submitted":False,"broadcast_allowed":False,
      "financial_effect":False,"private_key_used":False,"wave_mawja_untouched":True}
    result["burn_program_review_sha256"]=sha(result); return result
