#!/usr/bin/env python3
"""THF TokenOps -> Vault/Forge/Core read-only integration contract.

Pure planning/verification boundary. It cannot sign, broadcast, settle, burn,
transfer, change authorities, migrate treasury, or execute governance.
"""
from __future__ import annotations
import hashlib, json, re
from typing import Any

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
CONSUMERS = ("Vault", "Forge", "Core")
CONTRACT_VERSION = "tokenops-integration-v1"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def build_integration_contract(*, source_commit_sha: str, mint: str,
                               onchain_snapshot_sha256: str,
                               policy_sha256: str,
                               reward_epoch_commitment_sha256: str,
                               signer_handoff_bundle_sha256: str,
                               snapshot_slot: int,
                               supply_base_units: int,
                               decimals: int,
                               mint_authority: Any,
                               freeze_authority: Any) -> dict[str, Any]:
    reasons: list[str] = []
    if not HEX40.fullmatch(source_commit_sha): reasons.append("invalid_source_commit_sha")
    for name, value in (
        ("onchain_snapshot_sha256", onchain_snapshot_sha256),
        ("policy_sha256", policy_sha256),
        ("reward_epoch_commitment_sha256", reward_epoch_commitment_sha256),
        ("signer_handoff_bundle_sha256", signer_handoff_bundle_sha256),
    ):
        if not HEX64.fullmatch(value): reasons.append(f"invalid_{name}")
    if not mint or len(mint) < 32: reasons.append("invalid_mint")
    if not isinstance(snapshot_slot, int) or snapshot_slot <= 0: reasons.append("invalid_snapshot_slot")
    if not isinstance(supply_base_units, int) or supply_base_units < 0: reasons.append("invalid_supply")
    if not isinstance(decimals, int) or not 0 <= decimals <= 18: reasons.append("invalid_decimals")

    payload = {
        "contract_version": CONTRACT_VERSION,
        "network": "mainnet-beta",
        "source_commit_sha": source_commit_sha,
        "mint": mint,
        "snapshot": {
            "slot": snapshot_slot,
            "supply_base_units": supply_base_units,
            "decimals": decimals,
            "mint_authority": mint_authority,
            "freeze_authority": freeze_authority,
            "evidence_sha256": onchain_snapshot_sha256,
        },
        "commitments": {
            "policy_sha256": policy_sha256,
            "reward_epoch_commitment_sha256": reward_epoch_commitment_sha256,
            "signer_handoff_bundle_sha256": signer_handoff_bundle_sha256,
        },
        "consumers": list(CONSUMERS),
        "capabilities": [
            "read_token_state", "read_reward_epoch_status", "read_handoff_status",
            "verify_evidence_hashes",
        ],
        "forbidden_capabilities": [
            "sign", "broadcast", "transfer", "burn", "change_authority",
            "migrate_treasury", "settle_vesting", "settle_lock_rewards", "execute_dao",
        ],
        "sign": False,
        "broadcast": False,
        "financial_execution": False,
    }
    contract_sha256 = _sha(payload)
    return {
        **payload,
        "status": "BLOCKED" if reasons else "READ_ONLY_CONTRACT_READY",
        "reasons": sorted(set(reasons)),
        "contract_sha256": contract_sha256,
    }


def verify_integration_contract(contract: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if contract.get("contract_version") != CONTRACT_VERSION: reasons.append("version_mismatch")
    if contract.get("network") != "mainnet-beta": reasons.append("network_mismatch")
    if tuple(contract.get("consumers", [])) != CONSUMERS: reasons.append("consumer_set_mismatch")
    if contract.get("sign") is not False: reasons.append("sign_must_be_false")
    if contract.get("broadcast") is not False: reasons.append("broadcast_must_be_false")
    if contract.get("financial_execution") is not False: reasons.append("financial_execution_must_be_false")
    forbidden = set(contract.get("forbidden_capabilities", []))
    required_forbidden = {"sign","broadcast","transfer","burn","change_authority","migrate_treasury","settle_vesting","settle_lock_rewards","execute_dao"}
    if not required_forbidden.issubset(forbidden): reasons.append("forbidden_capability_gap")
    claimed = contract.get("contract_sha256", "")
    body = {k: v for k, v in contract.items() if k not in {"status", "reasons", "contract_sha256"}}
    if not HEX64.fullmatch(claimed) or _sha(body) != claimed: reasons.append("contract_hash_mismatch")
    return {"ok": not reasons, "status": "VERIFIED_READ_ONLY" if not reasons else "BLOCKED", "reasons": sorted(set(reasons))}
