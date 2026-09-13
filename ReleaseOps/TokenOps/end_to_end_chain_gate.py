#!/usr/bin/env python3
"""End-to-end offline integrity gate for THF TokenOps financial instruction envelopes.

Chain enforced:
Control-plane binding -> verified token-account digests -> verifier/compiler binding
-> deterministic SPL instruction envelope -> end-to-end chain digest.

This module is deliberately non-executing: it does not serialize a transaction,
sign, simulate, submit, broadcast, transfer, burn, or change authorities.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys

from verifier_compiler_binding import build as build_binding
from spl_instruction_compiler import build as build_instruction

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN = {"seed", "seed_phrase", "private_key", "secret_key", "signature", "signed_transaction"}


def canonical_sha(obj: dict) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def reject_forbidden(obj: object) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if str(key).lower() in FORBIDDEN:
                raise ValueError("secret/signature fields forbidden")
            reject_forbidden(value)
    elif isinstance(obj, list):
        for value in obj:
            reject_forbidden(value)


def require_hex64(value: object, name: str) -> str:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise ValueError(f"{name} must be lowercase 64-hex")
    return value


def validate_binding_digest(binding: dict) -> None:
    supplied = require_hex64(
        binding.get("verifier_compiler_binding_sha256"),
        "verifier_compiler_binding_sha256",
    )
    core = dict(binding)
    core.pop("verifier_compiler_binding_sha256", None)
    if canonical_sha(core) != supplied:
        raise ValueError("verifier/compiler binding digest mismatch")


def validate_instruction_digest(envelope: dict) -> None:
    supplied = require_hex64(
        envelope.get("instruction_envelope_sha256"), "instruction_envelope_sha256"
    )
    core = dict(envelope)
    core.pop("instruction_envelope_sha256", None)
    if canonical_sha(core) != supplied:
        raise ValueError("instruction envelope digest mismatch")


def build(req: dict) -> dict:
    reject_forbidden(req)
    if req.get("mint") != MINT:
        raise ValueError("canonical mint mismatch")

    # The existing binding gate independently recomputes on-chain verification digests.
    binding = build_binding(req)
    validate_binding_digest(binding)

    # The compiler receives only the compiler_request produced by the verified bridge.
    envelope = build_instruction(binding["compiler_request"])
    validate_instruction_digest(envelope)

    if envelope.get("control_plane_binding_sha256") != binding.get(
        "control_plane_binding_sha256"
    ):
        raise ValueError("control-plane binding was not preserved into instruction envelope")
    if envelope.get("mint") != MINT or binding.get("mint") != MINT:
        raise ValueError("canonical mint continuity failure")
    if envelope.get("operation") != binding.get("operation"):
        raise ValueError("operation continuity failure")

    core = {
        "version": 1,
        "network": "solana-mainnet-beta",
        "mint": MINT,
        "operation": binding["operation"],
        "control_plane_binding_sha256": binding["control_plane_binding_sha256"],
        "source_verification_sha256": binding["source_verification_sha256"],
        "destination_verification_sha256": binding[
            "destination_verification_sha256"
        ],
        "verifier_compiler_binding_sha256": binding[
            "verifier_compiler_binding_sha256"
        ],
        "instruction_envelope_sha256": envelope["instruction_envelope_sha256"],
        "integrity_chain_enforced": True,
        "ready_for_transaction_serialization": False,
        "ready_for_simulation": False,
        "ready_for_signing": False,
        "broadcast_allowed": False,
        "financial_effect": False,
    }
    core["end_to_end_chain_sha256"] = canonical_sha(core)
    return {"chain": core, "binding": binding, "instruction_envelope": envelope}


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: end_to_end_chain_gate.py INPUT.json OUTPUT.json")
    req = json.load(open(sys.argv[1], encoding="utf-8"))
    out = build(req)
    with open(sys.argv[2], "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("THF_TOKENOPS_END_TO_END_CHAIN_GATE=PASS")
    print("TRANSACTION_SERIALIZED=FALSE")
    print("TRANSACTION_SIGNED=FALSE")
    print("TRANSACTION_SUBMITTED=FALSE")
    print("TRANSACTION_BROADCAST=FALSE")
    print("FINANCIAL_EFFECT=FALSE")
    print("WAVE_UNTOUCHED=TRUE")


if __name__ == "__main__":
    main()
