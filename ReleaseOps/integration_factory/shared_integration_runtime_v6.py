from __future__ import annotations

from hashlib import sha256
import time
from typing import Any, Iterable, Mapping

from shared_integration_contracts import PRODUCTS, ALLOWED_HEALTH_METRICS, ContractError
from shared_integration_runtime_v4 import fresh_operator_authorization
from shared_integration_runtime_v5 import SUPPORTED_HEALTH_PROVIDERS, SUPPORTED_LOCALES


def consent_minimization_plan(*, provider: str, requested_metrics: Iterable[str], feature_metrics: Iterable[str]) -> dict[str, Any]:
    provider = provider.strip().lower()
    if provider not in SUPPORTED_HEALTH_PROVIDERS:
        raise ContractError("health_provider_unsupported")
    requested = sorted({str(x).strip() for x in requested_metrics if str(x).strip()})
    needed = sorted({str(x).strip() for x in feature_metrics if str(x).strip()})
    if any(x not in ALLOWED_HEALTH_METRICS for x in requested + needed):
        raise ContractError("health_metric_unsupported")
    excessive = sorted(set(requested).difference(needed))
    if excessive:
        raise ContractError("health_permission_not_minimized")
    return {"provider": provider, "metrics": requested, "least_privilege": True, "background_read_default": False, "write_default": False}


def health_export_view(*, records: Iterable[Mapping[str, Any]], subject: str) -> dict[str, Any]:
    subject = subject.strip()
    if not subject:
        raise ContractError("subject_required")
    safe = []
    for record in records:
        if not bool(record.get("provenance_complete")):
            raise ContractError("health_record_provenance_required")
        safe.append({k: record[k] for k in ("provider", "metric", "source_app_id", "source_record_id_hash", "start_ms", "end_ms", "dedup_key") if k in record})
    return {"subject_hash": sha256(subject.encode()).hexdigest(), "records": safe, "raw_provider_payload_exported": False, "portable_export": True}


def account_deletion_cascade(*, subject: str, recent_reauth: bool, linked_providers: Iterable[str], active_sessions: int) -> dict[str, Any]:
    subject = subject.strip()
    if not subject:
        raise ContractError("subject_required")
    if recent_reauth is not True:
        raise ContractError("recent_reauth_required")
    providers = sorted({str(x).strip().lower() for x in linked_providers if str(x).strip()})
    if active_sessions < 0:
        raise ContractError("active_session_count_invalid")
    return {
        "subject_hash": sha256(subject.encode()).hexdigest(),
        "linked_providers": providers,
        "revoke_all_sessions": True,
        "revoke_cross_app_handoffs": True,
        "delete_health_consent_receipts": True,
        "unlink_provider_credentials": True,
        "preserve_required_financial_audit_only": True,
        "client_side_delete_is_authority": False,
        "server_atomic_or_resumable_job_required": True,
    }


def operator_step_up(*, product: str, session: Mapping[str, Any], roles_issued_at: int, passkey_uv: bool, second_factor_verified: bool, now: int | None = None) -> dict[str, Any]:
    now = int(time.time()) if now is None else int(now)
    auth = fresh_operator_authorization(product=product, session=session, roles_issued_at=roles_issued_at, now=now)
    if product not in {"admin", "publisher"}:
        raise ContractError("operator_product_required")
    if passkey_uv is not True or second_factor_verified is not True:
        raise ContractError("operator_step_up_required")
    auth.update({"passkey_user_verification": True, "second_factor_verified": True, "step_up_max_age_seconds": 300, "sensitive_action_reauth_required": True})
    return auth


def cross_app_preference_payload(*, locale: str, data_saver: bool, reduce_motion: bool, high_contrast: bool) -> dict[str, Any]:
    locale = locale.strip().lower().replace("_", "-")
    base = locale.split("-", 1)[0]
    if base not in SUPPORTED_LOCALES:
        raise ContractError("locale_unsupported")
    return {
        "locale": locale,
        "rtl": base in {"ar", "fa", "ur"},
        "data_saver": bool(data_saver),
        "reduce_motion": bool(reduce_motion),
        "high_contrast": bool(high_contrast),
        "identity_fields_in_payload": False,
        "health_fields_in_payload": False,
        "economy_fields_in_payload": False,
    }


def runtime_v6_snapshot() -> dict[str, Any]:
    return {
        "schema": "thf.shared.integration.runtime.v6",
        "health_permissions": {"least_privilege": True, "background_read_default": False, "write_default": False},
        "health_export": {"portable": True, "raw_provider_payload_exported": False},
        "account_deletion": {"recent_reauth_required": True, "session_revoke": True, "handoff_revoke": True, "health_consent_delete": True, "client_delete_authority": False},
        "operator_step_up": {"passkey_uv_required": True, "second_factor_required": True, "max_age_seconds": 300},
        "preference_sync": {"identity_fields": False, "health_fields": False, "economy_fields": False},
        "package_ids": {name: meta["package"] for name, meta in PRODUCTS.items()},
        "release_truth": {
            "google_oauth_console_configured": False,
            "durable_identity_store_bound": False,
            "health_connect_physical_device_verified": False,
            "samsung_partner_registration_verified": False,
            "physical_device_pass": False,
            "final_or_play_ready": False,
        },
    }
