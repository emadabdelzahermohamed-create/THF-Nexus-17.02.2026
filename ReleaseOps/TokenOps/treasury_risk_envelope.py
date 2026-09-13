#!/usr/bin/env python3
"""Non-binding THF treasury/distribution/burn planning risk envelope."""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict
MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"; NETWORK="solana-mainnet-beta"; DECIMALS=8
FLOOR_RAW=8_000_000_000*10**DECIMALS

def dig(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def build_risk_envelope(policy:Dict[str,Any], treasury:Dict[str,Any], audit:Dict[str,Any], epoch_revenue_raw:int|None=None, treasury_evidence:Dict[str,Any]|None=None)->Dict[str,Any]:
    if policy.get("mint")!=MINT or treasury.get("mint")!=MINT or audit.get("mint")!=MINT: raise ValueError("mint mismatch")
    if policy.get("network")!=NETWORK or treasury.get("network")!=NETWORK or audit.get("network")!=NETWORK: raise ValueError("network mismatch")
    if policy.get("economics",{}).get("active_user_revenue_share")!=0.35: raise ValueError("share drift")
    supply_raw=int(audit["supply_raw"]); theoretical_burn=max(0,supply_raw-FLOOR_RAW)
    verified_balance=None
    if treasury_evidence and treasury_evidence.get("status")=="verified" and treasury_evidence.get("mint")==MINT and treasury_evidence.get("network")==NETWORK:
        x=treasury_evidence.get("verified_treasury_owned_balance_raw")
        if isinstance(x,int) and x>=0: verified_balance=x
    review_burn_cap=None if verified_balance is None else min(theoretical_burn,verified_balance)
    dc=policy.get("distribution_controls",{})
    share_budget=None if epoch_revenue_raw is None else max(0,int(epoch_revenue_raw))*35//100
    approved_epoch=dc.get("epoch_budget_cap")
    review_epoch_budget=None if share_budget is None or approved_epoch is None else min(share_budget,int(approved_epoch))
    thresholds={k:int(v["minimum_approvals"]) for k,v in treasury.get("approval_classes",{}).items() if k in ("reward_epoch","vesting_settlement","burn","treasury_transfer")}
    r={"schema":"thf-tokenops-treasury-risk-envelope/v1","network":NETWORK,"mint":MINT,
       "evidence":{"policy_sha256":dig(policy),"treasury_policy_sha256":dig(treasury),"audit_sha256":dig(audit)},
       "supply":{"current_raw":supply_raw,"current_ui":audit.get("supply_ui"),"approved_floor_raw":FLOOR_RAW,"approved_floor_ui":"8000000000","theoretical_max_burn_raw":theoretical_burn},
       "burn":{"verified_treasury_owned_balance_raw":verified_balance,"review_burn_cap_raw":review_burn_cap,"actionable_burn_amount_raw":None,"minimum_approvals":thresholds.get("burn")},
       "distribution":{"share_bps":3500,"epoch_revenue_raw":epoch_revenue_raw,"theoretical_35pct_budget_raw":share_budget,"approved_epoch_budget_cap":approved_epoch,"review_epoch_budget_raw":review_epoch_budget,"approved_per_user_cap":dc.get("per_user_cap"),"actionable_allocation_budget_raw":None,"minimum_approvals":thresholds.get("reward_epoch")},
       "vesting_locking":{"vesting_minimum_approvals":thresholds.get("vesting_settlement"),"settlement_amount_raw":None,"lock_reward_settlement_amount_raw":None},
       "treasury_transfer":{"minimum_approvals":thresholds.get("treasury_transfer"),"actionable_amount_raw":None},
       "execution_authorized":False,"broadcast_allowed":False,"financial_effect":False,"wave_mawja_untouched":True}
    r["risk_envelope_sha256"]=dig(r); return r
