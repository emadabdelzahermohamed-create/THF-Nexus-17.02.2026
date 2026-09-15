from __future__ import annotations

from hashlib import sha256
import time
from typing import Any, Iterable, Mapping

from shared_integration_contracts import ContractError, PRODUCTS
from shared_integration_runtime_v5 import SUPPORTED_HEALTH_PROVIDERS


def _required(value: str, error: str) -> str:
    value = str(value).strip()
    if not value:
        raise ContractError(error)
    return value


def device_bound_session(*, subject: str, package_id: str, device_key_thumbprint: str, issued_at: int, expires_at: int, now: int | None = None) -> dict[str, Any]:
    now = int(time.time()) if now is None else int(now)
    subject = _required(subject, "subject_required")
    package_id = _required(package_id, "package_id_required")
    thumbprint = _required(device_key_thumbprint, "device_key_thumbprint_required")
    allowed_packages = {meta["package"] for meta in PRODUCTS.values()}
    if package_id not in allowed_packages:
        raise ContractError("package_id_not_registered")
    if issued_at > now + 60 or expires_at <= now or expires_at <= issued_at:
        raise ContractError("session_time_invalid")
    if expires_at - issued_at > 3600:
        raise ContractError("session_ttl_excessive")
    return {
        "subject_hash": sha256(subject.encode()).hexdigest(),
        "package_id": package_id,
        "device_key_thumbprint": thumbprint,
        "proof_of_possession_required": True,
        "client_role_claims_authoritative": False,
        "expires_at": expires_at,
    }


def health_consent_transition(*, provider: str, current_state: str, action: str, granted_metrics: Iterable[str] = (), now: int | None = None) -> dict[str, Any]:
    now = int(time.time()) if now is None else int(now)
    provider = provider.strip().lower()
    if provider not in SUPPORTED_HEALTH_PROVIDERS:
        raise ContractError("health_provider_unsupported")
    current_state = current_state.strip().lower()
    action = action.strip().lower()
    allowed = {
        ("unknown", "request"): "pending",
        ("pending", "grant"): "granted",
        ("pending", "deny"): "denied",
        ("granted", "revoke"): "revoked",
        ("denied", "request"): "pending",
        ("revoked", "request"): "pending",
    }
    next_state = allowed.get((current_state, action))
    if next_state is None:
        raise ContractError("health_consent_transition_invalid")
    metrics = sorted({str(x).strip() for x in granted_metrics if str(x).strip()}) if next_state == "granted" else []
    return {
        "provider": provider,
        "state": next_state,
        "granted_metrics": metrics,
        "effective_at": now,
        "background_read": False,
        "write_access": False,
        "sync_allowed": next_state == "granted",
    }


def provider_failover_plan(*, health_connect_available: bool, samsung_available: bool, consented_providers: Iterable[str]) -> dict[str, Any]:
    consented = {str(x).strip().lower() for x in consented_providers if str(x).strip()}
    candidates = []
    if health_connect_available and "health_connect" in consented:
        candidates.append("health_connect")
    if samsung_available and "samsung_health" in consented:
        candidates.append("samsung_health")
    return {
        "ordered_providers": candidates,
        "primary": candidates[0] if candidates else None,
        "graceful_absence": not candidates,
        "fabricate_health_data": False,
        "manual_activity_is_verified_evidence": False,
    }


def privileged_route_guard(*, product: str, session: Mapping[str, Any], device_proof_valid: bool, step_up_age_seconds: int) -> dict[str, Any]:
    if product not in {"admin", "publisher"}:
        raise ContractError("operator_product_required")
    if session.get("state") != "authenticated":
        raise ContractError("authenticated_session_required")
    roles = {str(x).lower() for x in session.get("server_roles", [])}
    required = "admin" if product == "admin" else "publisher"
    if required not in roles:
        raise ContractError("server_role_required")
    if device_proof_valid is not True:
        raise ContractError("device_proof_required")
    if step_up_age_seconds < 0 or step_up_age_seconds > 300:
        raise ContractError("fresh_step_up_required")
    return {"allowed": True, "ordinary_user_visibility": False, "server_role_authoritative": True, "device_proof_required": True}


def runtime_v7_snapshot() -> dict[str, Any]:
    return {
        "schema": "thf.shared.integration.runtime.v7",
        "sessions": {"device_bound": True, "max_access_ttl_seconds": 3600, "proof_of_possession": True},
        "health_consent": {"explicit_state_machine": True, "revocation_stops_sync": True, "background_read_default": False, "write_default": False},
        "health_failover": {"health_connect_primary": True, "samsung_optional": True, "graceful_absence": True, "fabrication": False},
        "operator_routes": {"ordinary_user_visibility": False, "server_role_authoritative": True, "device_proof_required": True, "step_up_max_age_seconds": 300},
        "package_ids": {name: meta["package"] for name, meta in PRODUCTS.items()},
        "release_truth": {"physical_device_pass": False, "final_or_play_ready": False},
    }
