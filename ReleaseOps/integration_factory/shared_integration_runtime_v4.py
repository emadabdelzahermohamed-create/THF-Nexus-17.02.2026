from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re
import time
from typing import Any, Iterable, Mapping

from shared_integration_contracts import (
    PRODUCTS,
    ALLOWED_HEALTH_METRICS,
    HEALTH_PROVIDER_STATUS,
    ContractError,
    authorize_product_for_session,
    cross_app_handoff,
    health_permission_plan,
    motion_evidence_contract,
    validate_google_id_token_claims,
    validate_google_oauth_config,
)


def credential_manager_google_request(
    *, server_client_id: str, nonce: str, package_name: str, client_secret_present: bool = False
) -> dict[str, Any]:
    """Fail-closed Android Credential Manager / Sign in with Google request contract.

    This is intentionally configuration-only. OAuth console ownership and cryptographic
    token verification remain server/external boundaries.
    """
    if client_secret_present:
        raise ContractError("mobile_client_secret_forbidden")
    validate_google_oauth_config({"server_client_id": server_client_id, "redirect_scheme": "thf"})
    nonce = nonce.strip()
    if len(nonce) < 32:
        raise ContractError("google_nonce_too_short")
    packages = {str(meta["package"]) for meta in PRODUCTS.values()}
    if package_name not in packages:
        raise ContractError("google_package_not_registered")
    return {
        "server_client_id": server_client_id,
        "nonce_sha256": sha256(nonce.encode()).hexdigest(),
        "package_name": package_name,
        "credential_manager": True,
        "server_signature_verification_required": True,
        "server_nonce_verification_required": True,
        "mobile_client_secret_allowed": False,
    }


def validate_google_identity_v4(
    claims: Mapping[str, Any], *, expected_audience: str, expected_nonce: str,
    signature_verified: bool, now: int | None = None,
) -> dict[str, str]:
    identity = validate_google_id_token_claims(
        claims,
        expected_audience=expected_audience,
        signature_verified=signature_verified,
        now=now,
    )
    expected_nonce = expected_nonce.strip()
    if len(expected_nonce) < 32:
        raise ContractError("google_expected_nonce_too_short")
    token_nonce = str(claims.get("nonce", "")).strip()
    if token_nonce != expected_nonce:
        raise ContractError("google_nonce_mismatch")
    return identity


def session_token_lifecycle(
    *, session: Mapping[str, Any], access_expires_at: int, refresh_token_id: str,
    device_id: str, now: int | None = None,
) -> dict[str, Any]:
    now = int(time.time()) if now is None else int(now)
    if str(session.get("state", "")).strip().lower() != "authenticated":
        raise ContractError("authenticated_session_required")
    if not str(session.get("subject", "")).strip():
        raise ContractError("session_subject_required")
    if access_expires_at <= now or access_expires_at - now > 1800:
        raise ContractError("access_token_lifetime_invalid")
    refresh_token_id = refresh_token_id.strip()
    device_id = device_id.strip()
    if len(refresh_token_id) < 16 or len(device_id) < 8:
        raise ContractError("refresh_or_device_id_invalid")
    return {
        "subject": str(session["subject"]).strip(),
        "access_expires_at": int(access_expires_at),
        "refresh_token_id_hash": sha256(refresh_token_id.encode()).hexdigest(),
        "device_id_hash": sha256(device_id.encode()).hexdigest(),
        "refresh_rotation_required": True,
        "reuse_detection_required": True,
        "secure_storage_only": True,
        "server_revocation_required": True,
        "raw_refresh_token_logged": False,
    }


def fresh_operator_authorization(
    *, product: str, session: Mapping[str, Any], roles_issued_at: int, now: int | None = None,
) -> dict[str, Any]:
    now = int(time.time()) if now is None else int(now)
    authorize_product_for_session(product, session)
    if product in {"admin", "publisher"}:
        if roles_issued_at > now or now - roles_issued_at > 300:
            raise ContractError("fresh_server_role_claim_required")
    return {
        "product": product,
        "subject": str(session.get("subject", "")).strip(),
        "server_role_claim_fresh": True,
        "client_role_override_allowed": False,
    }


def package_bound_handoff(
    *, source: str, target: str, target_package: str, subject: str,
    nonce: str, expires_at: int, now: int | None = None,
) -> dict[str, Any]:
    handoff = cross_app_handoff(
        source=source, target=target, subject=subject, nonce=nonce,
        expires_at=expires_at, now=now,
    )
    expected_package = str(PRODUCTS[target]["package"])
    if target_package != expected_package:
        raise ContractError("handoff_target_package_mismatch")
    handoff.update({
        "target_package": expected_package,
        "audience_bound": True,
        "package_bound": True,
        "server_signature_must_cover_target_package": True,
    })
    return handoff


@dataclass(frozen=True)
class HealthConsentReceipt:
    subject: str
    provider: str
    metrics: tuple[str, ...]
    granted_at: int
    consent_id: str
    revoked_at: int | None = None

    def validate(self, *, now: int | None = None) -> "HealthConsentReceipt":
        now = int(time.time()) if now is None else int(now)
        if not self.subject.strip() or len(self.consent_id.strip()) < 16:
            raise ContractError("health_consent_identity_required")
        health_permission_plan(self.metrics, provider=self.provider)
        if self.granted_at <= 0 or self.granted_at > now:
            raise ContractError("health_consent_grant_time_invalid")
        if self.revoked_at is not None and self.revoked_at < self.granted_at:
            raise ContractError("health_consent_revoke_time_invalid")
        return self

    @property
    def active(self) -> bool:
        self.validate()
        return self.revoked_at is None

    @property
    def audit_view(self) -> dict[str, Any]:
        self.validate()
        return {
            "subject_hash": sha256(self.subject.strip().encode()).hexdigest(),
            "provider": self.provider,
            "metrics": sorted(set(self.metrics)),
            "granted_at": self.granted_at,
            "revoked_at": self.revoked_at,
            "consent_id_hash": sha256(self.consent_id.strip().encode()).hexdigest(),
            "raw_health_payload_present": False,
        }


def health_sync_window(
    *, receipt: HealthConsentReceipt, metric: str, start_ms: int, end_ms: int,
    opaque_cursor: str = "",
) -> dict[str, Any]:
    receipt.validate()
    if not receipt.active:
        raise ContractError("health_consent_revoked")
    if metric not in receipt.metrics or metric not in ALLOWED_HEALTH_METRICS:
        raise ContractError("health_metric_not_consented")
    if start_ms < 0 or end_ms <= start_ms:
        raise ContractError("health_sync_window_invalid")
    max_window_ms = 31 * 24 * 60 * 60 * 1000
    if end_ms - start_ms > max_window_ms:
        raise ContractError("health_sync_window_too_large")
    cursor = opaque_cursor.strip()
    if cursor and (len(cursor) < 16 or not re.fullmatch(r"[A-Za-z0-9._~-]+", cursor)):
        raise ContractError("health_sync_cursor_invalid")
    return {
        "provider": receipt.provider,
        "metric": metric,
        "start_ms": int(start_ms),
        "end_ms": int(end_ms),
        "opaque_cursor": cursor,
        "consent_id_hash": sha256(receipt.consent_id.encode()).hexdigest(),
        "dedup_required": True,
        "provenance_required": True,
        "client_reward_authority": False,
    }


def verified_motion_submission(
    *, subject: str, workout_id: str, source: str, repetitions: int,
    confidence: float, monotonic_ms: int, sensor_attested: bool,
    evidence_nonce: str, health_record_refs: Iterable[str] = (),
) -> dict[str, Any]:
    subject = subject.strip()
    workout_id = workout_id.strip()
    if not subject or not workout_id:
        raise ContractError("motion_subject_workout_required")
    evidence = motion_evidence_contract(
        source=source,
        repetitions=repetitions,
        confidence=confidence,
        monotonic_ms=monotonic_ms,
        sensor_attested=sensor_attested,
        evidence_nonce=evidence_nonce,
    )
    refs = sorted({str(x).strip() for x in health_record_refs if str(x).strip()})
    evidence.update({
        "subject_hash": sha256(subject.encode()).hexdigest(),
        "workout_id": workout_id,
        "health_record_refs": refs,
        "health_data_is_supporting_evidence_only": True,
        "manual_reward_override_allowed": False,
        "server_verdict_required": True,
    })
    return evidence


def product_brand_manifest(product: str) -> dict[str, Any]:
    if product not in PRODUCTS:
        raise ContractError("unknown_product")
    meta = PRODUCTS[product]
    return {
        "product": product,
        "legacy": meta["legacy"],
        "package": meta["package"],
        "display_name_en": meta["en"],
        "display_name_ar": meta["ar"],
        "adaptive_icon_required": True,
        "monochrome_icon_required": True,
        "store_icon_source_required": True,
        "package_id_change_allowed": False,
        "operator_listing_public": False if meta["visibility"] == "operator" else None,
    }


def runtime_v4_snapshot() -> dict[str, Any]:
    return {
        "schema": "thf.shared.integration.runtime.v4",
        "credential_manager": {
            "google_nonce_required": True,
            "server_signature_verification_required": True,
            "mobile_client_secret_allowed": False,
        },
        "session": {
            "max_access_token_lifetime_seconds": 1800,
            "refresh_rotation_required": True,
            "reuse_detection_required": True,
            "secure_storage_only": True,
        },
        "operator": {
            "fresh_server_role_claim_max_age_seconds": 300,
            "client_role_override_allowed": False,
        },
        "handoff": {
            "target_package_bound": True,
            "server_signature_covers_target_package": True,
        },
        "health": {
            "explicit_consent_receipt": True,
            "revocation_fail_closed": True,
            "max_sync_window_days": 31,
            "dedup_required": True,
            "provenance_required": True,
            "reward_authority": False,
        },
        "motion": {
            "server_verdict_required": True,
            "health_supporting_evidence_only": True,
            "manual_reward_override_allowed": False,
        },
        "release_truth": {
            "google_oauth_console_configured": False,
            "google_server_signature_verifier_bound": False,
            "durable_session_refresh_store_bound": False,
            "operator_role_issuer_bound": False,
            "health_consent_store_bound": False,
            "health_connect_physical_device_verified": False,
            "samsung_partner_registration_verified": False,
            "cross_app_handoff_server_signer_bound": False,
            "physical_device_pass": False,
            "final_or_play_ready": False,
        },
    }
