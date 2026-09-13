#!/usr/bin/env python3
"""Fail-closed governance authority requirements for THF TokenOps policy mutation.

This module never invents a governance threshold. It only validates whether an externally
approved governance charter explicitly names the canonical THF mint, policy-mutation scope,
decision threshold/process, and evidence hashes. It does not sign, broadcast, execute,
or mutate authoritative policy.
"""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict, List

NETWORK="solana-mainnet-beta"
MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
SCHEMA="thf-tokenops-governance-authority-requirements/v1"
SENSITIVE={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature",
"signatures","signed_transaction","raw_transaction","serialized_transaction","transaction_bytes",
"instruction_bytes","service_account_key","secret"}

def digest(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def scan(v:Any,path="$")->None:
    if isinstance(v,dict):
        for k,x in v.items():
            n=str(k).lower().replace("-","_")
            if n in SENSITIVE: raise ValueError(f"sensitive field rejected: {path}.{k}")
            scan(x,f"{path}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): scan(x,f"{path}[{i}]")

def _policy_guard(policy:Dict[str,Any])->None:
    scan(policy,"$.policy")
    if policy.get("network")!=NETWORK or policy.get("mint")!=MINT: raise ValueError("policy canonical target mismatch")
    econ=policy.get("economics",{})
    if econ.get("active_user_revenue_share")!=0.35: raise ValueError("35% policy drift")
    if econ.get("approved_supply_floor_target_ui")!="8000000000": raise ValueError("8B floor drift")

def build_requirements(policy:Dict[str,Any], treasury_policy:Dict[str,Any],
                       governance_charter:Dict[str,Any]|None=None)->Dict[str,Any]:
    _policy_guard(policy); scan(treasury_policy,"$.treasury_policy")
    if treasury_policy.get("network")!=NETWORK or treasury_policy.get("mint")!=MINT:
        raise ValueError("treasury policy canonical target mismatch")
    if treasury_policy.get("control_model")!="external_multisig_required":
        raise ValueError("treasury control model drift")
    blockers:List[str]=[]
    charter_status="not_provided"
    charter_hash=None
    if governance_charter is None:
        blockers.append("POLICY_MUTATION_GOVERNANCE_CHARTER_NOT_APPROVED")
    else:
        scan(governance_charter,"$.governance_charter")
        charter_hash=digest(governance_charter)
        if governance_charter.get("network")!=NETWORK or governance_charter.get("mint")!=MINT:
            blockers.append("GOVERNANCE_CHARTER_TARGET_MISMATCH")
        if governance_charter.get("status")!="approved":
            blockers.append("GOVERNANCE_CHARTER_NOT_APPROVED")
        if governance_charter.get("policy_mutation_scope")!="tokenops_policy_parameters":
            blockers.append("POLICY_MUTATION_SCOPE_NOT_EXPLICIT")
        if not isinstance(governance_charter.get("minimum_approvals"),int) or governance_charter.get("minimum_approvals",0)<1:
            blockers.append("POLICY_MUTATION_THRESHOLD_NOT_EXPLICIT")
        if governance_charter.get("decision_process") not in ("external_multisig","dao_then_external_multisig"):
            blockers.append("POLICY_MUTATION_DECISION_PROCESS_NOT_EXPLICIT")
        if not isinstance(governance_charter.get("approval_evidence_sha256"),str) or len(governance_charter.get("approval_evidence_sha256",""))!=64:
            blockers.append("GOVERNANCE_APPROVAL_EVIDENCE_HASH_MISSING")
        charter_status="approved_review_only" if not blockers else "incomplete_or_unapproved"
    r={
      "schema":SCHEMA,"network":NETWORK,"mint":MINT,
      "policy_sha256":digest(policy),"treasury_policy_sha256":digest(treasury_policy),
      "governance_charter_sha256":charter_hash,"governance_charter_status":charter_status,
      "constitutional_constraints":{
        "active_user_revenue_share":"35%",
        "approved_supply_floor_target_ui":"8000000000",
        "minting":"forbidden",
        "authority_change":"forbidden",
        "wave_mawja":"untouched"},
      "required_policy_decisions":[
        "distribution.per_user_cap","distribution.epoch_budget_cap","distribution.claim_or_push_model",
        "distribution.reserve","signer.production_policy","vesting.locking_terms",
        "rewards.lock_reward_terms","treasury.inventory_ownership_balances"],
      "blockers":sorted(set(blockers)),
      "policy_mutation_ready_for_human_review":not blockers,
      "policy_mutation_authorized":False,"execution_authorized":False,"financial_effect":False,
      "transaction_bytes_created":False,"private_key_required":False,"wave_mawja_untouched":True}
    r["requirements_sha256"]=digest(r)
    return r
