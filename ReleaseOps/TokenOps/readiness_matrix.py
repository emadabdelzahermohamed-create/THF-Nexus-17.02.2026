#!/usr/bin/env python3
"""Consolidated THF TokenOps readiness matrix; truthfully separates planning from execution readiness."""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def build_matrix(control:Dict[str,Any], allocation:Dict[str,Any], inventory:Dict[str,Any],
                 monitoring:Dict[str,Any], integrations:Dict[str,Any])->Dict[str,Any]:
    sources={"control_plane":control.get("control_plane_sha256"),"allocation":allocation.get("simulation_sha256"),
      "inventory":inventory.get("receipt_sha256"),"monitoring":monitoring.get("monitoring_receipt_sha256"),
      "integrations":integrations.get("integration_contracts_sha256")}
    if any(not isinstance(x,str) or len(x)!=64 for x in sources.values()): raise ValueError("missing source hash")
    domains={
      "mainnet_read_only":{"ready":monitoring.get("severity")!="critical","status":monitoring.get("severity")},
      "active_user_distribution":{"ready":allocation.get("simulation_ready") is True,
          "blockers":allocation.get("blockers",[])},
      "anti_whale":{"ready":control.get("anti_whale",{}).get("enforcement_ready") is True,
          "blockers":[x for x in control.get("blockers",[]) if "cap" in x or "budget" in x]},
      "treasury_inventory":{"ready":inventory.get("inventory_ready") is True,"blockers":inventory.get("blockers",[])},
      "vesting_locking":{"ready":False,"status":control.get("vesting_locking",{}).get("locking_policy_status")},
      "burn_planning":{"ready":control.get("burn",{}).get("verified_treasury_owned_burnable_raw") is not None,
          "status":"planning_only"},
      "dao_multisig":{"ready":False,"status":"external_multisig_required_user_approval_required"},
      "vault_forge_core":{"ready":True,"status":"hash_only_non_custodial_contracts_defined"},
      "execution":{"ready":False,"status":"fail_closed_no_signing_or_broadcast"}}
    blockers=sorted(set(sum([v.get("blockers",[]) for v in domains.values() if isinstance(v,dict)],[])))
    r={"schema":"thf-tokenops-readiness-matrix/v1","source_hashes":sources,"domains":domains,
       "unresolved_blockers":blockers,"financial_execution_ready":False,"broadcast_allowed":False,
       "binding_dao_action_ready":False,"truthful_readiness":"control_plane_planning_hardened_execution_not_approved",
       "wave_mawja_untouched":True}
    r["readiness_sha256"]=sha(r);return r
