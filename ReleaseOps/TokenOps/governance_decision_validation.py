#!/usr/bin/env python3
"""Review-only validation for THF TokenOps governance decision inputs.

This module validates the shape and integrity of public/governance evidence supplied
against immutable decision-packet templates. It does not decide economic values,
verify that a governance body actually approved an artifact, create transaction or
instruction bytes, request signatures, or authorize any financial execution.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Mapping, Tuple

SCHEMA = "thf-tokenops-governance-decision-evidence-review/v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BASE58_INDEX = {c: i for i, c in enumerate(BASE58_ALPHABET)}
FORBIDDEN_KEYS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "transaction_bytes", "instruction_bytes",
    "raw_transaction", "serialized_transaction",
}


def _sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


def _base58_decode(value: str) -> bytes:
    if not value or any(c not in BASE58_INDEX for c in value):
        raise ValueError("invalid base58")
    number = 0
    for char in value:
        number = number * 58 + BASE58_INDEX[char]
    body = number.to_bytes((number.bit_length() + 7) // 8, "big") if number else b""
    leading_zeroes = len(value) - len(value.lstrip("1"))
    return b"\x00" * leading_zeroes + body


def _is_pubkey(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return len(_base58_decode(value)) == 32
    except ValueError:
        return False


def _parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None


def _walk_forbidden_keys(value: Any, path: str = "$") -> List[str]:
    errors: List[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_").replace(" ", "_")
            child_path = f"{path}.{key}"
            if normalized in FORBIDDEN_KEYS:
                errors.append(f"forbidden_field:{child_path}")
            errors.extend(_walk_forbidden_keys(child, child_path))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            errors.extend(_walk_forbidden_keys(child, f"{path}[{idx}]"))
    return errors


def _validate_field(name: str, value: Any) -> List[str]:
    errors: List[str] = []
    if name.endswith("_sha256"):
        if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
            errors.append(f"invalid_sha256:{name}")
        return errors

    if name in {"per_user_cap_raw", "epoch_budget_cap_raw", "reward_budget_cap_raw"}:
        if type(value) is not int or value <= 0:
            errors.append(f"invalid_positive_integer:{name}")
        return errors

    if name == "balance_raw":
        if type(value) is not int or value < 0:
            errors.append("invalid_nonnegative_integer:balance_raw")
        return errors

    if name == "observed_slot":
        if type(value) is not int or value <= 0:
            errors.append("invalid_positive_integer:observed_slot")
        return errors

    if name == "minimum_approvals":
        if type(value) is not int or value <= 0:
            errors.append("invalid_positive_integer:minimum_approvals")
        return errors

    if name in {"token_account", "owner_pubkey"}:
        if not _is_pubkey(value):
            errors.append(f"invalid_solana_pubkey:{name}")
        return errors

    if name == "public_token_accounts":
        if not isinstance(value, list) or not value:
            errors.append("public_token_accounts_must_be_nonempty_list")
        elif any(not _is_pubkey(v) for v in value):
            errors.append("invalid_solana_pubkey:public_token_accounts")
        elif len(set(value)) != len(value):
            errors.append("duplicate_public_token_accounts")
        return errors

    if name == "multisig_or_user_controlled":
        allowed = {True, "multisig", "external_multisig", "user_controlled", "multisig_or_user_controlled"}
        if value not in allowed:
            errors.append("invalid_multisig_or_user_controlled")
        return errors

    if name in {
        "delivery_model", "denomination", "method", "signer_model", "ci_identity_model",
        "authority_model",
    }:
        if not isinstance(value, str) or not value.strip():
            errors.append(f"invalid_nonempty_string:{name}")
        return errors

    if name in {"valid_from_utc", "valid_until_utc"}:
        if _parse_utc(value) is None:
            errors.append(f"invalid_utc_timestamp:{name}")
        return errors

    if value is None:
        errors.append(f"missing_value:{name}")
    return errors


def _validate_packet_input(packet: Dict[str, Any], supplied: Any) -> Tuple[str, List[str], List[str]]:
    required = list(packet.get("required_fields", []))
    if supplied is None:
        return "INPUTS_MISSING", sorted(required), []
    if not isinstance(supplied, Mapping):
        return "INVALID_FAIL_CLOSED", [], ["decision_input_must_be_object"]

    supplied_keys = set(str(k) for k in supplied.keys())
    required_keys = set(str(k) for k in required)
    missing = sorted(required_keys - supplied_keys)
    extra = sorted(supplied_keys - required_keys)
    errors: List[str] = []
    if extra:
        errors.extend(f"unexpected_field:{name}" for name in extra)
    errors.extend(_walk_forbidden_keys(supplied))

    for field in sorted(required_keys & supplied_keys):
        value = supplied[field]
        if value is None:
            missing.append(field)
        else:
            errors.extend(_validate_field(field, value))

    if "valid_from_utc" in supplied and "valid_until_utc" in supplied:
        start = _parse_utc(supplied.get("valid_from_utc"))
        end = _parse_utc(supplied.get("valid_until_utc"))
        if start is not None and end is not None and end <= start:
            errors.append("invalid_validity_window:not_strictly_increasing")

    if errors:
        return "INVALID_FAIL_CLOSED", sorted(set(missing)), sorted(set(errors))
    if missing:
        return "INPUTS_MISSING", sorted(set(missing)), []
    return "REVIEWABLE_EVIDENCE_COMPLETE", [], []


def build_decision_evidence_review(
    decision_bundle: Dict[str, Any],
    decision_inputs: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Validate decision inputs without converting evidence into authorization."""
    decision_inputs = decision_inputs or {}
    packet_reviews: List[Dict[str, Any]] = []
    known_blockers = {str(p.get("blocker")) for p in decision_bundle.get("packets", [])}
    unknown_input_blockers = sorted(set(str(k) for k in decision_inputs.keys()) - known_blockers)

    for packet in decision_bundle.get("packets", []):
        blocker = str(packet.get("blocker"))
        supplied = decision_inputs.get(blocker)
        status, missing, errors = _validate_packet_input(packet, supplied)
        review = {
            "blocker": blocker,
            "packet_sha256": packet.get("packet_sha256"),
            "status": status,
            "required_fields": list(packet.get("required_fields", [])),
            "missing_fields": missing,
            "validation_errors": errors,
            "evidence_shape_validated": status == "REVIEWABLE_EVIDENCE_COMPLETE",
            "governance_evidence_authenticity_verified": False,
            "execution_authorized": False,
            "signer_action_now": "NONE",
        }
        review["review_sha256"] = _sha256(review)
        packet_reviews.append(review)

    invalid_count = sum(r["status"] == "INVALID_FAIL_CLOSED" for r in packet_reviews)
    complete_count = sum(r["status"] == "REVIEWABLE_EVIDENCE_COMPLETE" for r in packet_reviews)
    missing_count = sum(r["status"] == "INPUTS_MISSING" for r in packet_reviews)

    if unknown_input_blockers or invalid_count:
        status = "FAIL_CLOSED_INVALID"
    elif packet_reviews and complete_count == len(packet_reviews):
        status = "REVIEWABLE_EVIDENCE_COMPLETE_NOT_AUTHORIZED"
    elif packet_reviews:
        status = "REVIEW_INPUTS_REQUIRED"
    else:
        status = "NO_DECISION_PACKETS"

    result = {
        "schema": SCHEMA,
        "network": decision_bundle.get("network"),
        "mint": decision_bundle.get("mint"),
        "decision_packet_root_sha256": decision_bundle.get("decision_packet_root_sha256"),
        "status": status,
        "packet_count": len(packet_reviews),
        "reviewable_evidence_complete_count": complete_count,
        "inputs_missing_count": missing_count,
        "invalid_count": invalid_count,
        "unknown_input_blockers": unknown_input_blockers,
        "packet_reviews": packet_reviews,
        "important_semantics": {
            "sha256_presence_is_not_governance_approval": True,
            "shape_validation_is_not_authenticity_verification": True,
            "complete_review_evidence_is_not_execution_authorization": True,
        },
        "signer_action_now": "NONE",
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
    result["decision_evidence_review_sha256"] = _sha256(result)
    return result


def validate_decision_evidence_review(review: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if review.get("signer_action_now") != "NONE":
        errors.append("signer_action_must_be_none")
    for flag in (
        "execution_authorized", "transaction_bytes_created", "instruction_bytes_created",
        "signed", "submitted", "broadcast", "financial_effect", "private_key_required", "wave_touched",
    ):
        if review.get(flag) is not False:
            errors.append(f"unsafe_review_flag:{flag}")
    semantics = dict(review.get("important_semantics", {}))
    for key in (
        "sha256_presence_is_not_governance_approval",
        "shape_validation_is_not_authenticity_verification",
        "complete_review_evidence_is_not_execution_authorization",
    ):
        if semantics.get(key) is not True:
            errors.append(f"missing_safety_semantic:{key}")
    errors.extend(_walk_forbidden_keys(review))
    return sorted(set(errors))
