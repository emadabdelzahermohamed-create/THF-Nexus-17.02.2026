#!/usr/bin/env python3
"""Cryptographically bind THF token-account verifier output to compiler input.

Fail-closed and offline. This module does not create, serialize, sign, simulate,
submit, or broadcast transactions. It verifies that token-account metadata has
not changed since mainnet verification, binds it to the existing control-plane
snapshot, and emits compiler input only with execution disabled.
"""
from __future__ import annotations
import hashlib, json, re, sys

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
DECIMALS = 8
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN = {"seed", "seed_phrase", "private_key", "secret_key", "signature", "signed_transaction"}


def canonical_sha(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def require_hex64(value: object, name: str) -> str:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise ValueError(f"{name} must be lowercase 64-hex")
    return value


def reject_forbidden(obj: object) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).lower() in FORBIDDEN:
                raise ValueError("secret/signature fields forbidden")
            reject_forbidden(v)
    elif isinstance(obj, list):
        for v in obj:
            reject_forbidden(v)


def validate_verification(record: dict, *, require_treasury: bool) -> dict:
    reject_forbidden(record)
    supplied = require_hex64(record.get("verification_sha256"), "verification_sha256")
    core = dict(record)
    core.pop("verification_sha256", None)
    if canonical_sha(core) != supplied:
        raise ValueError("verification digest mismatch: token-account metadata changed after verification")
    if core.get("mint") != MINT or core.get("owner_program") != TOKEN_PROGRAM:
        raise ValueError("canonical mint/program mismatch")
    if int(core.get("decimals", -1)) != DECIMALS:
        raise ValueError("decimals mismatch")
    if core.get("onchain_verified") is not True:
        raise ValueError("on-chain verification required")
    if core.get("transaction_created") is not False or core.get("transaction_signed") is not False or core.get("transaction_submitted") is not False:
        raise ValueError("verification record is not read-only")
    if core.get("financial_effect") is not False:
        raise ValueError("verification record reports financial effect")
    if require_treasury:
        if core.get("treasury_controlled") is not True:
            raise ValueError("source is not verified treasury-controlled")
        require_hex64(core.get("control_evidence_sha256"), "control_evidence_sha256")
    return record


def build(req: dict) -> dict:
    reject_forbidden(req)
    if req.get("mint") != MINT:
        raise ValueError("canonical mint mismatch")
    op = req.get("operation")
    if op not in {"transfer_checked", "burn_checked"}:
        raise ValueError("unsupported operation")
    binding = require_hex64(req.get("control_plane_binding_sha256"), "control_plane_binding_sha256")
    source = validate_verification(req.get("source_verification") or {}, require_treasury=True)
    dest = None
    if op == "transfer_checked":
        dest = validate_verification(req.get("destination_verification") or {}, require_treasury=False)
    amount = int(req.get("amount_raw", 0))
    if amount <= 0 or amount > 2**64 - 1:
        raise ValueError("amount_raw must fit positive u64")
    authority = req.get("authority_pubkey")
    if authority != source.get("owner_wallet"):
        raise ValueError("authority must equal verified source owner")

    compiler_request = {
        "mint": MINT,
        "operation": op,
        "amount_raw": str(amount),
        "decimals": DECIMALS,
        "control_plane_binding_sha256": binding,
        "source": source,
        "authority_pubkey": authority,
    }
    if dest is not None:
        compiler_request["destination"] = dest

    core = {
        "version": 1,
        "network": "solana-mainnet-beta",
        "mint": MINT,
        "operation": op,
        "control_plane_binding_sha256": binding,
        "source_verification_sha256": source["verification_sha256"],
        "destination_verification_sha256": dest["verification_sha256"] if dest else None,
        "compiler_request": compiler_request,
        "verification_binding_enforced": True,
        "ready_for_compilation": True,
        "ready_for_transaction_serialization": False,
        "ready_for_signing": False,
        "broadcast_allowed": False,
        "financial_effect": False,
    }
    core["verifier_compiler_binding_sha256"] = canonical_sha(core)
    return core


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: verifier_compiler_binding.py INPUT.json OUTPUT.json")
    req = json.load(open(sys.argv[1]))
    out = build(req)
    with open(sys.argv[2], "w") as f:
        json.dump(out, f, indent=2, sort_keys=True); f.write("\n")
    print("THF_TOKENOPS_VERIFIER_COMPILER_BINDING=PASS")
    print("TRANSACTION_SERIALIZED=FALSE")
    print("TRANSACTION_SIGNED=FALSE")
    print("TRANSACTION_SUBMITTED=FALSE")
    print("FINANCIAL_EFFECT=FALSE")
    print("WAVE_UNTOUCHED=TRUE")

if __name__ == "__main__":
    main()
