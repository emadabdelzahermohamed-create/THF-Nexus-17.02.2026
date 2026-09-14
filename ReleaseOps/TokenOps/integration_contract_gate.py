#!/usr/bin/env python3
"""Fail-closed Vault/Forge/Core integration contract gate for THF TokenOps.

This module validates public, non-secret integration declarations only. It never
constructs Solana instructions/transactions, signs, submits, broadcasts, or
changes financial state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Tuple

NETWORK = "solana-mainnet-beta"
MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
DECIMALS = 8
SERVICES = ("Vault", "Forge", "Core")
AMOUNT_UNIT = "THF_RAW"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signatures", "signed_transaction", "raw_transaction",
    "serialized_transaction", "transaction_bytes", "instruction_bytes",
    "access_token", "refresh_token", "service_account_key",
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha256(value: Any) -> str:
    data = value if isinstance(value, bytes) else canonical_json(value)
    return hashlib.sha256(data).hexdigest()


def scan_sensitive(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_KEYS:
                raise ValueError(f"forbidden sensitive/executable field at {path}.{key}")
            scan_sensitive(child, f"{path}.{key}")
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            scan_sensitive(child, f"{path}[{idx}]")


def _as_set(value: Any) -> Set[str]:
    if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
        return set()
    return set(value)


def validate_contracts(obj: Dict[str, Any]) -> Dict[str, Any]:
    scan_sensitive(obj)
    errors: List[str] = []
    warnings: List[str] = []

    if obj.get("schema") != "thf-tokenops-integration-contracts/v1.2":
        errors.append("schema_mismatch")

    identity = obj.get("canonical_identity") or {}
    expected_identity = {
        "network": NETWORK,
        "mint": MINT,
        "token_program": TOKEN_PROGRAM,
        "decimals": DECIMALS,
        "amount_unit": AMOUNT_UNIT,
    }
    for key, expected in expected_identity.items():
        if identity.get(key) != expected:
            errors.append(f"canonical_identity:{key}_mismatch")

    envelope = obj.get("envelope_requirements") or {}
    required_fields = _as_set(envelope.get("required_fields"))
    must_require = {
        "schema", "contract_version", "network", "mint", "token_program", "decimals",
        "amount_unit", "evidence_sha256", "source_observed_at_utc", "source_slot",
        "idempotency_key", "expires_at_utc", "financial_effect", "signed", "broadcast",
    }
    missing_fields = sorted(must_require - required_fields)
    if missing_fields:
        errors.extend(f"envelope:missing_required_field:{x}" for x in missing_fields)
    if envelope.get("evidence_hash") != "sha256":
        errors.append("envelope:evidence_hash_must_be_sha256")
    if envelope.get("replay_protection") != "idempotency_key":
        errors.append("envelope:replay_protection_must_use_idempotency_key")
    max_age = envelope.get("max_evidence_age_seconds")
    if not isinstance(max_age, int) or not (1 <= max_age <= 3600):
        errors.append("envelope:max_evidence_age_seconds_out_of_range")
    if envelope.get("reject_expired") is not True:
        errors.append("envelope:reject_expired_must_be_true")
    if envelope.get("reject_duplicate_idempotency_key") is not True:
        errors.append("envelope:duplicate_idempotency_must_fail_closed")

    services = obj.get("services") or {}
    outputs_by_service: Dict[str, Set[str]] = {}
    inputs_by_service: Dict[str, Set[str]] = {}
    for service in SERVICES:
        contract = services.get(service)
        if not isinstance(contract, dict):
            errors.append(f"{service}:missing")
            continue
        for key, expected in (
            ("network", NETWORK), ("mint", MINT), ("token_program", TOKEN_PROGRAM),
            ("decimals", DECIMALS), ("amount_unit", AMOUNT_UNIT),
        ):
            if contract.get(key) != expected:
                errors.append(f"{service}:{key}_mismatch")
        if not isinstance(contract.get("contract_version"), str) or not contract["contract_version"]:
            errors.append(f"{service}:version_missing")
        for flag in ("may_sign", "may_broadcast", "accepts_private_key_material", "may_change_authorities"):
            if contract.get(flag) is not False:
                errors.append(f"{service}:{flag}_must_be_false")
        if contract.get("execution_model") != "review_only_non_broadcast":
            errors.append(f"{service}:execution_model_mismatch")
        inputs = _as_set(contract.get("allowed_inputs"))
        outputs = _as_set(contract.get("allowed_outputs"))
        if not outputs:
            errors.append(f"{service}:allowed_outputs_empty")
        outputs_by_service[service] = outputs
        inputs_by_service[service] = inputs

    allowed_routes: Set[Tuple[str, str, str]] = set()
    routes = obj.get("routes") or []
    if not isinstance(routes, list) or not routes:
        errors.append("routes:missing")
        routes = []
    for idx, route in enumerate(routes):
        if not isinstance(route, dict):
            errors.append(f"routes[{idx}]:invalid")
            continue
        source, target, message = route.get("from"), route.get("to"), route.get("message_type")
        if source not in SERVICES or target not in SERVICES or source == target:
            errors.append(f"routes[{idx}]:invalid_endpoints")
            continue
        if message not in outputs_by_service.get(source, set()):
            errors.append(f"routes[{idx}]:source_output_not_declared")
        if message not in inputs_by_service.get(target, set()):
            errors.append(f"routes[{idx}]:target_input_not_declared")
        key = (source, target, message)
        if key in allowed_routes:
            errors.append(f"routes[{idx}]:duplicate")
        allowed_routes.add(key)

    # Explicitly prohibit any contract path that delegates execution or signer custody.
    forbidden_message_fragments = ("private_key", "seed", "signed_transaction", "transaction_bytes", "instruction_bytes", "broadcast")
    for service, outputs in outputs_by_service.items():
        for message in outputs:
            if any(fragment in message.lower() for fragment in forbidden_message_fragments):
                errors.append(f"{service}:forbidden_output:{message}")

    governance = obj.get("governance") or {}
    if governance.get("contract_mutation") != "user_controlled_multisig_review_required":
        errors.append("governance:contract_mutation_policy_missing")
    if governance.get("automatic_activation") is not False:
        errors.append("governance:automatic_activation_must_be_false")
    if governance.get("financial_effect") is not False:
        errors.append("governance:financial_effect_must_be_false")

    status = "PASS_NON_BROADCAST" if not errors else "FAIL_CLOSED"
    result: Dict[str, Any] = {
        "schema": "thf-tokenops-integration-contract-gate/v1",
        "status": status,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "service_count": sum(1 for s in SERVICES if isinstance(services.get(s), dict)),
        "route_count": len(allowed_routes),
        "contracts_sha256": sha256(obj),
        "execution_authorized": False,
        "transaction_bytes_created": False,
        "instruction_bytes_created": False,
        "signed": False,
        "submitted": False,
        "broadcast": False,
        "financial_effect": False,
        "private_key_required": False,
        "wave_touched": False,
    }
    result["gate_sha256"] = sha256(result)
    return result


def validate_message_envelope(envelope: Dict[str, Any], contracts: Dict[str, Any], source: str, target: str, now_utc: str) -> Dict[str, Any]:
    """Validate a synthetic/review message envelope; never executes the message."""
    scan_sensitive(envelope)
    errors: List[str] = []
    gate = validate_contracts(contracts)
    if gate["status"] != "PASS_NON_BROADCAST":
        errors.append("contracts_not_valid")

    routes = {(r.get("from"), r.get("to"), r.get("message_type")) for r in contracts.get("routes", []) if isinstance(r, dict)}
    message_type = envelope.get("message_type")
    if (source, target, message_type) not in routes:
        errors.append("route_not_allowed")

    for key, expected in (("network", NETWORK), ("mint", MINT), ("token_program", TOKEN_PROGRAM), ("decimals", DECIMALS), ("amount_unit", AMOUNT_UNIT)):
        if envelope.get(key) != expected:
            errors.append(f"{key}_mismatch")
    if not SHA256_RE.fullmatch(str(envelope.get("evidence_sha256", ""))):
        errors.append("invalid_evidence_sha256")
    if not isinstance(envelope.get("source_slot"), int) or envelope["source_slot"] <= 0:
        errors.append("invalid_source_slot")
    if not isinstance(envelope.get("idempotency_key"), str) or len(envelope["idempotency_key"]) < 16:
        errors.append("invalid_idempotency_key")
    for flag in ("financial_effect", "signed", "broadcast"):
        if envelope.get(flag) is not False:
            errors.append(f"{flag}_must_be_false")

    def parse(ts: Any) -> datetime | None:
        if not isinstance(ts, str):
            return None
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)
        except ValueError:
            return None

    observed = parse(envelope.get("source_observed_at_utc"))
    expires = parse(envelope.get("expires_at_utc"))
    now = parse(now_utc)
    max_age = int((contracts.get("envelope_requirements") or {}).get("max_evidence_age_seconds", 0) or 0)
    if observed is None or expires is None or now is None:
        errors.append("invalid_timestamp")
    else:
        age = (now - observed).total_seconds()
        if age < 0 or age > max_age:
            errors.append("evidence_stale_or_future")
        if expires <= now:
            errors.append("envelope_expired")
        if expires <= observed:
            errors.append("expiry_not_after_observation")

    return {
        "status": "PASS_NON_BROADCAST" if not errors else "FAIL_CLOSED",
        "errors": sorted(set(errors)),
        "source": source,
        "target": target,
        "message_type": message_type,
        "envelope_sha256": sha256(envelope),
        "execution_authorized": False,
        "signed": False,
        "broadcast": False,
        "financial_effect": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contracts", default="ReleaseOps/TokenOps/integration_contracts.json")
    ap.add_argument("--out", default="out/tokenops-integration/integration-contract-gate.json")
    args = ap.parse_args()
    contracts = json.loads(pathlib.Path(args.contracts).read_text(encoding="utf-8"))
    result = validate_contracts(contracts)
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("INTEGRATION_CONTRACT_GATE=" + result["status"])
    print("INTEGRATION_CONTRACT_SHA256=" + result["contracts_sha256"])
    print("INTEGRATION_GATE_SHA256=" + result["gate_sha256"])
    print("INTEGRATION_SERVICE_COUNT=" + str(result["service_count"]))
    print("INTEGRATION_ROUTE_COUNT=" + str(result["route_count"]))
    if result["status"] != "PASS_NON_BROADCAST":
        print("INTEGRATION_ERRORS=" + ",".join(result["errors"]))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
