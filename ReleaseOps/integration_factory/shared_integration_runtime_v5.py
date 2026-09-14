from __future__ import annotations

from hashlib import sha256
import re
import time
from typing import Any, Iterable, Mapping

from shared_integration_contracts import PRODUCTS, ALLOWED_HEALTH_METRICS, ContractError, validate_email_address


PUBLIC_AUTH_METHODS = {"google", "passkey", "password", "email_code", "guest"}
SUPPORTED_HEALTH_PROVIDERS = {"health_connect", "samsung_health_data_sdk"}
SUPPORTED_LOCALES = {
    "ar", "en", "fr", "de", "es", "it", "pt", "tr", "ru", "zh", "hi", "ko", "ja",
    "id", "ms", "ur", "fa", "bn", "sw", "fil",
}


def identity_link_plan(
    *, authenticated_subject: str, current_provider: str, new_provider: str,
    new_provider_subject: str, provider_credential_verified: bool,
    existing_owner_subject: str = "",
) -> dict[str, Any]:
    """Server-side account-linking contract that fails closed on account collisions.

    Linking never trusts client-side email equality and never silently merges two existing
    THF identities. A verified provider credential is required before a new provider subject
    can be attached to the authenticated THF subject.
    """
    subject = authenticated_subject.strip()
    current_provider = current_provider.strip().lower()
    new_provider = new_provider.strip().lower()
    provider_subject = new_provider_subject.strip()
    owner = existing_owner_subject.strip()
    if not subject:
        raise ContractError("authenticated_subject_required")
    if current_provider not in PUBLIC_AUTH_METHODS - {"guest"}:
        raise ContractError("current_provider_invalid")
    if new_provider not in PUBLIC_AUTH_METHODS - {"guest"}:
        raise ContractError("new_provider_invalid")
    if new_provider == current_provider:
        raise ContractError("provider_already_primary")
    if not provider_subject:
        raise ContractError("new_provider_subject_required")
    if provider_credential_verified is not True:
        raise ContractError("provider_credential_verification_required")
    if owner and owner != subject:
        raise ContractError("identity_collision_manual_recovery_required")
    return {
        "subject": subject,
        "new_provider": new_provider,
        "new_provider_subject_hash": sha256(provider_subject.encode()).hexdigest(),
        "credential_verified": True,
        "email_equality_is_link_authority": False,
        "silent_cross_account_merge_allowed": False,
        "server_atomic_link_required": True,
        "audit_event_required": True,
    }


def guest_upgrade_plan(
    *, guest_session_id: str, authenticated_subject: str,
    guest_progress_refs: Iterable[str], server_ownership_verified: bool,
) -> dict[str, Any]:
    guest_id = guest_session_id.strip()
    subject = authenticated_subject.strip()
    refs = sorted({str(x).strip() for x in guest_progress_refs if str(x).strip()})
    if len(guest_id) < 16 or not subject:
        raise ContractError("guest_upgrade_identity_invalid")
    if server_ownership_verified is not True:
        raise ContractError("guest_progress_server_ownership_required")
    if len(refs) > 128:
        raise ContractError("guest_progress_reference_limit")
    return {
        "guest_session_id_hash": sha256(guest_id.encode()).hexdigest(),
        "authenticated_subject": subject,
        "progress_refs": refs,
        "server_ownership_verified": True,
        "economy_balance_client_merge_allowed": False,
        "ranked_state_client_merge_allowed": False,
        "atomic_migration_required": True,
        "guest_session_revocation_required": True,
    }


def health_provider_capability_plan(
    *, provider: str, installed: bool, authorized: bool,
    available_metrics: Iterable[str], requested_metrics: Iterable[str],
) -> dict[str, Any]:
    provider = provider.strip().lower()
    if provider not in SUPPORTED_HEALTH_PROVIDERS:
        raise ContractError("health_provider_unsupported")
    requested = sorted({str(x).strip() for x in requested_metrics if str(x).strip()})
    available = sorted({str(x).strip() for x in available_metrics if str(x).strip()})
    if any(x not in ALLOWED_HEALTH_METRICS for x in requested + available):
        raise ContractError("health_metric_unsupported")
    usable = bool(installed and authorized)
    readable = sorted(set(requested).intersection(available)) if usable else []
    missing = sorted(set(requested).difference(readable))
    return {
        "provider": provider,
        "installed": bool(installed),
        "authorized": bool(authorized),
        "usable": usable,
        "readable_metrics": readable,
        "missing_metrics": missing,
        "provider_absence_is_fatal": False,
        "fallback_to_manual_health_claims_allowed": False,
        "permission_prompt_required": bool(installed and not authorized),
    }


def normalized_health_record(
    *, provider: str, metric: str, source_app_id: str, source_record_id: str,
    start_ms: int, end_ms: int, value_fingerprint: str,
) -> dict[str, Any]:
    provider = provider.strip().lower()
    metric = metric.strip()
    source_app_id = source_app_id.strip()
    source_record_id = source_record_id.strip()
    value_fingerprint = value_fingerprint.strip().lower()
    if provider not in SUPPORTED_HEALTH_PROVIDERS:
        raise ContractError("health_provider_unsupported")
    if metric not in ALLOWED_HEALTH_METRICS:
        raise ContractError("health_metric_unsupported")
    if not source_app_id or not source_record_id:
        raise ContractError("health_record_provenance_required")
    if start_ms < 0 or end_ms < start_ms:
        raise ContractError("health_record_time_invalid")
    if not re.fullmatch(r"[0-9a-f]{64}", value_fingerprint):
        raise ContractError("health_value_fingerprint_invalid")
    canonical = "|".join((provider, metric, source_app_id, source_record_id, str(start_ms), str(end_ms), value_fingerprint))
    return {
        "provider": provider,
        "metric": metric,
        "source_app_id": source_app_id,
        "source_record_id_hash": sha256(source_record_id.encode()).hexdigest(),
        "start_ms": int(start_ms),
        "end_ms": int(end_ms),
        "dedup_key": sha256(canonical.encode()).hexdigest(),
        "provenance_complete": True,
        "raw_payload_logging_allowed": False,
        "reward_authority": False,
    }


def user_preference_sync(
    *, locale: str, data_saver: bool, reduce_motion: bool,
    high_contrast: bool, rtl_override: bool | None = None,
) -> dict[str, Any]:
    locale = locale.strip().lower().replace("_", "-")
    base = locale.split("-", 1)[0]
    if base not in SUPPORTED_LOCALES:
        raise ContractError("locale_unsupported")
    system_rtl = base in {"ar", "fa", "ur"}
    if rtl_override is not None and bool(rtl_override) != system_rtl:
        raise ContractError("rtl_override_conflicts_with_locale")
    return {
        "locale": locale,
        "base_locale": base,
        "rtl": system_rtl,
        "data_saver": bool(data_saver),
        "reduce_motion": bool(reduce_motion),
        "high_contrast": bool(high_contrast),
        "cross_app_sync_allowed": True,
        "product_specific_visuals_preserved": True,
    }


def account_recovery_channel(*, email: str, verified: bool, operator_account: bool) -> dict[str, Any]:
    email = validate_email_address(email)
    if verified is not True:
        raise ContractError("recovery_email_must_be_verified")
    return {
        "email": email,
        "verified": True,
        "operator_account": bool(operator_account),
        "single_channel_operator_recovery_allowed": False if operator_account else True,
        "server_rate_limit_required": True,
        "recovery_event_audit_required": True,
    }


def runtime_v5_snapshot() -> dict[str, Any]:
    return {
        "schema": "thf.shared.integration.runtime.v5",
        "identity_linking": {
            "verified_provider_credential_required": True,
            "silent_cross_account_merge_allowed": False,
            "email_equality_is_link_authority": False,
            "server_atomic_link_required": True,
        },
        "guest_upgrade": {
            "server_ownership_required": True,
            "client_economy_merge_allowed": False,
            "client_ranked_merge_allowed": False,
        },
        "health_provider_negotiation": {
            "primary": "health_connect",
            "optional_adapter": "samsung_health_data_sdk",
            "provider_absence_is_fatal": False,
            "manual_claim_fallback_allowed": False,
        },
        "health_dedup": {
            "provider_and_source_bound": True,
            "deterministic_dedup_key": True,
            "raw_payload_logging_allowed": False,
            "reward_authority": False,
        },
        "preferences": {
            "supported_locale_count": len(SUPPORTED_LOCALES),
            "rtl_locales": ["ar", "fa", "ur"],
            "data_saver": True,
            "reduce_motion": True,
            "high_contrast": True,
        },
        "operator_recovery": {
            "verified_recovery_email_required": True,
            "single_channel_operator_recovery_allowed": False,
        },
        "release_truth": {
            "google_oauth_console_configured": False,
            "durable_identity_link_store_bound": False,
            "durable_guest_migration_store_bound": False,
            "health_connect_provider_runtime_bound": False,
            "samsung_partner_registration_verified": False,
            "physical_device_pass": False,
            "final_or_play_ready": False,
        },
    }
