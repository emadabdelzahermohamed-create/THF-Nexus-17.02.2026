#!/usr/bin/env python3
"""THF TokenOps evidence-DAG financial control batch.

Planning/evidence only. This module deliberately cannot create Solana transaction
or instruction bytes and cannot accept key/signature material.
"""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict, Iterable, List

MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK="solana-mainnet-beta"
PROGRAM="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
DECIMALS=8
SUPPLY_FLOOR_RAW=8_000_000_000 * 10**DECIMALS
SCHEMA="thf-tokenops-evidence-dag-financial-control/v1"
FORBIDDEN_KEYS={
 "seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature","signatures",
 "transaction_bytes","raw_transaction","serialized_transaction","signed_transaction",
 "instruction_bytes","raw_instruction","service_account_key","secret"
}
ALLOWED_CLASSES={"reward_epoch","vesting_settlement","burn","treasury_transfer"}

def canonical_bytes(value:Any)->bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()

def sha256(value:Any)->str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()

def scan_no_secrets(value:Any,path:str="$")->None:
    if isinstance(value,dict):
        for k,v in value.items():
            key=str(k).lower().replace("-","_")
            if key in FORBIDDEN_KEYS:
                raise ValueError(f"forbidden field {path}.{k}")
            scan_no_secrets(v,f"{path}.{k}")
    elif isinstance(value,list):
        for i,v in enumerate(value): scan_no_secrets(v,f"{path}[{i}]")

def validate_authority(policy:Dict[str,Any], treasury:Dict[str,Any])->None:
    scan_no_secrets(policy); scan_no_secrets(treasury)
    for label,obj in (("policy",policy),("treasury",treasury)):
        if obj.get("network")!=NETWORK or obj.get("mint")!=MINT:
            raise ValueError(f"{label} target mismatch")
    eco=policy.get("economics",{})
    if eco.get("active_user_revenue_share")!=0.35:
        raise ValueError("35 percent policy drift")
    if eco.get("approved_supply_floor_target_ui")!="8000000000":
        raise ValueError("8B floor drift")
    if treasury.get("control_model")!="external_multisig_required":
        raise ValueError("external multisig requirement drift")

def audit_quarantine_reasons(audit:Dict[str,Any])->List[str]:
    scan_no_secrets(audit)
    reasons=[]
    checks=[
      ("network_drift",audit.get("network")==NETWORK),
      ("mint_drift",audit.get("mint")==MINT),
      ("program_drift",audit.get("program_id")==PROGRAM),
      ("decimals_drift",audit.get("decimals")==DECIMALS),
      ("mint_authority_reappeared",audit.get("mint_authority") is None),
      ("freeze_authority_reappeared",audit.get("freeze_authority") is None),
    ]
    reasons += [name for name,ok in checks if not ok]
    try:
        if int(audit.get("supply_raw","0")) < SUPPLY_FLOOR_RAW:
            reasons.append("supply_below_8b_floor")
    except Exception:
        reasons.append("invalid_supply")
    return sorted(set(reasons))

def build_evidence_dag(policy:Dict[str,Any], treasury:Dict[str,Any], audit:Dict[str,Any], evidence:Dict[str,Any])->Dict[str,Any]:
    """Bind public/hash-only evidence. Missing nodes remain explicit blockers."""
    validate_authority(policy,treasury); scan_no_secrets(audit); scan_no_secrets(evidence)
    required_nodes=[
      "treasury_registry","treasury_balance_attestation","distribution_reserve",
      "allocation_accounting","vesting_liability","burn_reserve","simulation_receipt",
      "governance_charter","vault_contract","forge_contract","core_contract"
    ]
    nodes={}; blockers=[]
    for name in required_nodes:
        obj=evidence.get(name)
        if obj is None:
            nodes[name]={"present":False,"sha256":None}; blockers.append(f"missing_evidence:{name}")
        else:
            nodes[name]={"present":True,"sha256":sha256(obj)}
    quarantine=audit_quarantine_reasons(audit)
    blockers.extend(f"quarantine:{x}" for x in quarantine)
    out={"schema":SCHEMA,"network":NETWORK,"mint":MINT,
      "policy_sha256":sha256(policy),"treasury_policy_sha256":sha256(treasury),"audit_sha256":sha256(audit),
      "nodes":nodes,"quarantined":bool(quarantine),"quarantine_reasons":quarantine,
      "blockers":sorted(set(blockers)),"review_ready":False,"execution_authorized":False,
      "broadcast_allowed":False,"financial_effect":False}
    out["dag_sha256"]=sha256(out); return out

def build_double_entry_preview(action_class:str, amount_raw:int, source_ref_hash:str, destination_ref_hash:str)->Dict[str,Any]:
    """Planning-only journal preview with deterministic debit/credit conservation."""
    if action_class not in ALLOWED_CLASSES: raise ValueError("unsupported action class")
    if not isinstance(amount_raw,int) or amount_raw<0: raise ValueError("amount_raw must be nonnegative int")
    for name,h in (("source",source_ref_hash),("destination",destination_ref_hash)):
        if not isinstance(h,str) or len(h)!=64 or any(c not in "0123456789abcdef" for c in h):
            raise ValueError(f"{name} ref must be lowercase sha256")
    debit={"account_ref_hash":source_ref_hash,"direction":"debit","amount_raw":amount_raw}
    credit={"account_ref_hash":destination_ref_hash,"direction":"credit","amount_raw":amount_raw}
    out={"schema":"thf-tokenops-double-entry-preview/v1","action_class":action_class,"entries":[debit,credit],
         "debits_raw":amount_raw,"credits_raw":amount_raw,"balanced":True,"posting_authorized":False,"financial_effect":False}
    out["journal_preview_sha256"]=sha256(out); return out

def build_intent_lifecycle(action_class:str, dag:Dict[str,Any], journal:Dict[str,Any], treasury:Dict[str,Any])->Dict[str,Any]:
    """Fail-closed lifecycle. It never consumes approvals or signatures."""
    scan_no_secrets(dag);scan_no_secrets(journal);scan_no_secrets(treasury)
    if action_class not in ALLOWED_CLASSES: raise ValueError("unsupported action class")
    cls=treasury.get("approval_classes",{}).get(action_class)
    if not cls: raise ValueError("approval class absent from treasury policy")
    threshold=int(cls.get("minimum_approvals",0)); blockers=list(dag.get("blockers",[]))
    if dag.get("quarantined"): blockers.append("evidence_dag_quarantined")
    if not journal.get("balanced"): blockers.append("journal_unbalanced")
    if threshold<1: blockers.append("invalid_multisig_threshold")
    out={"schema":"thf-tokenops-intent-lifecycle/v1","network":NETWORK,"mint":MINT,"action_class":action_class,
         "evidence_dag_sha256":dag.get("dag_sha256"),"journal_preview_sha256":journal.get("journal_preview_sha256"),
         "minimum_external_multisig_approvals":threshold,"state":"blocked" if blockers else "review_packet_ready_nonbinding",
         "blockers":sorted(set(blockers)),"simulation_allowed":not blockers,"approval_collection_allowed":False,
         "signing_allowed":False,"broadcast_allowed":False,"execution_authorized":False,
         "transaction_bytes_created":False,"instruction_bytes_created":False,"financial_effect":False,
         "exact_remaining_signer_action":"none_until_fail_closed_blockers_are_resolved" if blockers else "user_controlled_review_then_external_multisig_process_outside_ci"}
    out["intent_lifecycle_sha256"]=sha256(out); return out

def build_incident_quarantine(audit:Dict[str,Any], active_intent_hashes:Iterable[str])->Dict[str,Any]:
    """Quarantine all planning intents when canonical on-chain invariants drift."""
    reasons=audit_quarantine_reasons(audit); intents=list(active_intent_hashes)
    for h in intents:
        if not isinstance(h,str) or len(h)!=64: raise ValueError("intent hash malformed")
    out={"schema":"thf-tokenops-incident-quarantine/v1","network":NETWORK,"mint":MINT,"triggered":bool(reasons),
         "reasons":reasons,"intent_hashes":sorted(intents) if reasons else [],
         "control_plane_action":"freeze_plan_admission_require_human_review" if reasons else "continue_read_only_monitoring",
         "automatic_on_chain_action":False,"rollback_scope":"config_and_planning_only","signing_allowed":False,
         "broadcast_allowed":False,"financial_effect":False}
    out["quarantine_receipt_sha256"]=sha256(out); return out

def build_integration_conformance(contracts:Dict[str,Any])->Dict[str,Any]:
    """Conformance matrix for public/hash-only Vault/Forge/Core contracts."""
    scan_no_secrets(contracts); results={}; blockers=[]
    for name in ("Vault","Forge","Core"):
        c=contracts.get(name)
        if not isinstance(c,dict):
            results[name]={"present":False,"conformant":False};blockers.append(f"missing_contract:{name}");continue
        forbidden=set(c.get("forbidden",[]))
        safe=(c.get("binding_financial_action") is False and {"private_keys","signatures","broadcast"}.issubset(forbidden))
        results[name]={"present":True,"conformant":safe,"sha256":sha256(c)}
        if not safe: blockers.append(f"nonconformant_contract:{name}")
    out={"schema":"thf-tokenops-integration-conformance/v1","network":NETWORK,"mint":MINT,"results":results,
         "blockers":sorted(blockers),"conformant":not blockers,"key_material_allowed":False,"signatures_allowed":False,
         "broadcast_allowed":False,"financial_effect":False}
    out["conformance_sha256"]=sha256(out); return out

def compile_batch(policy:Dict[str,Any],treasury:Dict[str,Any],audit:Dict[str,Any],evidence:Dict[str,Any],contracts:Dict[str,Any],action_class:str="reward_epoch",amount_raw:int=0)->Dict[str,Any]:
    validate_authority(policy,treasury)
    dag=build_evidence_dag(policy,treasury,audit,evidence)
    journal=build_double_entry_preview(action_class,amount_raw,"0"*64,"1"*64)
    lifecycle=build_intent_lifecycle(action_class,dag,journal,treasury)
    quarantine=build_incident_quarantine(audit,[lifecycle["intent_lifecycle_sha256"]])
    conformance=build_integration_conformance(contracts)
    blockers=sorted(set(lifecycle["blockers"]+conformance["blockers"]))
    out={"schema":"thf-tokenops-large-batch-compiled/v1","network":NETWORK,"mint":MINT,"evidence_dag":dag,
         "journal_preview":journal,"intent_lifecycle":lifecycle,"incident_quarantine":quarantine,
         "integration_conformance":conformance,"blockers":blockers,
         "readiness":"FAIL_CLOSED" if blockers else "NONBINDING_REVIEW_READY","execution_authorized":False,
         "transaction_created":False,"transaction_signed":False,"transaction_submitted":False,"broadcast_allowed":False,
         "financial_effect":False,"private_key_used":False,"persistent_service_account_key_used":False,"wave_mawja_untouched":True}
    out["compiled_batch_sha256"]=sha256(out); return out
