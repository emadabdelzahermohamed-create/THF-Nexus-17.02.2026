#!/usr/bin/env python3
"""Bind validated registry-driven treasury verification into the SPL compiler gate.

Offline/fail-closed. No transaction creation, serialization, signing, simulation,
submission, broadcast, or financial effect occurs here.
"""
from __future__ import annotations
import hashlib, json, re
from verifier_compiler_binding import build as build_compiler_binding

HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN = {"seed","seed_phrase","mnemonic","private_key","secret_key","keypair","signature","signed_transaction"}


def sha(v: dict) -> str:
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def reject(v):
    if isinstance(v, dict):
        for k, x in v.items():
            if str(k).lower().replace("-","_") in FORBIDDEN:
                raise ValueError("secret/signature fields forbidden")
            reject(x)
    elif isinstance(v, list):
        for x in v: reject(x)


def hex64(v, name):
    if not isinstance(v, str) or not HEX64.fullmatch(v):
        raise ValueError(f"{name} must be lowercase 64-hex")
    return v


def validate_registry_driven(record: dict) -> dict:
    reject(record)
    supplied = hex64(record.get("registry_driven_verification_sha256"), "registry_driven_verification_sha256")
    core = dict(record); core.pop("registry_driven_verification_sha256", None)
    if sha(core) != supplied:
        raise ValueError("registry-driven verification digest mismatch")
    if core.get("candidate_source") != "validated_treasury_control_registry_only":
        raise ValueError("source must derive from validated treasury registry")
    if core.get("caller_supplied_allowlist") is not False or core.get("caller_supplied_control_evidence") is not False:
        raise ValueError("caller-supplied treasury control metadata forbidden")
    for k in ("transaction_created","transaction_signed","transaction_submitted","ready_for_simulation","ready_for_signing","broadcast_allowed","financial_effect"):
        if core.get(k) is not False: raise ValueError(f"unsafe registry-driven flag: {k}")
    verified = core.get("verified_account") or {}
    if verified.get("verification_sha256") != core.get("verification_sha256"):
        raise ValueError("embedded verification digest mismatch")
    if verified.get("owner_wallet") != core.get("owner_wallet") or verified.get("token_account") != core.get("token_account"):
        raise ValueError("embedded verified identity mismatch")
    if verified.get("control_evidence_sha256") != core.get("control_evidence_sha256"):
        raise ValueError("embedded control evidence mismatch")
    hex64(core.get("registry_snapshot_sha256"), "registry_snapshot_sha256")
    hex64(core.get("control_evidence_sha256"), "control_evidence_sha256")
    return record


def build(req: dict) -> dict:
    reject(req)
    source = validate_registry_driven(req.get("registry_driven_source") or {})
    downstream = build_compiler_binding({
        "mint": source["mint"],
        "operation": req.get("operation"),
        "amount_raw": req.get("amount_raw"),
        "control_plane_binding_sha256": req.get("control_plane_binding_sha256"),
        "source_verification": source["verified_account"],
        "destination_verification": req.get("destination_verification"),
        "authority_pubkey": source["owner_wallet"],
    })
    core = {
        "version": 1,
        "network": source["network"],
        "mint": source["mint"],
        "operation": downstream["operation"],
        "registry_snapshot_sha256": source["registry_snapshot_sha256"],
        "registry_driven_verification_sha256": source["registry_driven_verification_sha256"],
        "control_evidence_sha256": source["control_evidence_sha256"],
        "verification_sha256": source["verification_sha256"],
        "verifier_compiler_binding_sha256": downstream["verifier_compiler_binding_sha256"],
        "registry_source_required": True,
        "caller_supplied_treasury_metadata_allowed": False,
        "ready_for_compilation": True,
        "ready_for_transaction_serialization": False,
        "ready_for_simulation": False,
        "ready_for_signing": False,
        "broadcast_allowed": False,
        "financial_effect": False,
    }
    core["registry_compiler_binding_sha256"] = sha(core)
    return core
