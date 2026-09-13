#!/usr/bin/env python3
"""Translate THF TokenOps fail-closed blockers into exact safe next actions."""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict

SCHEMA="thf-tokenops-blocker-action-map/v1"
ACTION_CATALOG={
 "per_user_cap_not_approved":{"owner":"governance","action":"approve an authoritative per-user reward cap","binding_financial_action":False},
 "epoch_budget_cap_not_approved":{"owner":"governance","action":"approve an authoritative reward-epoch budget cap","binding_financial_action":False},
 "reward_delivery_model_not_approved":{"owner":"treasury_governance","action":"approve claim, push, or hybrid reward delivery model","binding_financial_action":False},
 "production_signer_policy_not_approved":{"owner":"user_multisig_governance","action":"approve the production external signer/multisig policy; do not provide keys to CI","binding_financial_action":False},
 "missing_verified_evidence:treasury_ownership":{"owner":"treasury_controller","action":"publish hash-bound public treasury ownership evidence","binding_financial_action":False},
 "missing_verified_evidence:treasury_balance":{"owner":"observer","action":"capture a fresh read-only canonical-mint treasury balance receipt","binding_financial_action":False},
 "missing_verified_evidence:distribution_reserve":{"owner":"treasury_governance","action":"approve and evidence the reward distribution reserve","binding_financial_action":False},
 "missing_verified_evidence:vesting_terms":{"owner":"governance","action":"approve authoritative vesting and locking terms","binding_financial_action":False},
 "missing_verified_evidence:vesting_reserve":{"owner":"treasury_governance","action":"approve and evidence the vesting reserve","binding_financial_action":False},
 "missing_verified_evidence:burn_reserve":{"owner":"treasury_controller","action":"evidence treasury-owned burnable THF reserve without moving funds","binding_financial_action":False},
 "missing_verified_evidence:governance_authority":{"owner":"governance","action":"publish hash-bound policy-mutation/governance authority and threshold evidence","binding_financial_action":False},
 "missing_verified_evidence:destination_review":{"owner":"treasury_governance","action":"approve a public destination-review policy before any transfer planning","binding_financial_action":False},
}
def _sha(v:Any)->str:
 return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def compile_blocker_actions(graph:Dict[str,Any])->Dict[str,Any]:
 if graph.get("schema")!="thf-tokenops-execution-precondition-graph/v1": raise ValueError("unsupported graph")
 blockers=sorted(set(graph.get("global_blockers",[])+sum([v.get("blockers",[]) for v in graph.get("intents",{}).values()],[])))
 actions=[]
 for b in blockers:
  item=ACTION_CATALOG.get(b)
  if item is None:
   if b.startswith("missing_verified_evidence:"):
    key=b.split(":",1)[1]
    item={"owner":"evidence_owner","action":f"provide a verified hash-bound {key} receipt","binding_financial_action":False}
   elif "drift" in b or "authority_reappeared" in b or "supply_below" in b:
    item={"owner":"incident_response","action":"quarantine financial planning and independently re-run the read-only mainnet audit","binding_financial_action":False}
   else:
    item={"owner":"tokenops_governance","action":"resolve the named fail-closed blocker with authoritative evidence before signer handoff","binding_financial_action":False}
  actions.append({"blocker":b,**item})
 r={"schema":SCHEMA,"precondition_graph_sha256":graph.get("precondition_graph_sha256"),"actions":actions,
    "signer_action_now":"none_until_fail_closed_blockers_are_resolved" if blockers else "user_controlled_multisig_approval_still_required",
    "automatic_execution":False,"financial_effect":False,"wave_mawja_untouched":True}
 r["blocker_action_map_sha256"]=_sha(r)
 return r
