#!/usr/bin/env python3
"""Deterministic financial-evidence reconciliation for THF TokenOps.

Produces planning/readiness evidence only. It cannot create instructions, transaction bytes, signatures,
approvals, transfers, burns, vesting settlements, or DAO execution.
"""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict

MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"; NETWORK="solana-mainnet-beta"; DECIMALS=8
FLOOR_UI=8_000_000_000; FLOOR_RAW=FLOOR_UI*10**DECIMALS
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def reconcile(policy:Dict[str,Any], treasury_policy:Dict[str,Any], audit:Dict[str,Any],
              holder_receipt:Dict[str,Any], registry_receipt:Dict[str,Any],
              gross_epoch_revenue_raw:int=0)->Dict[str,Any]:
    for label,v in [("policy",policy),("treasury_policy",treasury_policy),("audit",audit)]:
        if v.get("network")!=NETWORK or v.get("mint")!=MINT: raise ValueError(f"{label} target mismatch")
    if gross_epoch_revenue_raw<0: raise ValueError("negative gross revenue")
    if policy.get("economics",{}).get("active_user_revenue_share")!=0.35: raise ValueError("35% policy drift")
    if policy.get("economics",{}).get("approved_supply_floor_target_ui")!="8000000000": raise ValueError("8B floor drift")
    if treasury_policy.get("control_model")!="external_multisig_required": raise ValueError("multisig policy drift")
    if holder_receipt.get("audit_sha256")!=sha(audit): raise ValueError("holder evidence detached from audit")
    if registry_receipt.get("network")!=NETWORK or registry_receipt.get("mint")!=MINT: raise ValueError("registry target mismatch")

    dc=policy.get("distribution_controls",{})
    blockers=[]
    per_user=dc.get("per_user_cap"); epoch_cap=dc.get("epoch_budget_cap")
    reserve=dc.get("distribution_reserve_account"); delivery=dc.get("distribution_delivery_model")
    if per_user is None: blockers.append("per_user_cap_not_approved")
    if epoch_cap is None: blockers.append("epoch_budget_cap_not_approved")
    if reserve is None: blockers.append("distribution_reserve_account_not_approved")
    if delivery is None: blockers.append("distribution_delivery_model_not_approved")
    if policy.get("signer_policy",{}).get("production_policy_status")!="approved": blockers.append("production_signer_policy_not_approved")
    if not registry_receipt.get("authoritative_inventory_ready"): blockers.append("authoritative_treasury_inventory_missing")
    if not holder_receipt.get("holder_concentration_available"): blockers.append("holder_concentration_observation_unavailable_nonbinding")

    theoretical_share=(gross_epoch_revenue_raw*35)//100
    actionable_budget=None; reserve_balance=None
    if registry_receipt.get("authoritative_inventory_ready") and reserve is not None:
        for row in registry_receipt.get("normalized_accounts",[]):
            if row["token_account_pubkey"]==reserve and "distribution_reserve" in row["roles"]:
                reserve_balance=row["observed_balance_raw"]; break
    if per_user is not None and epoch_cap is not None and reserve_balance is not None and delivery is not None:
        actionable_budget=min(theoretical_share,int(epoch_cap),reserve_balance)

    supply=int(audit.get("supply_raw","0")); headroom=max(0,supply-FLOOR_RAW); burnable_verified=None
    if registry_receipt.get("authoritative_inventory_ready"):
        burnable_verified=sum(r["observed_balance_raw"] for r in registry_receipt["normalized_accounts"] if "burn_reserve" in r["roles"])
    burn_review_cap=None if burnable_verified is None else min(headroom,burnable_verified)

    binding=[x for x in blockers if x!="holder_concentration_observation_unavailable_nonbinding"]
    thresholds={k:int(v["minimum_approvals"]) for k,v in treasury_policy.get("approval_classes",{}).items() if k in {"reward_epoch","vesting_settlement","burn","treasury_transfer"}}
    result={"schema":"thf-tokenops-financial-evidence-reconciliation/v1","network":NETWORK,"mint":MINT,
      "inputs":{"policy_sha256":sha(policy),"treasury_policy_sha256":sha(treasury_policy),"audit_sha256":sha(audit),
        "holder_evidence_sha256":holder_receipt.get("holder_evidence_sha256"),"treasury_registry_receipt_sha256":registry_receipt.get("registry_receipt_sha256")},
      "distribution":{"gross_epoch_revenue_raw":gross_epoch_revenue_raw,"share_bps":3500,"theoretical_35_percent_budget_raw":theoretical_share,
        "actionable_budget_raw":actionable_budget,"reserve_observed_balance_raw":reserve_balance,"per_user_cap":per_user,
        "epoch_budget_cap":epoch_cap,"delivery_model":delivery,"allocation_authorized":False},
      "burn":{"current_supply_raw":supply,"approved_floor_raw":FLOOR_RAW,"theoretical_headroom_raw":headroom,
        "verified_burn_reserve_raw":burnable_verified,"review_cap_raw":burn_review_cap,"execution_authorized":False},
      "holder_concentration":{"available":holder_receipt.get("holder_concentration_available"),"top1_percent":holder_receipt.get("top1_percent"),
        "top5_percent":holder_receipt.get("top5_percent"),"top10_percent":holder_receipt.get("top10_percent"),"policy_binding":False},
      "approval_thresholds":thresholds,"blockers":sorted(blockers),"binding_blockers":sorted(binding),
      "readiness":"READY_FOR_OFFLINE_APPROVAL_REVIEW" if not binding else "FAIL_CLOSED",
      "exact_remaining_signer_action":"none_until_fail_closed_blockers_are_resolved" if binding else "user_controlled_approval_then_external_multisig_threshold_offline_before_any_signing",
      "transaction_instructions_created":False,"transaction_bytes_created":False,"transaction_signed":False,"transaction_submitted":False,
      "broadcast_allowed":False,"financial_effect":False,"private_key_used":False,"wave_mawja_untouched":True}
    result["reconciliation_sha256"]=sha(result);return result
