#!/usr/bin/env python3
"""Deterministic public-only registry for THF treasury control evidence.

This registry stores public wallet/token-account identifiers and SHA-256 evidence
references only. It never stores signer material and never authorizes execution.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from typing import Any

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
NETWORK = "solana-mainnet-beta"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEY_FRAGMENTS = (
    "seed", "mnemonic", "private_key", "secret_key", "keypair", "signed_transaction",
    "signature", "recovery_phrase", "passphrase",
)
ALLOWED_EVIDENCE_TYPES = {
    "multisig_config_snapshot",
    "governance_record",
    "custody_control_attestation",
    "treasury_policy_record",
}


def _assert_public_only(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if any(fragment in normalized for fragment in FORBIDDEN_KEY_FRAGMENTS):
                raise ValueError(f"forbidden secret/signature field at {path}.{key}")
            _assert_public_only(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_public_only(child, f"{path}[{index}]")


def _canonical_sha256(value: dict) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def normalize_registry(registry: dict) -> dict:
    _assert_public_only(registry)
    if registry.get("network") != NETWORK:
        raise ValueError("network mismatch")
    if registry.get("mint") != MINT:
        raise ValueError("canonical mint mismatch")
    entries = registry.get("entries")
    if not isinstance(entries, list):
        raise ValueError("entries must be a list")

    seen_owners: set[str] = set()
    seen_accounts: set[str] = set()
    normalized_entries = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"entry {index} must be an object")
        owner = entry.get("owner_wallet")
        if not isinstance(owner, str) or not owner:
            raise ValueError(f"entry {index} owner_wallet required")
        if owner in seen_owners:
            raise ValueError("duplicate owner_wallet")
        seen_owners.add(owner)

        evidence = entry.get("control_evidence_sha256")
        if not isinstance(evidence, str) or not HEX64.fullmatch(evidence):
            raise ValueError("control_evidence_sha256 must be lowercase SHA-256")
        evidence_type = entry.get("evidence_type")
        if evidence_type not in ALLOWED_EVIDENCE_TYPES:
            raise ValueError("unsupported evidence_type")
        governance_reference = entry.get("governance_reference")
        if not isinstance(governance_reference, str) or not governance_reference.strip():
            raise ValueError("governance_reference required")

        token_accounts = entry.get("token_accounts") or []
        if not isinstance(token_accounts, list) or any(not isinstance(x, str) or not x for x in token_accounts):
            raise ValueError("token_accounts must be a string list")
        for account in token_accounts:
            if account in seen_accounts:
                raise ValueError("duplicate token_account across registry")
            seen_accounts.add(account)

        normalized_entries.append({
            "owner_wallet": owner,
            "token_accounts": sorted(token_accounts),
            "control_evidence_sha256": evidence,
            "evidence_type": evidence_type,
            "governance_reference": governance_reference.strip(),
            "execution_authorized": False,
        })

    core = {
        "version": 1,
        "network": NETWORK,
        "mint": MINT,
        "entries": sorted(normalized_entries, key=lambda x: x["owner_wallet"]),
        "public_identifiers_only": True,
        "contains_signer_secrets": False,
        "execution_authorized": False,
        "transaction_signing_enabled": False,
        "transaction_broadcast_enabled": False,
    }
    core["registry_snapshot_sha256"] = _canonical_sha256(core)
    return core


def candidate_from_registry(registry_snapshot: dict, token_account: str, owner_wallet: str) -> dict:
    """Build verifier input from an already-normalized registry snapshot.

    Exact token-account membership is required; owner allowlisting alone is not enough.
    """
    _assert_public_only(registry_snapshot)
    supplied = registry_snapshot.get("registry_snapshot_sha256")
    core = dict(registry_snapshot)
    core.pop("registry_snapshot_sha256", None)
    if not isinstance(supplied, str) or supplied != _canonical_sha256(core):
        raise ValueError("registry snapshot digest mismatch")
    if registry_snapshot.get("execution_authorized") is not False:
        raise ValueError("registry must not authorize execution")

    for entry in registry_snapshot.get("entries") or []:
        if entry.get("owner_wallet") == owner_wallet and token_account in (entry.get("token_accounts") or []):
            return {
                "token_account": token_account,
                "treasury_owner_allowlist": [owner_wallet],
                "control_evidence_sha256": entry["control_evidence_sha256"],
                "registry_snapshot_sha256": supplied,
            }
    raise ValueError("token account is not explicitly registered for treasury control")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: treasury_control_registry.py INPUT.json OUTPUT.json")
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        source = json.load(handle)
    output = normalize_registry(source)
    with open(sys.argv[2], "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("THF_TOKENOPS_TREASURY_CONTROL_REGISTRY=PASS")
    print(f"REGISTRY_SNAPSHOT_SHA256={output['registry_snapshot_sha256']}")
    print("EXECUTION_AUTHORIZED=FALSE")
    print("PRIVATE_KEY_USED=FALSE")
    print("TRANSACTION_BROADCAST=FALSE")
    print("WAVE_UNTOUCHED=TRUE")


if __name__ == "__main__":
    main()
