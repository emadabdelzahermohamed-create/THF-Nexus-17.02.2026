#!/usr/bin/env python3
"""Read-only/candidate THF treasury solvency stress model. Never transfers or burns."""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict
MINT='HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv';NETWORK='solana-mainnet-beta';DEC=8;FLOOR=8_000_000_000*10**DEC
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def stress(policy:Dict[str,Any], registry:Dict[str,Any], audit:Dict[str,Any], liabilities:Dict[str,int])->Dict[str,Any]:
    if any(x.get('network')!=NETWORK or x.get('mint')!=MINT for x in (policy,registry,audit)): raise ValueError('target mismatch')
    if policy.get('economics',{}).get('active_user_revenue_share')!=0.35: raise ValueError('35% policy drift')
    verified=registry.get('status')=='authoritatively_configured' and bool(registry.get('accounts'))
    balances=0
    if verified:
        for a in registry['accounts']:
            if a.get('balance_verified') is not True or not a.get('ownership_evidence_sha256'): verified=False;break
            balances+=int(a.get('observed_balance_raw',0))
    reward=max(0,int(liabilities.get('reward_raw',0)));vesting=max(0,int(liabilities.get('vesting_raw',0)));reserve=max(0,int(liabilities.get('operating_reserve_raw',0)))
    encumbered=reward+vesting+reserve; free=max(0,balances-encumbered) if verified else 0
    supply=int(audit.get('supply_raw','0')); headroom=max(0,supply-FLOOR)
    burn_review_cap=min(free,headroom) if verified else None
    blockers=[]
    if not verified: blockers.append('authoritative_treasury_inventory_ownership_balance_evidence_incomplete')
    if policy.get('distribution_controls',{}).get('epoch_budget_cap') is None: blockers.append('epoch_budget_cap_not_approved')
    r={'schema':'thf-tokenops-treasury-solvency-stress/v1','network':NETWORK,'mint':MINT,'policy_sha256':sha(policy),'registry_sha256':sha(registry),'audit_sha256':sha(audit),
       'treasury_verified':verified,'observed_treasury_balance_raw':str(balances) if verified else None,
       'liabilities':{'reward_raw':str(reward),'vesting_raw':str(vesting),'operating_reserve_raw':str(reserve),'encumbered_raw':str(encumbered)},
       'free_unencumbered_raw':str(free) if verified else None,'theoretical_supply_burn_headroom_raw':str(headroom),'review_burn_cap_raw':None if burn_review_cap is None else str(burn_review_cap),
       'solvent_against_modeled_liabilities':(balances>=encumbered) if verified else None,'blockers':sorted(set(blockers)),
       'burn_authorized':False,'transfer_authorized':False,'execution_authorized':False,'financial_effect':False,'wave_mawja_untouched':True}
    r['stress_sha256']=sha(r);return r
