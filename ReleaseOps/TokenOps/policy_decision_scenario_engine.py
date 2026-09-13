#!/usr/bin/env python3
"""Non-binding THF TokenOps policy scenario engine. No policy mutation or financial action."""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict, List
MINT='HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv'; NETWORK='solana-mainnet-beta'; DEN=10000
FORBIDDEN={'seed','seed_phrase','mnemonic','private_key','secret_key','keypair','signature','signed_transaction','raw_transaction','transaction_bytes','instruction_bytes'}
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def scan(v,p='$'):
    if isinstance(v,dict):
        for k,x in v.items():
            if str(k).lower().replace('-','_') in FORBIDDEN: raise ValueError(f'forbidden field {p}.{k}')
            scan(x,f'{p}.{k}')
    elif isinstance(v,list):
        for i,x in enumerate(v): scan(x,f'{p}[{i}]')
def build(policy:Dict[str,Any], scenarios:List[Dict[str,Any]])->Dict[str,Any]:
    scan(policy); scan(scenarios)
    if policy.get('network')!=NETWORK or policy.get('mint')!=MINT: raise ValueError('target mismatch')
    eco=policy.get('economics',{}); dc=policy.get('distribution_controls',{})
    if eco.get('active_user_revenue_share')!=0.35 or str(eco.get('approved_supply_floor_target_ui'))!='8000000000': raise ValueError('constitutional economics drift')
    rows=[]
    for s in scenarios:
        name=str(s.get('name','')).strip()
        epoch=int(s.get('epoch_budget_cap_raw',0)); user=int(s.get('per_user_cap_raw',0)); model=str(s.get('claim_or_push_model',''))
        if not name or epoch<=0 or user<=0 or user>epoch: raise ValueError('invalid scenario caps')
        if model not in {'claim','push','hybrid'}: raise ValueError('invalid delivery model')
        min_recipients=(epoch+user-1)//user
        rows.append({'name':name,'epoch_budget_cap_raw':str(epoch),'per_user_cap_raw':str(user),'claim_or_push_model':model,
          'per_user_share_of_epoch_bps':user*DEN//epoch,'minimum_recipients_to_fully_allocate_at_cap':min_recipients,
          'authoritative':False,'recommended':False})
    rows.sort(key=lambda x:x['name'])
    blockers=[]
    if dc.get('per_user_cap') is None: blockers.append('per_user_cap_not_approved')
    if dc.get('epoch_budget_cap') is None: blockers.append('epoch_budget_cap_not_approved')
    if dc.get('claim_or_push_model') not in {'claim','push','hybrid'}: blockers.append('delivery_model_not_approved')
    r={'schema':'thf-tokenops-policy-decision-scenarios/v1','network':NETWORK,'mint':MINT,'policy_sha256':sha(policy),
       'constitutional_economics':{'active_user_share_bps':3500,'supply_floor_ui':'8000000000'},'scenarios':rows,
       'current_blockers':blockers,'policy_mutated':False,'execution_authorized':False,'financial_effect':False,'wave_mawja_untouched':True}
    r['scenario_packet_sha256']=sha(r); return r
