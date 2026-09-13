#!/usr/bin/env python3
"""Bind THF treasury-control registry evidence into the offline E2E instruction chain.

This is an additive fail-closed gate. It validates that the source token account and
owner are explicitly present in a deterministic treasury-control registry snapshot,
that the source on-chain verification record carries the same external evidence hash,
and that the resulting existing end-to-end chain is cryptographically bound to the
registry snapshot digest.

No transaction is serialized, signed, simulated, submitted, broadcast, transferred,
burned, or otherwise executed by this module.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys

from end_to_end_chain_gate import build as build_existing_chain
from treasury_control_registry import candidate_from_registry

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_FRAGMENTS = (
    "seed", "mnemonic", "private_key", "secret_key", "keypair",
    "signed_transaction", "signature", "recovery_phrase", "passphrase",
)


def canonical_sha(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def reject_forbidden(value: object, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if any(fragment in normalized for fragment in FORBIDDEN_FRAGMENTS):
                raise ValueError(f"secret/signature fields forbidden at {path}.{key}")
            reject_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_forbidden(child, f"{path}[{index}]")


def require_hex64(value: object, name: str) -> str:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise ValueError(f"{name} must be lowercase 64-hex")
    return value


def build(req: dict) -> dict:
    reject_forbidden(req)
    if req.get("mint") != MINT:
        raise ValueError("canonical mint mismatch")

    registry = req.get("treasury_registry_snapshot")
    if not isinstance(registry, dict):
        raise ValueError("treasury_registry_snapshot required")
    registry_sha = require_hex64(
        registry.get("registry_snapshot_sha256"), "registry_snapshot_sha256"
    )

    source = req.get("source_verification") or {}
    if source.get("treasury_controlled") is not True:
        raise ValueError("source is not verified treasury-controlled")
    source_account = source.get("token_account")
    source_owner = source.get("owner_wallet")
    if not isinstance(source_account, str) or not source_account:
        raise ValueError("source token account missing")
    if not isinstance(source_owner, str) or not source_owner:
        raise ValueError("source owner missing")

    registry_candidate = candidate_from_registry(registry, source_account, source_owner)
    if registry_candidate.get("registry_snapshot_sha256") != registry_sha:
        raise ValueError("registry snapshot continuity failure")
    if registry_candidate.get("control_evidence_sha256") != source.get(
        "control_evidence_sha256"
    ):
        raise ValueError("registry/source control evidence mismatch")
    if registry_candidate.get("treasury_owner_allowlist") != [source_owner]:
        raise ValueError("registry/source owner continuity failure")

    existing_req = dict(req)
    existing_req.pop("treasury_registry_snapshot", None)
    existing = build_existing_chain(existing_req)
    chain = existing["chain"]

    if chain.get("mint") != MINT:
        raise ValueError("canonical mint continuity failure")
    if chain.get("source_verification_sha256") != source.get("verification_sha256"):
        raise ValueError("source verification continuity failure")
    if chain.get("ready_for_transaction_serialization") is not False:
        raise ValueError("transaction serialization unexpectedly enabled")
    if chain.get("ready_for_simulation") is not False:
        raise ValueError("financial simulation unexpectedly enabled")
    if chain.get("ready_for_signing") is not False:
        raise ValueError("signing unexpectedly enabled")
    if chain.get("broadcast_allowed") is not False:
        raise ValueError("broadcast unexpectedly enabled")
    if chain.get("financial_effect") is not False:
        raise ValueError("financial effect unexpectedly enabled")

    bound = {
        "version": 1,
        "network": "solana-mainnet-beta",
        "mint": MINT,
        "operation": chain["operation"],
        "registry_snapshot_sha256": registry_sha,
        "control_evidence_sha256": source["control_evidence_sha256"],
        "source_verification_sha256": chain["source_verification_sha256"],
        "verifier_compiler_binding_sha256": chain[
            "verifier_compiler_binding_sha256"
        ],
        "instruction_envelope_sha256": chain["instruction_envelope_sha256"],
        "end_to_end_chain_sha256": chain["end_to_end_chain_sha256"],
        "registry_membership_enforced": True,
        "registry_evidence_continuity_enforced": True,
        "ready_for_transaction_serialization": False,
        "ready_for_simulation": False,
        "ready_for_signing": False,
        "broadcast_allowed": False,
        "financial_effect": False,
    }
    bound["registry_bound_chain_sha256"] = canonical_sha(bound)
    return {
        "registry_bound_chain": bound,
        "registry_candidate": registry_candidate,
        "existing_end_to_end": existing,
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: registry_bound_end_to_end_gate.py INPUT.json OUTPUT.json"
        )
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        req = json.load(handle)
    out = build(req)
    with open(sys.argv[2], "w", encoding="utf-8") as handle:
        json.dump(out, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("THF_TOKENOPS_REGISTRY_BOUND_END_TO_END_GATE=PASS")
    print("TRANSACTION_SERIALIZED=FALSE")
    print("SIMULATION_ENABLED=FALSE")
    print("TRANSACTION_SIGNED=FALSE")
    print("TRANSACTION_SUBMITTED=FALSE")
    print("TRANSACTION_BROADCAST=FALSE")
    print("FINANCIAL_EFFECT=FALSE")
    print("WAVE_UNTOUCHED=TRUE")


if __name__ == "__main__":
    main()
