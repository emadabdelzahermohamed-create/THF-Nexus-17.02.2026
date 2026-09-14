#!/usr/bin/env python3
"""THF TokenOps financial control-plane helpers.

Pure planning/evidence functions only. This module does not construct Solana
instructions, transactions, signatures, or broadcast payloads.
"""
from __future__ import annotations
import hashlib, json, re
from typing import Any, Dict, Iterable, List, Optional

MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK="solana-mainnet-beta"
TOKEN_PROGRAM="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
DECIMALS=8
SHARE_BPS=3500
SUPPLY_FLOOR_RAW=8_000_000_000 * 10**DECIMALS
SUPPLY_CEILING_RAW=10_000_000_000 * 10**DECIMALS
BASE58="123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
FORBIDDEN={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature","signatures","signed_transaction","raw_transaction","serialized_transaction","transaction_bytes","instruction_bytes","access_token","refresh_token","service_account_key"}

def canonical_json(v:Any)->bytes:
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
def sha256(v:Any)->str:
    return hashlib.sha256(v if isinstance(v,bytes) else (v.encode() if isinstance(v,str) else canonical_json(v))).hexdigest()
def scan_sensitive(v:Any,path="$")->None:
    if isinstance(v,dict):
        for k,x in v.items():
            n=str(k).lower().replace("-","_")
            if n in FORBIDDEN: raise ValueError(f"forbidden sensitive field at {path}.{k}")
            scan_sensitive(x,f"{path}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): scan_sensitive(x,f"{path}[{i}]")

def _b58decode(s:str)->bytes:
    n=0
    for c in s:
        if c not in BASE58: raise ValueError("invalid base58 character")
        n=n*58+BASE58.index(c)
    b=n.to_bytes((n.bit_length()+7)//8,"big") if n else b""
    pad=len(s)-len(s.lstrip("1"))
    return b"\x00"*pad+b
def valid_pubkey(s:Any)->bool:
    try: return isinstance(s,str) and len(_b58decode(s))==32
    except Exception: return False

def validate_identity(policy:Dict[str,Any])->Dict[str,Any]:
    checks={"network":policy.get("network")==NETWORK,"mint":policy.get("mint")==MINT,"token_program":policy.get("token_program")==TOKEN_PROGRAM,"decimals":int(policy.get("decimals",-1))==DECIMALS}
    failed=sorted(k for k,v in checks.items() if not v)
    return {"status":"PASS" if not failed else "FAIL_CLOSED","failed":failed,"identity_sha256":sha256({"network":NETWORK,"mint":MINT,"token_program":TOKEN_PROGRAM,"decimals":DECIMALS})}

def validate_treasury_registry(reg:Dict[str,Any], observed_slot:Optional[int]=None, max_slot_lag:int=5000)->Dict[str,Any]:
    scan_sensitive(reg); errors=[]
    if reg.get("network")!=NETWORK: errors.append("network_mismatch")
    if reg.get("mint")!=MINT: errors.append("mint_mismatch")
    accounts=reg.get("accounts") or []; seen=set(); roles={}; total=0
    allowed_roles={"distribution_reserve","burn_reserve","vesting_reserve","dao_treasury","operations","lock_reward_reserve"}
    for i,a in enumerate(accounts):
        p=f"accounts[{i}]"
        if not valid_pubkey(a.get("token_account")): errors.append(f"{p}:invalid_token_account")
        if not valid_pubkey(a.get("owner")): errors.append(f"{p}:invalid_owner")
        ta=a.get("token_account")
        if ta in seen: errors.append(f"{p}:duplicate_token_account")
        seen.add(ta)
        if a.get("mint")!=MINT: errors.append(f"{p}:mint_mismatch")
        if a.get("token_program")!=TOKEN_PROGRAM: errors.append(f"{p}:token_program_mismatch")
        if a.get("decimals")!=DECIMALS: errors.append(f"{p}:decimals_mismatch")
        if a.get("state")!="initialized": errors.append(f"{p}:account_not_initialized")
        role=a.get("role")
        if role not in allowed_roles: errors.append(f"{p}:unsupported_role")
        bal=a.get("observed_balance_raw")
        if not isinstance(bal,int) or bal<0: errors.append(f"{p}:invalid_balance")
        else:
            total += bal
            if role in allowed_roles: roles[role]=roles.get(role,0)+bal
        slot=a.get("observed_slot")
        if not isinstance(slot,int) or slot<=0: errors.append(f"{p}:invalid_slot")
        elif observed_slot is not None and (slot>observed_slot or observed_slot-slot>max_slot_lag): errors.append(f"{p}:stale_or_future_slot")
        for fld in ("ownership_evidence_sha256","balance_evidence_sha256"):
            x=a.get(fld)
            if not isinstance(x,str) or not re.fullmatch(r"[0-9a-f]{64}",x): errors.append(f"{p}:invalid_{fld}")
    result={"status":"PASS" if not errors and accounts else "FAIL_CLOSED","errors":sorted(errors),"account_count":len(accounts),"total_observed_raw":str(total),"role_balances_raw":{k:str(v) for k,v in sorted(roles.items())},"registry_sha256":sha256(reg)}
    result["reconciliation_sha256"]=sha256({"registry_sha256":result["registry_sha256"],"roles":result["role_balances_raw"],"account_count":len(accounts),"observed_slot":observed_slot})
    return result

def distribution_value_basis(revenue_amount:int,revenue_unit:str,proposed_thf_budget_raw:Optional[int]=None,conversion_basis_sha256:Optional[str]=None)->Dict[str,Any]:
    if not isinstance(revenue_amount,int) or revenue_amount<0: raise ValueError("revenue_amount must be nonnegative integer")
    blockers=[]; share_source=revenue_amount*SHARE_BPS//10000; budget=None
    if revenue_unit=="THF_RAW": budget=share_source
    else:
        if proposed_thf_budget_raw is None: blockers.append("thf_budget_derivation_missing")
        if not isinstance(conversion_basis_sha256,str) or not re.fullmatch(r"[0-9a-f]{64}",conversion_basis_sha256): blockers.append("conversion_basis_evidence_missing")
        if not blockers:
            if not isinstance(proposed_thf_budget_raw,int) or proposed_thf_budget_raw<0: blockers.append("invalid_proposed_thf_budget_raw")
            else: budget=proposed_thf_budget_raw
    return {"status":"FAIL_CLOSED" if blockers else "REVIEW_READY_NOT_EXECUTION_READY","revenue_unit":revenue_unit,"approved_share_bps":SHARE_BPS,"share_in_source_unit":share_source,"proposed_thf_budget_raw":budget,"conversion_basis_sha256":conversion_basis_sha256,"blockers":sorted(blockers),"execution_authorized":False,"broadcast":False}

def distribution_preview(policy:Dict[str,Any], treasury_validation:Dict[str,Any], revenue_minor:int, eligible:List[Dict[str,Any]])->Dict[str,Any]:
    scan_sensitive(eligible); dc=policy["distribution_controls"]; blockers=[]
    if revenue_minor<0: raise ValueError("revenue_minor must be nonnegative")
    for k in ("per_user_cap_raw","epoch_budget_cap_raw","distribution_reserve_account","delivery_model"):
        if dc.get(k) is None: blockers.append(f"{k}_not_approved")
    if dc.get("revenue_value_basis_status")!="approved": blockers.append("revenue_value_basis_not_approved")
    if treasury_validation.get("status")!="PASS": blockers.append("treasury_registry_not_verified")
    if not eligible: blockers.append("eligible_population_empty")
    if not all(isinstance(x.get("activity_units"),int) and x["activity_units"]>=0 for x in eligible): blockers.append("invalid_activity_units")
    approved_pool_minor=revenue_minor*SHARE_BPS//10000; allocations=[]
    return {"status":"FAIL_CLOSED","blockers":sorted(set(blockers)),"approved_share_bps":SHARE_BPS,"approved_pool_source_minor":approved_pool_minor,"allocated_raw":0,"allocations":allocations,"execution_authorized":False,"transaction_bytes_created":False,"broadcast":False}

def vesting_preview(terms:Dict[str,Any], now_ts:int, grant_raw:int)->Dict[str,Any]:
    scan_sensitive(terms); req=("start_ts","cliff_ts","end_ts","reward_bps"); missing=[k for k in req if k not in terms]
    if missing: return {"status":"FAIL_CLOSED","blockers":[f"missing:{k}" for k in missing],"settlement_authorized":False}
    s,c,e=[int(terms[k]) for k in ("start_ts","cliff_ts","end_ts")]
    if not (0<=s<=c<=e) or e==s or grant_raw<0 or not (0<=int(terms["reward_bps"])<=10000): return {"status":"FAIL_CLOSED","blockers":["invalid_terms"],"settlement_authorized":False}
    vested=0 if now_ts<c else (grant_raw if now_ts>=e else grant_raw*(now_ts-s)//(e-s)); reward=vested*int(terms["reward_bps"])//10000
    return {"status":"REVIEW_READY_NOT_EXECUTION_READY","vested_raw":vested,"unvested_raw":grant_raw-vested,"lock_reward_preview_raw":reward,"settlement_authorized":False,"broadcast":False}

def burn_preview(audit:Dict[str,Any], treasury_validation:Dict[str,Any])->Dict[str,Any]:
    supply=int(audit["supply_raw"]); headroom=max(0,supply-SUPPLY_FLOOR_RAW); verified=None; review_cap=None; blockers=[]
    if treasury_validation.get("status")!="PASS": blockers.append("treasury_registry_not_verified")
    else:
        verified=int(treasury_validation.get("role_balances_raw",{}).get("burn_reserve","0")); review_cap=min(headroom,verified)
        if verified<=0: blockers.append("verified_burn_reserve_empty")
    return {"status":"FAIL_CLOSED" if blockers else "REVIEW_READY_NOT_EXECUTION_READY","supply_raw":str(supply),"supply_floor_raw":str(SUPPLY_FLOOR_RAW),"theoretical_headroom_raw":str(headroom),"verified_burn_reserve_raw":None if verified is None else str(verified),"review_cap_raw":None if review_cap is None else str(review_cap),"execution_authorized":False,"instruction_bytes_created":False,"broadcast":False,"blockers":blockers}

def approval_manifest(kind:str, treasury_policy:Dict[str,Any], evidence_sha256:Iterable[str])->Dict[str,Any]:
    scan_sensitive(treasury_policy); cls=treasury_policy.get("approval_classes",{}).get(kind)
    if not cls: raise ValueError("unsupported approval class")
    ev=sorted(set(evidence_sha256))
    if any(not re.fullmatch(r"[0-9a-f]{64}",x or "") for x in ev): raise ValueError("invalid evidence sha256")
    out={"schema":"thf-tokenops-approval-intent/v1","network":NETWORK,"mint":MINT,"token_program":TOKEN_PROGRAM,"kind":kind,"minimum_approvals":int(cls["minimum_approvals"]),"execution_model":cls["execution"],"evidence_sha256":ev,"execution_authorized":False,"signed":False,"submitted":False,"broadcast":False,"financial_effect":False}; out["manifest_sha256"]=sha256(out); return out

def validate_unsigned_intent(intent:Dict[str,Any],treasury_policy:Dict[str,Any])->Dict[str,Any]:
    scan_sensitive(intent); errors=[]
    if intent.get("network")!=NETWORK: errors.append("network_mismatch")
    if intent.get("mint")!=MINT: errors.append("mint_mismatch")
    if intent.get("token_program")!=TOKEN_PROGRAM: errors.append("token_program_mismatch")
    kind=intent.get("kind"); cls=treasury_policy.get("approval_classes",{}).get(kind)
    if not cls: errors.append("unsupported_kind")
    amount=intent.get("amount_raw")
    if not isinstance(amount,int) or amount<0: errors.append("invalid_amount_raw")
    ev=intent.get("evidence_sha256") or []
    if not ev or any(not isinstance(x,str) or not re.fullmatch(r"[0-9a-f]{64}",x) for x in ev): errors.append("invalid_evidence")
    if intent.get("signed") is not False or intent.get("broadcast") is not False or intent.get("execution_authorized") is not False: errors.append("execution_flags_must_be_false")
    return {"status":"PASS_NON_BROADCAST" if not errors else "FAIL_CLOSED","errors":sorted(errors),"minimum_approvals":None if not cls else int(cls["minimum_approvals"]),"intent_sha256":sha256(intent),"execution_authorized":False,"broadcast":False}

def incident_assessment(audit:Dict[str,Any])->Dict[str,Any]:
    checks={"network":audit.get("network")==NETWORK,"mint":audit.get("mint")==MINT,"token_program":audit.get("token_program")==TOKEN_PROGRAM,"decimals":int(audit.get("decimals",-1))==DECIMALS,"mint_authority_disabled":audit.get("mint_authority") is None,"freeze_authority_disabled":audit.get("freeze_authority") is None,"supply_floor":int(audit.get("supply_raw",0))>=SUPPLY_FLOOR_RAW,"supply_ceiling":int(audit.get("supply_raw",0))<=SUPPLY_CEILING_RAW}; failed=sorted(k for k,v in checks.items() if not v)
    return {"status":"QUARANTINE" if failed else "NORMAL","failed":failed,"actions":["block_all_financial_intents","preserve_evidence","require_human_multisig_review"] if failed else [],"automatic_rollback":False,"automatic_authority_change":False,"broadcast":False}

def validate_integration_contracts(obj:Dict[str,Any])->Dict[str,Any]:
    scan_sensitive(obj); errors=[]
    for svc in ("Vault","Forge","Core"):
        c=(obj.get("services") or {}).get(svc)
        if not isinstance(c,dict): errors.append(f"{svc}:missing"); continue
        if c.get("network")!=NETWORK or c.get("mint")!=MINT: errors.append(f"{svc}:identity_mismatch")
        if c.get("token_program")!=TOKEN_PROGRAM: errors.append(f"{svc}:token_program_mismatch")
        if c.get("may_sign") is not False: errors.append(f"{svc}:may_sign_must_be_false")
        if c.get("may_broadcast") is not False: errors.append(f"{svc}:may_broadcast_must_be_false")
        if c.get("accepts_private_key_material") is not False: errors.append(f"{svc}:private_key_material_must_be_false")
        if c.get("contract_version") is None: errors.append(f"{svc}:version_missing")
    return {"status":"PASS" if not errors else "FAIL_CLOSED","errors":sorted(errors),"contracts_sha256":sha256(obj)}