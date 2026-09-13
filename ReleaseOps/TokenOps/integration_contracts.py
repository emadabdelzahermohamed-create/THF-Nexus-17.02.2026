#!/usr/bin/env python3
"""Hash-only, non-custodial TokenOps integration contracts for Vault/Forge/Core."""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict
MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"; NETWORK="solana-mainnet-beta"
SCHEMA="thf-tokenops-vault-forge-core-contracts/v1"
FORBIDDEN={"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature","signatures",
"transaction_bytes","instruction_bytes","raw_transaction","signed_transaction","serialized_transaction"}

def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
def scan(v,p="$"):
    if isinstance(v,dict):
        for k,x in v.items():
            if str(k).lower().replace("-","_") in FORBIDDEN: raise ValueError(f"forbidden field {p}.{k}")
            scan(x,f"{p}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): scan(x,f"{p}[{i}]")

def build_contracts(policy:Dict[str,Any], treasury:Dict[str,Any])->Dict[str,Any]:
    scan(policy);scan(treasury)
    if policy.get("mint")!=MINT or treasury.get("mint")!=MINT: raise ValueError("mint mismatch")
    if policy.get("network")!=NETWORK or treasury.get("network")!=NETWORK: raise ValueError("network mismatch")
    common={"network":NETWORK,"mint":MINT,"policy_sha256":sha(policy),"treasury_policy_sha256":sha(treasury)}
    contracts={
      "Vault":{"direction":"TokenOps<->Vault","allowed_inputs":["treasury_account_pubkeys","balance_observation_hashes",
        "ownership_attestation_hashes","multisig_policy_hash"],"allowed_outputs":["treasury_inventory_snapshot_hash",
        "custody_readiness_status"],"forbidden":["private_keys","seed_phrases","signatures","transaction_bytes"],
        "binding_financial_action":False},
      "Forge":{"direction":"TokenOps<->Forge","allowed_inputs":["unsigned_intent_hash","review_manifest_hash",
        "simulation_receipt_hash","approval_readiness_hash"],"allowed_outputs":["unsigned_plan_validation_hash",
        "simulation_summary_hash"],"forbidden":["signatures","broadcast","raw_key_material"],"binding_financial_action":False},
      "Core":{"direction":"TokenOps<->Core","allowed_inputs":["activity_evidence_hash","eligible_user_set_hash",
        "epoch_revenue_hash"],"allowed_outputs":["reward_budget_hash","allocation_review_hash","accounting_receipt_hash"],
        "forbidden":["raw_health_data","private_keys","signatures","broadcast"],"binding_financial_action":False}}
    r={"schema":SCHEMA,**common,"contracts":contracts,"execution_authorized":False,"broadcast_allowed":False,
       "financial_effect":False,"wave_mawja_untouched":True}
    r["integration_contracts_sha256"]=sha(r); return r
