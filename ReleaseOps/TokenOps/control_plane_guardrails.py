#!/usr/bin/env python3
"""THF TokenOps deterministic policy-bound planning/control-plane guardrails.

Planning and evidence only: no transaction bytes, instructions, signatures, keys, RPC writes,
or financial effects are accepted or produced.
"""
from __future__ import annotations
import hashlib, json, re
from typing import Any, Dict, Iterable, List

MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK="solana-mainnet-beta"
PROGRAM="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
DECIMALS=8
SUPPLY_FLOOR_UI=8_000_000_000
SHARE=0.35
SCHEMA="thf-tokenops-large-batch-control-plane/v1"
FORBIDDEN={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature",
"signatures","signed_transaction","raw_transaction","serialized_transaction","transaction_bytes",
"instruction_bytes","raw_instruction","secret","service_account_key"}

def sha256(v: Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def scan(v: Any, path="$")->None:
    if isinstance(v,dict):
        for k,x in v.items():
            n=str(k).lower().replace("-","_")
            if n in FORBIDDEN: raise ValueError(f"forbidden field {path}.{k}")
            scan(x,f"{path}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): scan(x,f"{path}[{i}]")

def _targets(policy: Dict[str,Any], treasury: Dict[str,Any])->None:
    scan(policy); scan(treasury)
    for label,v in (("policy",policy),("treasury",treasury)):
        if v.get("network")!=NETWORK or v.get("mint")!=MINT: raise ValueError(f"{label} target mismatch")
    e=policy.get("economics",{})
    if e.get("active_user_revenue_share")!=SHARE: raise ValueError("35% distribution policy drift")
    if e.get("approved_supply_floor_target_ui")!="8000000000": raise ValueError("8B floor drift")
    if treasury.get("control_model")!="external_multisig_required": raise ValueError("multisig control drift")

def audit_drift(audit: Dict[str,Any])->List[str]:
    scan(audit); out=[]
    if audit.get("network")!=NETWORK: out.append("network_drift")
    if audit.get("mint")!=MINT: out.append("mint_drift")
    if audit.get("program_id")!=PROGRAM: out.append("token_program_drift")
    if audit.get("decimals")!=DECIMALS: out.append("decimals_drift")
    if audit.get("mint_authority") is not None: out.append("mint_authority_reappeared")
    if audit.get("freeze_authority") is not None: out.append("freeze_authority_reappeared")
    try:
        if int(audit.get("supply_ui")) < SUPPLY_FLOOR_UI: out.append("supply_below_approved_floor")
    except Exception: out.append("invalid_supply")
    return sorted(set(out))

def build_control_plane(policy: Dict[str,Any], treasury: Dict[str,Any], audit: Dict[str,Any],
                        gross_revenue_raw: int=0, treasury_owned_burnable_raw: int|None=None)->Dict[str,Any]:
    _targets(policy,treasury); scan(audit)
    if gross_revenue_raw<0: raise ValueError("negative revenue")
    blockers=set(audit_drift(audit))
    dc=policy.get("distribution_controls",{})
    signer=policy.get("signer_policy",{})
    per_user=dc.get("per_user_cap")
    epoch_cap=dc.get("epoch_budget_cap")
    if per_user is None: blockers.add("per_user_cap_not_approved")
    if epoch_cap is None: blockers.add("epoch_budget_cap_not_approved")
    if dc.get("anti_sybil_required") is not True: blockers.add("anti_sybil_not_required")
    if dc.get("activity_evidence_required") is not True: blockers.add("activity_evidence_not_required")
    if signer.get("production_policy_status")!="approved": blockers.add("production_signer_policy_not_approved")

    theoretical_share_raw=(gross_revenue_raw*35)//100
    capped_budget_raw=None
    if epoch_cap is not None:
        capped_budget_raw=min(theoretical_share_raw,int(epoch_cap))

    supply_raw=int(audit.get("supply_raw","0"))
    floor_raw=SUPPLY_FLOOR_UI*(10**DECIMALS)
    theoretical_max_burn_raw=max(0,supply_raw-floor_raw)
    burn_plan_cap_raw=None if treasury_owned_burnable_raw is None else min(theoretical_max_burn_raw,max(0,int(treasury_owned_burnable_raw)))

    classes=treasury.get("approval_classes",{})
    required={k:int(v["minimum_approvals"]) for k,v in classes.items()
              if k in {"reward_epoch","vesting_settlement","burn","treasury_transfer"}}
    result={
      "schema":SCHEMA,"network":NETWORK,"mint":MINT,
      "policy_sha256":sha256(policy),"treasury_policy_sha256":sha256(treasury),"audit_sha256":sha256(audit),
      "read_only_observation":{"rpc_slot":audit.get("rpc_slot"),"supply_raw":supply_raw,
        "supply_ui":audit.get("supply_ui"),"holder_concentration_status":audit.get("largest_accounts_status"),
        "recent_signature_count":audit.get("recent_signature_count"),"drift":audit_drift(audit)},
      "active_user_distribution":{"share_bps":3500,"gross_revenue_raw":gross_revenue_raw,
        "theoretical_35_percent_budget_raw":theoretical_share_raw,"approved_epoch_budget_raw":capped_budget_raw,
        "per_user_cap":per_user,"epoch_budget_cap":epoch_cap,"allocation_authorized":False},
      "anti_whale":{"required":dc.get("anti_whale_cap_required") is True,"approved_per_user_cap":per_user,
        "enforcement_ready":per_user is not None and epoch_cap is not None},
      "vesting_locking":{"settlement_threshold":required.get("vesting_settlement"),
        "locking_policy_status":"planning_only_until_authoritative_terms_approved",
        "lock_rewards_status":"planning_only_until_authoritative_terms_approved","settlement_authorized":False},
      "burn":{"approved_supply_floor_ui":str(SUPPLY_FLOOR_UI),"theoretical_max_burn_raw":theoretical_max_burn_raw,
        "verified_treasury_owned_burnable_raw":treasury_owned_burnable_raw,"plan_cap_raw":burn_plan_cap_raw,
        "threshold":required.get("burn"),"execution_authorized":False},
      "treasury":{"transfer_threshold":required.get("treasury_transfer"),"migration_authorized":False,
        "transfer_authorized":False},
      "dao":{"decision_execution_authorized":False,"external_multisig_required":True,
        "governance_binding_status":"non_binding_planning_only"},
      "approval_thresholds":required,"blockers":sorted(blockers),
      "exact_remaining_signer_action":"none_until_fail_closed_blockers_are_resolved" if blockers
        else "user_controlled_approval_then_external_multisig_threshold_offline_before_any_signing",
      "execution":{"transaction_instructions_created":False,"transaction_bytes_created":False,
        "transaction_created":False,"transaction_signed":False,"transaction_submitted":False,
        "broadcast_allowed":False,"financial_effect":False,"private_key_used":False,
        "wave_mawja_untouched":True}
    }
    result["control_plane_sha256"]=sha256(result)
    return result
