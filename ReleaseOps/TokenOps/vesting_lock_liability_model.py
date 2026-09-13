#!/usr/bin/env python3
"""Deterministic non-binding THF vesting/locking and lock-reward liability model."""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict,List
MINT='HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv'; NETWORK='solana-mainnet-beta'; YEAR=365*86400
FORBIDDEN={'seed','seed_phrase','mnemonic','private_key','secret_key','keypair','signature','signed_transaction','raw_transaction','transaction_bytes','instruction_bytes'}
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def scan(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if str(k).lower().replace('-','_') in FORBIDDEN: raise ValueError('forbidden sensitive field')
            scan(x)
    elif isinstance(v,list):
        for x in v: scan(x)
def model(policy:Dict[str,Any], terms:Dict[str,Any], positions:List[Dict[str,Any]], as_of_unix:int)->Dict[str,Any]:
    scan(policy);scan(terms);scan(positions)
    if policy.get('network')!=NETWORK or policy.get('mint')!=MINT: raise ValueError('target mismatch')
    apr=int(terms.get('lock_reward_apr_bps',-1)); max_reward=int(terms.get('max_lock_reward_budget_raw',-1))
    if apr<0 or apr>10000 or max_reward<0: raise ValueError('invalid candidate reward terms')
    total_principal=0; total_unlocked=0; reward_liability=0; rows=[]
    for p in positions:
        pid=str(p.get('position_id','')).strip(); principal=int(p.get('principal_raw',0)); start=int(p.get('start_unix',0)); cliff=int(p.get('cliff_unix',start)); end=int(p.get('end_unix',0))
        if not pid or principal<=0 or not (0<=start<=cliff<=end): raise ValueError('invalid vesting position')
        if as_of_unix < cliff: unlocked=0
        elif end==start or as_of_unix>=end: unlocked=principal
        else: unlocked=principal*max(0,as_of_unix-start)//(end-start)
        elapsed=max(0,min(as_of_unix,end)-start); reward=principal*apr*elapsed//(10000*YEAR)
        total_principal+=principal;total_unlocked+=unlocked;reward_liability+=reward
        rows.append({'position_id':pid,'principal_raw':str(principal),'unlocked_raw':str(unlocked),'candidate_lock_reward_raw':str(reward)})
    reward_liability_capped=min(reward_liability,max_reward)
    blockers=['vesting_terms_not_authoritative','lock_reward_terms_not_authoritative']
    r={'schema':'thf-tokenops-vesting-lock-liability-model/v1','network':NETWORK,'mint':MINT,'policy_sha256':sha(policy),
       'terms':{'candidate_only':True,'lock_reward_apr_bps':apr,'max_lock_reward_budget_raw':str(max_reward)},'positions':sorted(rows,key=lambda x:x['position_id']),
       'liability':{'total_principal_raw':str(total_principal),'unlocked_principal_raw':str(total_unlocked),'uncapped_lock_reward_raw':str(reward_liability),'capped_lock_reward_raw':str(reward_liability_capped),'maximum_total_liability_raw':str(total_principal+reward_liability_capped)},
       'blockers':blockers,'settlement_authorized':False,'execution_authorized':False,'financial_effect':False,'wave_mawja_untouched':True}
    r['liability_model_sha256']=sha(r);return r
