#!/usr/bin/env python3
"""Bind policy/audit/blocker/risk evidence into a truthful non-executing readiness attestation."""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict
MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"; NETWORK="solana-mainnet-beta"
def dig(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
def build_attestation(policy:Dict[str,Any], treasury:Dict[str,Any], audit:Dict[str,Any], registry:Dict[str,Any], risk:Dict[str,Any])->Dict[str,Any]:
    for name,v in (("policy",policy),("treasury",treasury),("audit",audit),("registry",registry),("risk",risk)):
        if v.get("mint")!=MINT or v.get("network")!=NETWORK: raise ValueError(f"{name} target mismatch")
    if registry.get("policy_sha256")!=dig(policy) or registry.get("treasury_policy_sha256")!=dig(treasury) or registry.get("audit_sha256")!=dig(audit): raise ValueError("registry evidence mismatch")
    ev=risk.get("evidence",{})
    if ev.get("policy_sha256")!=dig(policy) or ev.get("treasury_policy_sha256")!=dig(treasury) or ev.get("audit_sha256")!=dig(audit): raise ValueError("risk evidence mismatch")
    blockers=int(registry.get("blocker_count",-1)); status="FAIL_CLOSED" if blockers else "READY_FOR_USER_AND_MULTISIG_REVIEW_ONLY"
    a={"schema":"thf-tokenops-financial-readiness-attestation/v1","network":NETWORK,"mint":MINT,
       "source_hashes":{"policy_sha256":dig(policy),"treasury_policy_sha256":dig(treasury),"audit_sha256":dig(audit),"blocker_registry_sha256":dig(registry),"risk_envelope_sha256":dig(risk)},
       "readiness_status":status,"blocker_count":blockers,"exact_remaining_signer_action":registry.get("exact_remaining_signer_action"),
       "claims":{"financial_gate_complete":False,"onchain_execution_ready":False,"signed_evidence_present":False,"onchain_execution_evidence_present":False},
       "execution":{"transaction_created":False,"transaction_signed":False,"transaction_submitted":False,"broadcast_allowed":False,"financial_effect":False,"private_key_used":False},
       "wave_mawja_untouched":True}
    a["attestation_sha256"]=dig(a); return a
