#!/usr/bin/env python3
"""Fail-closed proposal schema for TokenOps economic parameters. No proposal is self-executing."""
from __future__ import annotations
import hashlib,json
MINT='HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv'; NETWORK='solana-mainnet-beta'
ALLOWED={'per_user_cap','epoch_budget_cap','distribution_reserve_account','vesting_terms_hash','lock_reward_terms_hash','claim_or_push_model'}
FORBIDDEN={'seed','seed_phrase','mnemonic','private_key','secret_key','keypair','signature','signed_transaction','transaction_bytes','instruction_bytes'}

def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def scan(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if str(k).lower().replace('-','_') in FORBIDDEN: raise ValueError('forbidden sensitive/execution field')
            scan(x)
    elif isinstance(v,list):
        for x in v: scan(x)

def build(parameter,value,governance_decision_hash=None,policy_source_hash=None,effective_epoch=None):
    if parameter not in ALLOWED: raise ValueError('unsupported parameter')
    scan(value)
    blockers=[]
    if value is None: blockers.append('parameter_value_not_selected')
    if not governance_decision_hash: blockers.append('governance_decision_hash_missing')
    if not policy_source_hash: blockers.append('policy_source_hash_missing')
    if effective_epoch is None: blockers.append('effective_epoch_missing')
    out={'schema':'thf-tokenops-governance-parameter-proposal/v1','network':NETWORK,'mint':MINT,
         'parameter':parameter,'proposed_value':value,'governance_decision_hash':governance_decision_hash,
         'policy_source_hash':policy_source_hash,'effective_epoch':effective_epoch,'blockers':sorted(blockers),
         'proposal_complete':not blockers,'policy_mutation_authorized':False,'execution_authorized':False,
         'transaction_created':False,'transaction_signed':False,'transaction_submitted':False,
         'broadcast_allowed':False,'financial_effect':False,'required_next_action':
         'record_authoritative_governance_decision_and_update_policy_in_separate_reviewed_commit' if not blockers else
         'resolve_proposal_blockers_without_signing_or_broadcast'}
    out['proposal_sha256']=sha(out); return out
