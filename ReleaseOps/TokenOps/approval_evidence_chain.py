#!/usr/bin/env python3
"""Hash-only approval evidence chain for THF TokenOps.

This does not collect cryptographic signatures and cannot authorize or execute financial actions.
"""
from __future__ import annotations
import hashlib,json,re
from typing import Any,Dict
MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv";NETWORK="solana-mainnet-beta"
HEX64=re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature","signatures",
"transaction_bytes","instruction_bytes","signed_transaction","serialized_transaction","service_account_key","secret"}
THRESHOLDS={"reward_epoch":2,"vesting_settlement":2,"burn":3,"treasury_transfer":3}

def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
def scan(v,p="$"):
    if isinstance(v,dict):
        for k,x in v.items():
            if str(k).lower().replace("-","_") in FORBIDDEN: raise ValueError(f"forbidden field {p}.{k}")
            scan(x,f"{p}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): scan(x,f"{p}[{i}]")

def build_approval_packet(intent_class:str, intent_hash:str, reconciliation:Dict[str,Any], review_hash:str|None=None)->Dict[str,Any]:
    scan(reconciliation)
    if intent_class not in THRESHOLDS: raise ValueError("unsupported intent class")
    if not isinstance(intent_hash,str) or not HEX64.fullmatch(intent_hash): raise ValueError("intent hash required")
    if review_hash is not None and (not isinstance(review_hash,str) or not HEX64.fullmatch(review_hash)): raise ValueError("invalid review hash")
    if reconciliation.get("network")!=NETWORK or reconciliation.get("mint")!=MINT: raise ValueError("target mismatch")
    authoritative=reconciliation.get("approval_thresholds",{}).get(intent_class)
    if authoritative!=THRESHOLDS[intent_class]: raise ValueError("approval threshold drift")
    ready=(reconciliation.get("readiness")=="READY_FOR_OFFLINE_APPROVAL_REVIEW" and not reconciliation.get("binding_blockers"))
    result={"schema":"thf-tokenops-approval-evidence-packet/v1","network":NETWORK,"mint":MINT,
      "intent_class":intent_class,"intent_sha256":intent_hash,"review_sha256":review_hash,
      "reconciliation_sha256":reconciliation.get("reconciliation_sha256"),
      "required_approvals":authoritative,"approval_collection_status":"not_collected",
      "approval_identity_records":[],"approval_evidence_hashes":[],
      "ready_to_request_user_controlled_offline_approvals":ready,
      "exact_remaining_action":"request_user_controlled_offline_approval_and_external_multisig_threshold" if ready else "none_until_fail_closed_blockers_are_resolved",
      "cryptographic_signatures_collected":False,"execution_authorized":False,
      "transaction_instructions_created":False,"transaction_bytes_created":False,
      "transaction_signed":False,"transaction_submitted":False,"broadcast_allowed":False,
      "financial_effect":False,"private_key_used":False,"wave_mawja_untouched":True}
    result["approval_packet_sha256"]=sha(result); return result
