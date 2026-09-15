#!/usr/bin/env python3
"""Fail-closed binding of an unsigned Solana simulation receipt to a THF reward epoch.
No signing, broadcasting, settlement, authority mutation, or private-key handling.
"""
from __future__ import annotations
import hashlib, json

SCHEMA="thf-tokenops-simulation-receipt/v1"

def _canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"))
def digest(v): return hashlib.sha256(_canon(v).encode()).hexdigest()
def _sha(v): return isinstance(v,str) and len(v)==64 and all(c in "0123456789abcdef" for c in v.lower())
def _pubkey(v): return isinstance(v,str) and 32 <= len(v) <= 44

def bind(*, epoch:dict, simulation:dict, expected_mint:str, expected_cluster:str="mainnet-beta")->dict:
    blockers=[]
    if epoch.get("status")!="COMMITTED_FOR_SIMULATION": blockers.append("EPOCH_NOT_COMMITTED")
    if epoch.get("sign") is not False or epoch.get("broadcast") is not False or epoch.get("financial_execution") is not False:
        blockers.append("UNSAFE_EPOCH_FLAGS")
    if not _sha(epoch.get("reward_epoch_commitment_sha256")): blockers.append("EPOCH_COMMITMENT_INVALID")
    if simulation.get("cluster")!=expected_cluster: blockers.append("CLUSTER_MISMATCH")
    if simulation.get("mint")!=expected_mint or not _pubkey(expected_mint): blockers.append("MINT_MISMATCH")
    if simulation.get("unsigned") is not True: blockers.append("SIMULATION_NOT_UNSIGNED")
    if simulation.get("broadcast") is not False: blockers.append("SIMULATION_BROADCAST_FLAG_UNSAFE")
    if simulation.get("err") not in (None, False): blockers.append("SIMULATION_ERROR")
    if not isinstance(simulation.get("slot"),int) or simulation.get("slot",0)<=0: blockers.append("SIMULATION_SLOT_INVALID")
    if not _sha(simulation.get("message_sha256")): blockers.append("MESSAGE_SHA256_INVALID")
    if simulation.get("reward_epoch_commitment_sha256")!=epoch.get("reward_epoch_commitment_sha256"):
        blockers.append("EPOCH_BINDING_MISMATCH")
    out={"schema":SCHEMA,"epoch_id":epoch.get("epoch_id"),"reward_epoch_commitment_sha256":epoch.get("reward_epoch_commitment_sha256"),
         "cluster":expected_cluster,"mint":expected_mint,"slot":simulation.get("slot"),"message_sha256":simulation.get("message_sha256"),
         "blockers":sorted(set(blockers)),"contains_private_keys":False,"sign":False,"broadcast":False,"financial_execution":False,
         "status":"BLOCKED" if blockers else "SIMULATION_EVIDENCE_READY_FOR_EXTERNAL_SIGNER_REVIEW"}
    out["simulation_receipt_sha256"]=digest(out)
    return out
