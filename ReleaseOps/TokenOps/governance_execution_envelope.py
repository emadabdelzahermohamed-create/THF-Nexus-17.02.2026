#!/usr/bin/env python3
"""Fail-closed governance/treasury execution envelope for THF TokenOps.

Planning and review only. This module never signs, broadcasts, transfers, burns,
changes authorities, settles vesting, migrates treasury, or executes DAO actions.
"""
from __future__ import annotations
import hashlib, json

SCHEMA = "thf-tokenops-governance-envelope/v1"
IRREVERSIBLE = {
    "transfer", "burn", "authority_change", "treasury_migration",
    "vesting_settlement", "dao_execution", "lock_reward_settlement",
}

def _canon(v): return json.dumps(v, sort_keys=True, separators=(",", ":"))
def digest(v): return hashlib.sha256(_canon(v).encode()).hexdigest()

def build_envelope(*, action:str, source_commit_sha:str, policy_sha256:str,
                   transaction_manifest_sha256:str|None,
                   simulation_sha256:str|None,
                   governance_evidence_sha256:str|None,
                   treasury_pubkey:str|None,
                   expected_mint:str|None,
                   expected_supply_atomic:int|None,
                   observed_mint:str|None=None,
                   observed_supply_atomic:int|None=None)->dict:
    if action not in IRREVERSIBLE:
        raise ValueError("unsupported financial action")
    blockers=[]
    required={
        "source_commit_sha":source_commit_sha,
        "policy_sha256":policy_sha256,
        "transaction_manifest_sha256":transaction_manifest_sha256,
        "simulation_sha256":simulation_sha256,
        "governance_evidence_sha256":governance_evidence_sha256,
        "treasury_pubkey":treasury_pubkey,
        "expected_mint":expected_mint,
        "expected_supply_atomic":expected_supply_atomic,
    }
    blockers += [f"MISSING_{k.upper()}" for k,v in required.items() if v is None or v==""]
    if observed_mint is not None and expected_mint is not None and observed_mint != expected_mint:
        blockers.append("ONCHAIN_MINT_MISMATCH")
    if observed_supply_atomic is not None and expected_supply_atomic is not None and int(observed_supply_atomic) != int(expected_supply_atomic):
        blockers.append("ONCHAIN_SUPPLY_MISMATCH")
    out={"schema":SCHEMA,"action":action,"source_commit_sha":source_commit_sha,
         "policy_sha256":policy_sha256,"transaction_manifest_sha256":transaction_manifest_sha256,
         "simulation_sha256":simulation_sha256,"governance_evidence_sha256":governance_evidence_sha256,
         "treasury_pubkey":treasury_pubkey,"expected_mint":expected_mint,
         "expected_supply_atomic":expected_supply_atomic,"observed_mint":observed_mint,
         "observed_supply_atomic":observed_supply_atomic,"blockers":sorted(set(blockers)),
         "sign":False,"broadcast":False,"financial_execution":False,
         "requires_user_controlled_multisig":True,
         "status":"BLOCKED" if blockers else "READY_FOR_EXTERNAL_SIGNER_REVIEW"}
    out["envelope_sha256"]=digest(out)
    return out

def validate_for_automation(envelope:dict)->bool:
    """Automation must never execute an irreversible financial action."""
    if envelope.get("action") not in IRREVERSIBLE: return False
    if envelope.get("sign") or envelope.get("broadcast") or envelope.get("financial_execution"): return False
    if not envelope.get("requires_user_controlled_multisig"): return False
    return envelope.get("status") in {"BLOCKED","READY_FOR_EXTERNAL_SIGNER_REVIEW"}
