#!/usr/bin/env python3
"""Deterministic THF accounting lineage policy/source seal.

Review/accounting evidence only. This module never constructs, signs, submits,
broadcasts, transfers, burns, settles, migrates treasury balances, changes
authorities, or executes DAO decisions.
"""
from __future__ import annotations
import hashlib, json, re
from typing import Any, Dict
from epoch_accounting_lineage import CANONICAL_MINT, CANONICAL_NETWORK, LINEAGE_SCHEMA, canonical_sha256

SEAL_SCHEMA = "thf-tokenops-accounting-policy-source-seal/v1"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS = {"seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair", "signature", "signed_transaction", "raw_transaction", "serialized_transaction"}

def file_sha256(text: str) -> str:
    if not isinstance(text, str): raise ValueError("policy source must be UTF-8 text")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def git_blob_sha1(text: str) -> str:
    if not isinstance(text, str): raise ValueError("policy source must be UTF-8 text")
    data = text.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def _scan(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_KEYS: raise ValueError(f"forbidden sensitive/signature field at {path}.{key}")
            _scan(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value): _scan(item, f"{path}[{index}]")

def _hex(value: Any, size: int, label: str) -> str:
    pattern = HEX40 if size == 40 else HEX64
    if not isinstance(value, str) or not pattern.fullmatch(value): raise ValueError(f"invalid {label}")
    return value

def _verify_lineage(lineage: Dict[str, Any]) -> str:
    if lineage.get("schema") != LINEAGE_SCHEMA: raise ValueError("lineage schema mismatch")
    if lineage.get("network") != CANONICAL_NETWORK or lineage.get("mint") != CANONICAL_MINT: raise ValueError("lineage target mismatch")
    digest = _hex(lineage.get("lineage_checkpoint_sha256"), 64, "lineage SHA-256")
    body = dict(lineage); body.pop("lineage_checkpoint_sha256", None)
    if canonical_sha256(body) != digest: raise ValueError("lineage SHA-256 mismatch")
    execution = lineage.get("execution", {})
    for key in ("transaction_created", "transaction_signed", "transaction_submitted", "broadcast_allowed", "financial_effect", "settlement_executed", "burn_executed", "treasury_migrated", "dao_decision_executed", "private_key_used"):
        if execution.get(key) is not False: raise ValueError(f"unsafe lineage execution flag: {key}")
    if execution.get("wave_mawja_untouched") is not True: raise ValueError("lineage WAVE isolation flag is not preserved")
    return digest

def _verify_policy(policy: Dict[str, Any]) -> list[str]:
    if policy.get("network") != CANONICAL_NETWORK or policy.get("mint") != CANONICAL_MINT: raise ValueError("policy target mismatch")
    verified = policy.get("verified", {})
    if verified.get("decimals") != 8: raise ValueError("authoritative decimals changed")
    if verified.get("mint_authority") is not None or verified.get("freeze_authority") is not None: raise ValueError("authority policy drift")
    economics = policy.get("economics", {})
    if economics.get("active_user_revenue_share") != 0.35: raise ValueError("35% active-user share policy drift")
    if str(economics.get("approved_supply_floor_target_ui")) != "8000000000": raise ValueError("8B supply-floor policy drift")
    if economics.get("burn_source_policy") != "treasury_controlled_balances_only": raise ValueError("burn-source policy drift")
    automation = policy.get("automation", {})
    for key in ("transaction_signing", "transaction_broadcast", "burn_execution", "treasury_transfer_execution", "authority_change_execution"):
        if automation.get(key) is not False: raise ValueError(f"unsafe automation policy: {key}")
    signer = policy.get("signer_policy", {})
    if signer.get("seed_phrase_in_repo") != "forbidden" or signer.get("private_key_in_repo") != "forbidden": raise ValueError("key-material policy drift")
    controls = policy.get("distribution_controls", {})
    blockers: list[str] = []
    if controls.get("anti_whale_cap_required") is not True: raise ValueError("anti-whale requirement removed")
    if controls.get("per_user_cap") is None or controls.get("epoch_budget_cap") is None: blockers.append("anti_whale_caps_not_authoritatively_configured")
    if signer.get("production_policy_status") != "approved": blockers.append("production_signer_policy_not_approved")
    if policy.get("isolation", {}).get("wave_mawja") != "must_not_be_touched": raise ValueError("WAVE isolation policy drift")
    return blockers

def _verify_treasury_policy(policy: Dict[str, Any]) -> None:
    if policy.get("network") != CANONICAL_NETWORK or policy.get("mint") != CANONICAL_MINT: raise ValueError("treasury policy target mismatch")
    if policy.get("control_model") != "external_multisig_required": raise ValueError("treasury control model drift")
    approvals = policy.get("approval_classes", {})
    expected = {"reward_epoch": 2, "vesting_settlement": 2, "burn": 3, "treasury_transfer": 3}
    for name, minimum in expected.items():
        item = approvals.get(name, {})
        if item.get("minimum_approvals") != minimum or item.get("execution") != "external_multisig": raise ValueError(f"treasury approval policy drift: {name}")
    if str(approvals.get("burn", {}).get("supply_floor_ui")) != "8000000000": raise ValueError("treasury burn floor drift")
    guards = policy.get("hard_guards", {})
    for key in ("seed_phrase_forbidden", "private_key_forbidden", "persistent_hot_wallet_forbidden", "broadcast_from_ci_forbidden", "authority_change_forbidden", "minting_forbidden", "third_party_balance_burn_forbidden", "wave_mawja_untouched"):
        if guards.get(key) is not True: raise ValueError(f"treasury hard guard drift: {key}")

def compile_accounting_policy_seal(lineage: Dict[str, Any], policy_text: str, treasury_policy_text: str, request: Dict[str, Any]) -> Dict[str, Any]:
    _scan(lineage); _scan(request)
    lineage_sha = _verify_lineage(lineage)
    try:
        policy = json.loads(policy_text); treasury_policy = json.loads(treasury_policy_text)
    except json.JSONDecodeError as exc: raise ValueError("invalid policy JSON") from exc
    _scan(policy); _scan(treasury_policy)
    blockers = set(_verify_policy(policy)); _verify_treasury_policy(treasury_policy)
    policy_sha = file_sha256(policy_text); treasury_sha = file_sha256(treasury_policy_text)
    policy_blob_actual = git_blob_sha1(policy_text); treasury_blob_actual = git_blob_sha1(treasury_policy_text)
    if request.get("network") != CANONICAL_NETWORK or request.get("mint") != CANONICAL_MINT: raise ValueError("seal request target mismatch")
    if request.get("lineage_checkpoint_sha256") != lineage_sha: raise ValueError("seal detached from lineage checkpoint")
    if request.get("policy_file_sha256") != policy_sha: raise ValueError("policy source SHA-256 mismatch")
    if request.get("treasury_policy_file_sha256") != treasury_sha: raise ValueError("treasury policy source SHA-256 mismatch")
    policy_blob = _hex(request.get("policy_git_blob_sha"), 40, "policy git blob SHA")
    treasury_blob = _hex(request.get("treasury_policy_git_blob_sha"), 40, "treasury policy git blob SHA")
    if policy_blob != policy_blob_actual: raise ValueError("policy git blob identity mismatch")
    if treasury_blob != treasury_blob_actual: raise ValueError("treasury policy git blob identity mismatch")
    source_commit = _hex(request.get("source_commit_sha"), 40, "source commit SHA")
    lineage_source_sha = _hex(request.get("lineage_source_sha256"), 64, "lineage source SHA-256")
    blockers |= set(str(x) for x in lineage.get("blockers", []))
    result = {"schema": SEAL_SCHEMA, "network": CANONICAL_NETWORK, "mint": CANONICAL_MINT, "request_id": str(request.get("request_id", "")), "lineage_checkpoint_sha256": lineage_sha, "policy_source": {"policy_file_sha256": policy_sha, "policy_git_blob_sha": policy_blob, "treasury_policy_file_sha256": treasury_sha, "treasury_policy_git_blob_sha": treasury_blob, "lineage_source_sha256": lineage_source_sha, "source_commit_sha": source_commit}, "policy_invariants": {"active_user_revenue_share": "35%", "approved_supply_floor_target_ui": "8000000000", "external_multisig_required": True}, "seal_review_eligible": len(blockers) == 0, "blockers": sorted(blockers), "execution": {"transaction_created": False, "transaction_signed": False, "transaction_submitted": False, "broadcast_allowed": False, "financial_effect": False, "settlement_executed": False, "burn_executed": False, "treasury_migrated": False, "dao_decision_executed": False, "private_key_used": False, "external_multisig_required": True, "wave_mawja_untouched": True}}
    result["accounting_policy_seal_sha256"] = canonical_sha256(result)
    return result
