#!/usr/bin/env python3
"""Validate sensitive TokenOps policy transitions against governance proposal evidence."""
from __future__ import annotations
import hashlib,json
SENSITIVE={'per_user_cap','epoch_budget_cap','distribution_reserve_account','claim_or_push_model'}

def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def get(policy,k): return (policy.get('distribution_controls') or {}).get(k)

def validate(old,new,proposals):
    changed={k:(get(old,k),get(new,k)) for k in SENSITIVE if get(old,k)!=get(new,k)}
    blockers=[]; matched={}
    for k,(before,after) in changed.items():
        matches=[p for p in proposals if p.get('parameter')==k and p.get('proposed_value')==after and p.get('proposal_complete') is True]
        if len(matches)!=1: blockers.append(f'{k}:requires_exactly_one_complete_governance_proposal')
        else: matched[k]=matches[0].get('proposal_sha256')
    if old.get('mint')!=new.get('mint') or old.get('network')!=new.get('network'): blockers.append('canonical_target_change_forbidden')
    oe=old.get('economics') or {}; ne=new.get('economics') or {}
    if oe.get('active_user_revenue_share')!=ne.get('active_user_revenue_share'): blockers.append('35_percent_share_change_requires_separate_constitutional_process')
    if oe.get('approved_supply_floor_target_ui')!=ne.get('approved_supply_floor_target_ui'): blockers.append('8b_floor_change_requires_separate_constitutional_process')
    out={'schema':'thf-tokenops-policy-transition-guard/v1','old_policy_sha256':sha(old),'new_policy_sha256':sha(new),
         'changed_sensitive_parameters':changed,'matched_proposal_sha256':matched,'blockers':sorted(blockers),
         'transition_review_pass':not blockers,'automatic_policy_write':False,'execution_authorized':False,
         'broadcast_allowed':False,'financial_effect':False}
    out['transition_guard_sha256']=sha(out); return out
