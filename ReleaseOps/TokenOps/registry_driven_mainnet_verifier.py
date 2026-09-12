#!/usr/bin/env python3
"""Registry-driven read-only verifier for canonical THF treasury token accounts.

The caller may select only a public owner/token-account pair. All treasury-control
metadata is derived from a validated registry snapshot; caller-supplied allowlists
or control-evidence hashes are not accepted. No transaction is created or signed.
"""
from __future__ import annotations

import hashlib
import json
import sys
from typing import Any

from mainnet_token_account_verifier import DEFAULT_RPC, MINT, _rpc, verify_account
from treasury_control_registry import candidate_from_registry

FORBIDDEN_REQUEST_FIELDS = {
    "treasury_owner_allowlist",
    "control_evidence_sha256",
    "candidate",
    "candidates",
    "seed",
    "seed_phrase",
    "mnemonic",
    "private_key",
    "secret_key",
    "keypair",
    "signature",
    "signed_transaction",
}


def _canonical_sha256(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _reject_forbidden_request_fields(value: Any, path: str = "request") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_REQUEST_FIELDS:
                raise ValueError(f"caller-supplied control/secret field forbidden at {path}.{key}")
            _reject_forbidden_request_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_request_fields(child, f"{path}[{index}]")


def build_registry_driven_verification(
    registry_snapshot: dict,
    token_account: str,
    owner_wallet: str,
    account_value: dict | None,
) -> dict:
    """Derive verifier input from registry and bind live verification to its snapshot."""
    candidate = candidate_from_registry(registry_snapshot, token_account, owner_wallet)
    verified = verify_account(candidate, account_value)
    if verified.get("treasury_controlled") is not True:
        raise ValueError("registry-derived account did not verify as treasury controlled")
    if verified.get("owner_wallet") != owner_wallet:
        raise ValueError("on-chain owner does not match registry owner")
    if verified.get("token_account") != token_account:
        raise ValueError("verified token account mismatch")
    if verified.get("control_evidence_sha256") != candidate["control_evidence_sha256"]:
        raise ValueError("control evidence mismatch")

    core = {
        "version": 1,
        "network": "solana-mainnet-beta",
        "mint": MINT,
        "registry_snapshot_sha256": candidate["registry_snapshot_sha256"],
        "control_evidence_sha256": candidate["control_evidence_sha256"],
        "owner_wallet": owner_wallet,
        "token_account": token_account,
        "verification_sha256": verified["verification_sha256"],
        "verified_account": verified,
        "candidate_source": "validated_treasury_control_registry_only",
        "caller_supplied_allowlist": False,
        "caller_supplied_control_evidence": False,
        "transaction_created": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "ready_for_simulation": False,
        "ready_for_signing": False,
        "broadcast_allowed": False,
        "financial_effect": False,
    }
    core["registry_driven_verification_sha256"] = _canonical_sha256(core)
    return core


def verify_request(request: dict, account_value: dict | None = None) -> dict:
    _reject_forbidden_request_fields({
        key: value for key, value in request.items() if key != "registry_snapshot"
    })
    if request.get("mint", MINT) != MINT:
        raise ValueError("canonical mint mismatch")
    registry_snapshot = request.get("registry_snapshot")
    if not isinstance(registry_snapshot, dict):
        raise ValueError("registry_snapshot required")
    token_account = request.get("token_account")
    owner_wallet = request.get("owner_wallet")
    if not isinstance(token_account, str) or not token_account:
        raise ValueError("token_account required")
    if not isinstance(owner_wallet, str) or not owner_wallet:
        raise ValueError("owner_wallet required")

    if account_value is None:
        rpc_url = request.get("rpc_url") or DEFAULT_RPC
        result = _rpc(
            rpc_url,
            "getAccountInfo",
            [token_account, {"encoding": "jsonParsed", "commitment": "confirmed"}],
        )
        account_value = result.get("value")

    return build_registry_driven_verification(
        registry_snapshot, token_account, owner_wallet, account_value
    )


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: registry_driven_mainnet_verifier.py INPUT.json OUTPUT.json")
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        request = json.load(handle)
    output = verify_request(request)
    with open(sys.argv[2], "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("THF_TOKENOPS_REGISTRY_DRIVEN_VERIFIER=PASS")
    print(f"REGISTRY_DRIVEN_VERIFICATION_SHA256={output['registry_driven_verification_sha256']}")
    print("CALLER_SUPPLIED_ALLOWLIST=FALSE")
    print("CALLER_SUPPLIED_CONTROL_EVIDENCE=FALSE")
    print("TRANSACTION_CREATED=FALSE")
    print("TRANSACTION_SIGNED=FALSE")
    print("TRANSACTION_SUBMITTED=FALSE")
    print("READY_FOR_SIMULATION=FALSE")
    print("PRIVATE_KEY_USED=FALSE")
    print("WAVE_UNTOUCHED=TRUE")


if __name__ == "__main__":
    main()
