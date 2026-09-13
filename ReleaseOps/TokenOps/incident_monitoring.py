#!/usr/bin/env python3
"""Read-only TokenOps monitoring and incident/rollback decision evidence."""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict,List
MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"; NETWORK="solana-mainnet-beta"
PROGRAM="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"; DECIMALS=8
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def build_monitoring_receipt(audit:Dict[str,Any], policy_sha256:str, treasury_policy_sha256:str)->Dict[str,Any]:
    alerts=[]
    checks={
      "network":audit.get("network")==NETWORK,"mint":audit.get("mint")==MINT,
      "program":audit.get("program_id")==PROGRAM,"decimals":audit.get("decimals")==DECIMALS,
      "mint_authority_absent":audit.get("mint_authority") is None,
      "freeze_authority_absent":audit.get("freeze_authority") is None,
      "supply_at_or_above_8b":int(audit.get("supply_raw","0"))>=8_000_000_000*(10**DECIMALS)}
    alerts += [f"critical:{k}" for k,v in checks.items() if not v]
    if audit.get("largest_accounts_status")!="ok": alerts.append("degraded:holder_concentration_unavailable")
    if audit.get("recent_signatures_status")!="ok": alerts.append("degraded:recent_signature_query_unavailable")
    severity="critical" if any(x.startswith("critical:") for x in alerts) else ("degraded" if alerts else "healthy")
    action="freeze_all_tokenops_planning_and_require_human_review" if severity=="critical" else \
      ("preserve_core_audit_continue_safe_independent_tasks" if severity=="degraded" else "continue_read_only_monitoring")
    rollback={"scope":"control_plane/config_only","on_chain_rollback_possible":False,
      "reason":"no irreversible on-chain action is performed by this control plane",
      "safe_recovery":["pin_last_verified_policy_hash","pin_last_verified_audit_hash","disable_plan_admission",
        "re-run_read_only_audit","require_user_and_multisig_reapproval_after_incident"],
      "automatic_on_chain_action":False}
    r={"schema":"thf-tokenops-monitoring-incident-receipt/v1","network":NETWORK,"mint":MINT,
       "audit_sha256":sha(audit),"policy_sha256":policy_sha256,"treasury_policy_sha256":treasury_policy_sha256,
       "checks":checks,"alerts":alerts,"severity":severity,"recommended_control_plane_action":action,
       "rollback":rollback,"execution_authorized":False,"broadcast_allowed":False,"financial_effect":False,
       "wave_mawja_untouched":True}
    r["monitoring_receipt_sha256"]=sha(r);return r
