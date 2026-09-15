#!/usr/bin/env python3
"""Build a deterministic, non-executable THF TokenOps signer handoff bundle.
The bundle is evidence-only: no private keys, signing, broadcasting or settlement.
"""
from __future__ import annotations
import hashlib, json

SCHEMA="thf-tokenops-signer-handoff/v1"
ALLOWED_OPERATIONS={"transfer","burn","lock_reward_settlement","vesting_settlement","treasury_migration","dao_execution","authority_change"}

def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"))
def digest(v): return hashlib.sha256(_canon(v).encode()).hexdigest()
def _sha(v,n=64): return isinstance(v,str) and len(v)==n and all(c in "0123456789abcdef" for c in v.lower())
def _pubkey(v): return isinstance(v,str) and 32 <= len(v) <= 44

def build(*, operation:str, simulation_receipt:dict, expected_mint:str, policy_sha256:str,
          transaction_manifest_sha256:str, governance_evidence_sha256:str|None=None,
          multisig_policy_sha256:str|None=None)->dict:
    blockers=[]
    if operation not in ALLOWED_OPERATIONS: blockers.append("OPERATION_NOT_ALLOWED")
    if simulation_receipt.get("status")!="SIMULATION_EVIDENCE_READY_FOR_EXTERNAL_SIGNER_REVIEW": blockers.append("SIMULATION_NOT_READY")
    if simulation_receipt.get("sign") is not False or simulation_receipt.get("broadcast") is not False or simulation_receipt.get("financial_execution") is not False:
        blockers.append("UNSAFE_SIMULATION_FLAGS")
    if simulation_receipt.get("mint")!=expected_mint or not _pubkey(expected_mint): blockers.append("MINT_MISMATCH")
    if not _sha(simulation_receipt.get("simulation_receipt_sha256")): blockers.append("SIMULATION_RECEIPT_SHA256_INVALID")
    if not _sha(simulation_receipt.get("message_sha256")): blockers.append("MESSAGE_SHA256_INVALID")
    if not _sha(policy_sha256): blockers.append("POLICY_SHA256_INVALID")
    if not _sha(transaction_manifest_sha256): blockers.append("TRANSACTION_MANIFEST_SHA256_INVALID")
    governance_required=operation in {"burn","treasury_migration","dao_execution","authority_change"}
    if governance_required and not _sha(governance_evidence_sha256): blockers.append("GOVERNANCE_EVIDENCE_REQUIRED")
    if not _sha(multisig_policy_sha256): blockers.append("MULTISIG_POLICY_SHA256_INVALID")
    out={"schema":SCHEMA,"operation":operation,"mint":expected_mint,
         "epoch_id":simulation_receipt.get("epoch_id"),
         "reward_epoch_commitment_sha256":simulation_receipt.get("reward_epoch_commitment_sha256"),
         "simulation_receipt_sha256":simulation_receipt.get("simulation_receipt_sha256"),
         "message_sha256":simulation_receipt.get("message_sha256"),"policy_sha256":policy_sha256,
         "transaction_manifest_sha256":transaction_manifest_sha256,
         "governance_evidence_sha256":governance_evidence_sha256,
         "multisig_policy_sha256":multisig_policy_sha256,"governance_required":governance_required,
         "blockers":sorted(set(blockers)),"contains_private_keys":False,"sign":False,"broadcast":False,
         "financial_execution":False,"status":"BLOCKED" if blockers else "READY_FOR_USER_CONTROLLED_MULTISIG_REVIEW"}
    out["signer_handoff_sha256"]=digest(out)
    return out
