#!/usr/bin/env python3
"""Read-only Solana mainnet verifier for candidate THF token accounts.

No signing, transaction creation, simulation, submission, authority change, transfer,
or burn is performed. Treasury control is never inferred from balance/rank; it must
be supplied through an explicit owner allowlist plus external evidence hash.
"""
from __future__ import annotations
import hashlib, json, re, sys, urllib.request

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
DECIMALS = 8
DEFAULT_RPC = "https://api.mainnet-beta.solana.com"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN = {"seed", "seed_phrase", "private_key", "secret_key", "signature", "signed_transaction"}


def _clean_input(obj: dict) -> None:
    for k in obj:
        if k.lower() in FORBIDDEN:
            raise ValueError("secret/signature fields forbidden")


def _rpc(url: str, method: str, params: list) -> dict:
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}, separators=(",", ":")).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=45) as r:
        out = json.load(r)
    if out.get("error"):
        raise RuntimeError(f"RPC error: {out['error']}")
    return out["result"]


def verify_account(candidate: dict, account_value: dict | None) -> dict:
    _clean_input(candidate)
    address = candidate.get("token_account")
    if not isinstance(address, str) or not address:
        raise ValueError("token_account required")
    if not account_value:
        raise ValueError("token account not found on-chain")
    if account_value.get("owner") != TOKEN_PROGRAM:
        raise ValueError("token account program mismatch")
    parsed = ((account_value.get("data") or {}).get("parsed") or {})
    if parsed.get("type") != "account":
        raise ValueError("not an SPL token account")
    info = parsed.get("info") or {}
    token_amount = info.get("tokenAmount") or {}
    if info.get("mint") != MINT:
        raise ValueError("token account mint mismatch")
    if int(token_amount.get("decimals", -1)) != DECIMALS:
        raise ValueError("token decimals mismatch")
    owner_wallet = info.get("owner")
    if not isinstance(owner_wallet, str) or not owner_wallet:
        raise ValueError("token-account owner missing")

    allow = candidate.get("treasury_owner_allowlist") or []
    if not isinstance(allow, list) or any(not isinstance(x, str) for x in allow):
        raise ValueError("treasury_owner_allowlist must be a string list")
    treasury_controlled = owner_wallet in allow
    evidence = candidate.get("control_evidence_sha256")
    if treasury_controlled:
        if not isinstance(evidence, str) or not HEX64.fullmatch(evidence):
            raise ValueError("treasury-controlled account requires control evidence sha256")
    elif evidence is not None:
        raise ValueError("control evidence supplied for owner not in allowlist")

    core = {
        "version": 1,
        "network": "solana-mainnet-beta",
        "token_account": address,
        "mint": MINT,
        "owner_wallet": owner_wallet,
        "owner_program": TOKEN_PROGRAM,
        "decimals": DECIMALS,
        "amount_raw": str(token_amount.get("amount", "0")),
        "state": info.get("state"),
        "onchain_verified": True,
        "treasury_controlled": treasury_controlled,
        "control_evidence_sha256": evidence if treasury_controlled else None,
        "verification_policy": "explicit_owner_allowlist_plus_external_evidence",
        "balance_or_rank_used_as_control_evidence": False,
        "transaction_created": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "financial_effect": False,
    }
    core["verification_sha256"] = hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return core


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: mainnet_token_account_verifier.py INPUT.json OUTPUT.json")
    req = json.load(open(sys.argv[1]))
    _clean_input(req)
    if req.get("mint", MINT) != MINT:
        raise ValueError("canonical mint mismatch")
    rpc_url = req.get("rpc_url") or DEFAULT_RPC
    candidates = req.get("candidates") or []
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("at least one candidate token account is required")
    verified = []
    for c in candidates:
        result = _rpc(rpc_url, "getAccountInfo", [c["token_account"], {"encoding":"jsonParsed","commitment":"confirmed"}])
        verified.append(verify_account(c, result.get("value")))
    out = {
        "mint": MINT,
        "network": "solana-mainnet-beta",
        "accounts": verified,
        "transaction_created": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "private_key_used": False,
        "wave_untouched": True,
    }
    out["evidence_sha256"] = hashlib.sha256(json.dumps(out, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    with open(sys.argv[2], "w") as f:
        json.dump(out, f, indent=2, sort_keys=True); f.write("\n")
    print("THF_TOKENOPS_TOKEN_ACCOUNT_VERIFIER=PASS")
    print("TRANSACTION_CREATED=FALSE")
    print("TRANSACTION_SIGNED=FALSE")
    print("TRANSACTION_SUBMITTED=FALSE")
    print("PRIVATE_KEY_USED=FALSE")
    print("WAVE_UNTOUCHED=TRUE")

if __name__ == "__main__":
    main()
