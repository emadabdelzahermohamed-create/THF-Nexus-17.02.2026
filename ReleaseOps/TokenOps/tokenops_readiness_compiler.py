#!/usr/bin/env python3
"""Unified truthful readiness compiler for THF TokenOps."""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict

NETWORK="solana-mainnet-beta"; MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
PROGRAM="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def compile_readiness(policy:Dict[str,Any], treasury_policy:Dict[str,Any], audit:Dict[str,Any],
                      governance:Dict[str,Any], treasury_bundle:Dict[str,Any])->Dict[str,Any]:
    for label,v in (("policy",policy),("treasury_policy",treasury_policy),("audit",audit),("governance",governance),("treasury_bundle",treasury_bundle)):
        if v.get("network")!=NETWORK or v.get("mint")!=MINT: raise ValueError(f"{label} target mismatch")
    econ=policy.get("economics",{}); dc=policy.get("distribution_controls",{})
    if econ.get("active_user_revenue_share")!=0.35: raise ValueError("35% policy drift")
    if econ.get("approved_supply_floor_target_ui")!="8000000000": raise ValueError("8B floor drift")
    blockers=[]
    def add(x):
        if x not in blockers: blockers.append(x)
    if dc.get("per_user_cap") is None: add("PER_USER_CAP_UNAPPROVED")
    if dc.get("epoch_budget_cap") is None: add("EPOCH_BUDGET_CAP_UNAPPROVED")
    if dc.get("claim_or_push_model") in (None,"to_be_selected_after_treasury_design"): add("DISTRIBUTION_DELIVERY_MODEL_UNAPPROVED")
    if dc.get("distribution_reserve_account") is None: add("DISTRIBUTION_RESERVE_UNAPPROVED")
    if policy.get("signer_policy",{}).get("production_policy_status")!="approved": add("PRODUCTION_SIGNER_POLICY_UNAPPROVED")
    if policy.get("vesting_controls",{}).get("authoritative_terms_status")!="approved": add("VESTING_TERMS_UNAPPROVED")
    if policy.get("lock_reward_controls",{}).get("authoritative_terms_status")!="approved": add("LOCK_REWARD_TERMS_UNAPPROVED")
    if treasury_bundle.get("status")!="verified": add("TREASURY_OWNERSHIP_BALANCE_UNVERIFIED")
    if governance.get("policy_mutation_ready_for_human_review") is not True: add("POLICY_MUTATION_GOVERNANCE_UNAPPROVED")
    onchain=[]
    if audit.get("program_id")!=PROGRAM: onchain.append("token_program")
    if audit.get("decimals")!=8: onchain.append("decimals")
    if audit.get("mint_authority") is not None: onchain.append("mint_authority")
    if audit.get("freeze_authority") is not None: onchain.append("freeze_authority")
    try:
        supply=int(audit.get("supply_raw","0"))
        if supply<8_000_000_000*10**8: onchain.append("supply_below_8b_floor")
    except: onchain.append("supply_parse")
    if onchain: add("ONCHAIN_CANONICAL_DRIFT")
    thresholds={k:v.get("minimum_approvals") for k,v in treasury_policy.get("approval_classes",{}).items()}
    r={"schema":"thf-tokenops-unified-readiness/v1","network":NETWORK,"mint":MINT,
       "policy_sha256":digest(policy),"treasury_policy_sha256":digest(treasury_policy),
       "audit_sha256":digest(audit),"governance_requirements_sha256":governance.get("requirements_sha256"),
       "treasury_bundle_sha256":treasury_bundle.get("bundle_sha256"),
       "onchain_core":{"status":"PASS" if not onchain else "DRIFT","drift":onchain,
           "program_id":audit.get("program_id"),"decimals":audit.get("decimals"),
           "supply_ui":audit.get("supply_ui"),"mint_authority":audit.get("mint_authority"),
           "freeze_authority":audit.get("freeze_authority"),
           "holder_concentration_status":audit.get("largest_accounts_status"),
           "recent_signature_count":audit.get("recent_signature_count")},
       "economic_constraints":{"active_user_revenue_share_bps":3500,"supply_floor_target_ui":"8000000000",
           "theoretical_burn_headroom_ui":str(max(0,int(audit.get("supply_raw","0"))//10**8-8_000_000_000))},
       "approval_thresholds":thresholds,"blocker_count":len(blockers),"blockers":blockers,
       "financial_gate_status":"FAIL_CLOSED" if blockers else "EVIDENCE_COMPLETE_REVIEW_ONLY",
       "exact_remaining_signer_action":"none_until_fail_closed_blockers_are_resolved" if blockers else "user_controlled_approval_then_required_external_multisig_threshold",
       "execution_authorized":False,"broadcast_allowed":False,"financial_effect":False,
       "transaction_bytes_created":False,"private_key_required":False,"wave_mawja_untouched":True}
    r["readiness_sha256"]=digest(r); return r
