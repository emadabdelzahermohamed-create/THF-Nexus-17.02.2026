#!/usr/bin/env python3
"""Hash-only governance decision packet for unresolved THF TokenOps policy blockers."""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict
MINT='HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv';NETWORK='solana-mainnet-beta'
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def build(policy:Dict[str,Any], treasury:Dict[str,Any], scenario_packet:Dict[str,Any])->Dict[str,Any]:
    if policy.get('mint')!=MINT or treasury.get('mint')!=MINT or scenario_packet.get('mint')!=MINT: raise ValueError('mint mismatch')
    dc=policy.get('distribution_controls',{}); signer=policy.get('signer_policy',{})
    decisions=[
      {'id':'distribution.per_user_cap','current':dc.get('per_user_cap'),'status':'decision_required'},
      {'id':'distribution.epoch_budget_cap','current':dc.get('epoch_budget_cap'),'status':'decision_required'},
      {'id':'distribution.claim_or_push_model','current':dc.get('claim_or_push_model'),'status':'decision_required'},
      {'id':'distribution.reserve','current':None,'status':'authoritative_evidence_required'},
      {'id':'treasury.inventory_ownership_balances','current':None,'status':'public_read_only_evidence_required'},
      {'id':'signer.production_policy','current':signer.get('production_policy_status'),'status':'decision_required'},
      {'id':'vesting.locking_terms','current':None,'status':'decision_required'},
      {'id':'rewards.lock_reward_terms','current':None,'status':'decision_required'}]
    r={'schema':'thf-tokenops-governance-decision-packet/v1','network':NETWORK,'mint':MINT,'policy_sha256':sha(policy),'treasury_policy_sha256':sha(treasury),'scenario_packet_sha256':scenario_packet.get('scenario_packet_sha256'),
       'constitutional_constraints':{'active_user_revenue_share':'35%','supply_floor_target_ui':'8000000000','minting':'forbidden','authority_change':'forbidden'},
       'decisions':decisions,'policy_governance_threshold_status':'not_authoritatively_defined_in_current_treasury_policy',
       'note':'This packet requests decisions/evidence only. It does not infer a governance threshold for policy changes and cannot approve itself.',
       'approval_satisfied':False,'policy_mutated':False,'execution_authorized':False,'financial_effect':False,'wave_mawja_untouched':True}
    r['decision_packet_sha256']=sha(r);return r
