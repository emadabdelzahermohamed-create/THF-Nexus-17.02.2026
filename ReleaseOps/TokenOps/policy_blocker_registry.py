#!/usr/bin/env python3
"""Deterministic fail-closed registry of unresolved THF TokenOps policy/evidence blockers."""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict, List

MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK="solana-mainnet-beta"
PROGRAM="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
SCHEMA="thf-tokenops-policy-blocker-registry/v1"
SENSITIVE={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair",
           "signed_transaction","raw_transaction","serialized_transaction","transaction_bytes","instruction_bytes"}

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

def _base_validate(policy:Dict[str,Any], treasury:Dict[str,Any], audit:Dict[str,Any])->None:
    for v in (policy,treasury,audit): scan(v)
    for label,v in (("policy",policy),("treasury",treasury),("audit",audit)):
        if v.get("network")!=NETWORK or v.get("mint")!=MINT: raise ValueError(f"{label} canonical target mismatch")
    if policy.get("economics",{}).get("active_user_revenue_share")!=0.35: raise ValueError("35% policy drift")
    if policy.get("economics",{}).get("approved_supply_floor_target_ui")!="8000000000": raise ValueError("8B floor drift")
    if treasury.get("control_model")!="external_multisig_required": raise ValueError("treasury control model drift")
    if treasury.get("hard_guards",{}).get("wave_mawja_untouched") is not True: raise ValueError("WAVE isolation drift")

def build_registry(policy:Dict[str,Any], treasury:Dict[str,Any], audit:Dict[str,Any],
                   treasury_evidence:Dict[str,Any]|None=None)->Dict[str,Any]:
    _base_validate(policy,treasury,audit)
    blockers:List[Dict[str,Any]]=[]; observations:List[Dict[str,Any]]=[]
    def add(code,domain,needed,owner="governance",binding=True):
        blockers.append({"code":code,"domain":domain,"required_action_or_evidence":needed,
                         "decision_owner":owner,"blocks_binding_financial_action":binding})
    dc=policy.get("distribution_controls",{})
    if dc.get("per_user_cap") is None:
        add("PER_USER_CAP_UNAPPROVED","distribution","approved numeric anti-whale per-user cap plus governance/policy-transition evidence")
    if dc.get("epoch_budget_cap") is None:
        add("EPOCH_BUDGET_CAP_UNAPPROVED","distribution","approved numeric epoch budget cap plus governance/policy-transition evidence")
    if dc.get("distribution_reserve_account") is None:
        add("DISTRIBUTION_RESERVE_UNAPPROVED","treasury","authoritative canonical-mint reserve token-account public key and ownership evidence")
    if dc.get("claim_or_push_model") in (None,"to_be_selected_after_treasury_design"):
        add("DISTRIBUTION_DELIVERY_MODEL_UNAPPROVED","distribution","approved claim-vs-push settlement model and replay/idempotency policy")
    if policy.get("signer_policy",{}).get("production_policy_status")!="approved":
        add("PRODUCTION_SIGNER_POLICY_UNAPPROVED","governance","approved production external-multisig signer policy and user-controlled approval procedure","user_and_governance")
    vesting=policy.get("vesting_controls",{})
    if not vesting or vesting.get("authoritative_terms_status")!="approved":
        add("VESTING_TERMS_UNAPPROVED","vesting","authoritative vesting schedule/beneficiary/settlement terms")
    lock=policy.get("lock_reward_controls",{})
    if not lock or lock.get("authoritative_terms_status")!="approved":
        add("LOCK_REWARD_TERMS_UNAPPROVED","locking","authoritative lock duration, reward formula, caps, early-unlock and abuse controls")
    verified_treasury=False
    if treasury_evidence is not None:
        scan(treasury_evidence,"$.treasury_evidence")
        verified_treasury=(treasury_evidence.get("status")=="verified" and treasury_evidence.get("network")==NETWORK and
                           treasury_evidence.get("mint")==MINT and isinstance(treasury_evidence.get("verified_treasury_owned_balance_raw"),int))
    if not verified_treasury:
        add("TREASURY_OWNERSHIP_BALANCE_UNVERIFIED","treasury","read-only token-account ownership, mint, authority/multisig and balance evidence for each treasury-controlled account","treasury_custody")
    drift=[]
    if audit.get("program_id")!=PROGRAM: drift.append("token_program")
    if audit.get("decimals")!=8: drift.append("decimals")
    if audit.get("mint_authority") is not None: drift.append("mint_authority")
    if audit.get("freeze_authority") is not None: drift.append("freeze_authority")
    try:
        if int(audit.get("supply_raw","0")) < 8_000_000_000*10**8: drift.append("supply_below_8b_floor")
    except Exception: drift.append("supply_parse")
    if drift:
        add("ONCHAIN_CANONICAL_DRIFT","monitoring","human incident review before any further financial planning: "+",".join(drift),"incident_response")
    if audit.get("largest_accounts_status")!="ok":
        observations.append({"code":"HOLDER_CONCENTRATION_UNAVAILABLE","severity":"degraded_optional","required_action_or_evidence":"retry read-only holder concentration through an RPC provider that permits getTokenLargestAccounts","blocks_binding_financial_action":False})
    reg={"schema":SCHEMA,"network":NETWORK,"mint":MINT,"policy_sha256":digest(policy),"treasury_policy_sha256":digest(treasury),"audit_sha256":digest(audit),
         "blocker_count":len(blockers),"blockers":blockers,"observations":observations,
         "financial_gate_status":"FAIL_CLOSED" if blockers else "POLICY_EVIDENCE_COMPLETE_REVIEW_ONLY",
         "exact_remaining_signer_action":"none_until_fail_closed_blockers_are_resolved" if blockers else "user_controlled_approval_then_required_external_multisig_threshold",
         "execution_authorized":False,"broadcast_allowed":False,"financial_effect":False,"private_key_required":False,"wave_mawja_untouched":True}
    reg["registry_sha256"]=digest(reg); return reg
