#!/usr/bin/env python3
"""Fail-closed SPL Token financial instruction envelope compiler.

This module NEVER signs, serializes, simulates, submits, or broadcasts a transaction.
It only emits deterministic instruction envelopes after verified treasury metadata and
an existing control-plane binding hash are supplied.
"""
import hashlib, json, re, struct, sys

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
DECIMALS = 8
OPS = {"transfer_checked": 12, "burn_checked": 15}
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58decode(s: str) -> bytes:
    if not isinstance(s, str) or not s:
        raise ValueError("pubkey must be non-empty base58")
    n = 0
    for ch in s:
        try:
            n = n * 58 + B58.index(ch)
        except ValueError as exc:
            raise ValueError("invalid base58 pubkey") from exc
    pad = len(s) - len(s.lstrip("1"))
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    return b"\x00" * pad + raw


def pubkey(s: str) -> str:
    if len(b58decode(s)) != 32:
        raise ValueError("pubkey must decode to 32 bytes")
    return s


def sha256_hex(s: str) -> str:
    if not isinstance(s, str) or not re.fullmatch(r"[0-9a-f]{64}", s):
        raise ValueError("control_plane_binding_sha256 must be lowercase 64-hex")
    return s


def verified_token_account(obj: dict, *, require_treasury: bool) -> dict:
    required = ["token_account", "mint", "owner_wallet", "owner_program", "decimals", "onchain_verified"]
    if any(k not in obj for k in required):
        raise ValueError("verified token-account metadata incomplete")
    pubkey(obj["token_account"]); pubkey(obj["owner_wallet"])
    if obj["mint"] != MINT:
        raise ValueError("token account mint mismatch")
    if obj["owner_program"] != TOKEN_PROGRAM:
        raise ValueError("token account program mismatch")
    if int(obj["decimals"]) != DECIMALS:
        raise ValueError("token decimals mismatch")
    if obj["onchain_verified"] is not True:
        raise ValueError("token account must be verified on-chain")
    if require_treasury and obj.get("treasury_controlled") is not True:
        raise ValueError("source account is not verified treasury-controlled")
    if require_treasury and not obj.get("control_evidence_sha256"):
        raise ValueError("treasury control evidence missing")
    if obj.get("control_evidence_sha256"):
        sha256_hex(obj["control_evidence_sha256"])
    return obj


def build(req: dict) -> dict:
    forbidden = {"seed", "seed_phrase", "private_key", "secret_key", "signature", "signed_transaction"}
    if any(k.lower() in forbidden for k in req):
        raise ValueError("secret/signature fields forbidden")
    if req.get("mint") != MINT:
        raise ValueError("canonical mint mismatch")
    op = req.get("operation")
    if op not in OPS:
        raise ValueError("unsupported operation")
    binding = sha256_hex(req.get("control_plane_binding_sha256", ""))
    amount = int(req.get("amount_raw", 0))
    if amount <= 0 or amount > 2**64 - 1:
        raise ValueError("amount_raw must fit positive u64")
    if int(req.get("decimals", -1)) != DECIMALS:
        raise ValueError("decimals mismatch")

    source = verified_token_account(req.get("source") or {}, require_treasury=True)
    authority = pubkey(req.get("authority_pubkey", ""))
    if authority != source["owner_wallet"]:
        raise ValueError("authority does not match verified source owner")

    data = bytes([OPS[op]]) + struct.pack("<Q", amount) + bytes([DECIMALS])
    metas = [
        {"pubkey": source["token_account"], "is_writable": True, "is_signer": False, "role": "source"},
        {"pubkey": MINT, "is_writable": op == "burn_checked", "is_signer": False, "role": "mint"},
    ]
    if op == "transfer_checked":
        dest = verified_token_account(req.get("destination") or {}, require_treasury=False)
        metas.append({"pubkey": dest["token_account"], "is_writable": True, "is_signer": False, "role": "destination"})
    metas.append({"pubkey": authority, "is_writable": False, "is_signer": False, "role": "authority_external_multisig"})

    core = {
        "version": 1,
        "network": "solana-mainnet-beta",
        "mint": MINT,
        "token_program": TOKEN_PROGRAM,
        "operation": op,
        "opcode": OPS[op],
        "amount_raw": str(amount),
        "decimals": DECIMALS,
        "instruction_data_hex": data.hex(),
        "account_metas": metas,
        "control_plane_binding_sha256": binding,
        "authority_model": "external_multisig_unresolved",
        "ready_for_transaction_serialization": False,
        "ready_for_simulation": False,
        "ready_for_signing": False,
        "broadcast_allowed": False,
        "financial_effect": False,
    }
    digest = hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    core["instruction_envelope_sha256"] = digest
    return core


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: spl_instruction_compiler.py INPUT.json OUTPUT.json")
    req = json.load(open(sys.argv[1]))
    out = build(req)
    with open(sys.argv[2], "w") as f:
        json.dump(out, f, indent=2, sort_keys=True); f.write("\n")
    print("THF_TOKENOPS_SPL_COMPILER=PASS")
    print("TRANSACTION_SERIALIZED=FALSE")
    print("TRANSACTION_SIGNED=FALSE")
    print("TRANSACTION_SUBMITTED=FALSE")
    print("FINANCIAL_EFFECT=FALSE")
    print("WAVE_UNTOUCHED=TRUE")

if __name__ == "__main__":
    main()
