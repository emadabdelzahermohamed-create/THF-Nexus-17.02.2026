from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
import time
from typing import Any, Iterable, Mapping

GOOGLE_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}
PUBLIC_ROLES = {"user", "member", "guest"}
OPERATOR_ROLES = {"owner", "admin", "publisher", "moderator"}

PRODUCTS: dict[str, dict[str, Any]] = {
    "hub": {"legacy": "core", "package": "com.topherofit.thf.core", "en": "THF Hub", "ar": "مركز THF", "visibility": "public"},
    "fitness": {"legacy": "pulse", "package": "com.topherofit.thf.pulse", "en": "THF Fitness", "ar": "لياقة THF", "visibility": "public"},
    "market": {"legacy": "forge", "package": "com.topherofit.thf.forge", "en": "THF Market", "ar": "سوق THF", "visibility": "public"},
    "community": {"legacy": "echo", "package": "com.topherofit.thf.echo", "en": "THF Community", "ar": "مجتمع THF", "visibility": "public"},
    "learn": {"legacy": "codex", "package": "com.topherofit.thf.codex", "en": "THF Learn", "ar": "تعلّم THF", "visibility": "public"},
    "wallet": {"legacy": "vault", "package": "com.topherofit.thf.vault", "en": "THF Wallet", "ar": "محفظة THF", "visibility": "public"},
    "world": {"legacy": "terra", "package": "com.topherofit.thf.terra", "en": "THF World", "ar": "عالم THF", "visibility": "public"},
    "arena": {"legacy": "rift", "package": "com.topherofit.thf.rift", "en": "THF Arena", "ar": "ساحة THF", "visibility": "public"},
    "learn_games": {"legacy": "spark", "package": "com.topherofit.thf.spark", "en": "THF Learn Games", "ar": "ألعاب تعلم THF", "visibility": "public"},
    "motion_games": {"legacy": "rush", "package": "com.topherofit.thf.rush", "en": "THF Motion Games", "ar": "ألعاب حركة THF", "visibility": "public"},
    "publisher": {"legacy": "signal", "package": "com.topherofit.thf.signal", "en": "THF Publisher", "ar": "ناشر THF", "visibility": "operator", "required_roles": {"owner", "admin", "publisher"}},
    "admin": {"legacy": "command", "package": "com.topherofit.thf.command", "en": "THF Admin", "ar": "إدارة THF", "visibility": "operator", "required_roles": {"owner", "admin"}},
}

HEALTH_PROVIDER_STATUS = {
    "health_connect": "SUPPORTED_ANDROID_PRIMARY",
    "samsung_health_data_sdk": "OPTIONAL_PARTNER_ADAPTER",
}

ALLOWED_HEALTH_METRICS = {
    "activity", "workout", "steps", "distance_m", "calories_kcal",
    "heart_rate_bpm", "sleep", "weight_kg", "body_fat_pct",
}


class ContractError(ValueError):
    pass


def visible_products(roles: Iterable[str]) -> list[str]:
    role_set = {str(r).strip().lower() for r in roles}
    out: list[str] = []
    for key, meta in PRODUCTS.items():
        if meta["visibility"] == "public":
            out.append(key)
            continue
        if role_set.intersection(meta["required_roles"]):
            out.append(key)
    return out


def assert_operator_route(product: str, roles: Iterable[str]) -> None:
    if product not in PRODUCTS:
        raise ContractError("unknown_product")
    meta = PRODUCTS[product]
    if meta["visibility"] != "operator":
        return
    role_set = {str(r).strip().lower() for r in roles}
    if not role_set.intersection(meta["required_roles"]):
        raise ContractError("operator_role_required")


def validate_google_oauth_config(config: Mapping[str, Any]) -> dict[str, str]:
    client_id = str(config.get("server_client_id", "")).strip()
    redirect_scheme = str(config.get("redirect_scheme", "thf")).strip()
    if not client_id:
        raise ContractError("google_server_client_id_missing")
    if not re.fullmatch(r"[0-9]+-[A-Za-z0-9_-]+\.apps\.googleusercontent\.com", client_id):
        raise ContractError("google_server_client_id_invalid")
    if any(k in config for k in ("client_secret", "google_client_secret", "oauth_secret")):
        raise ContractError("mobile_config_must_not_contain_client_secret")
    if redirect_scheme != "thf":
        raise ContractError("unexpected_redirect_scheme")
    return {"server_client_id": client_id, "redirect_scheme": redirect_scheme}


def validate_google_id_token_claims(
    claims: Mapping[str, Any], *, expected_audience: str,
    signature_verified: bool, now: int | None = None
) -> dict[str, str]:
    """Validate claims only after a trusted JWT/JWK verifier proves the signature.

    This intentionally refuses decoded-but-unverified JWT payloads. Production callers
    must verify Google's signature/JWK chain first (for example with the provider's
    supported server library), then pass signature_verified=True here.
    """
    if signature_verified is not True:
        raise ContractError("google_signature_verification_required")
    now = int(time.time()) if now is None else int(now)
    issuer = str(claims.get("iss", ""))
    audience = claims.get("aud")
    if issuer not in GOOGLE_ISSUERS:
        raise ContractError("google_issuer_invalid")
    if isinstance(audience, list):
        audience_ok = expected_audience in audience
    else:
        audience_ok = str(audience) == expected_audience
    if not audience_ok:
        raise ContractError("google_audience_invalid")
    try:
        exp = int(claims.get("exp", 0))
    except (TypeError, ValueError) as exc:
        raise ContractError("google_exp_invalid") from exc
    if exp <= now:
        raise ContractError("google_token_expired")
    sub = str(claims.get("sub", "")).strip()
    if not sub:
        raise ContractError("google_subject_missing")
    email = str(claims.get("email", "")).strip().lower()
    verified = claims.get("email_verified") is True or str(claims.get("email_verified", "")).lower() == "true"
    if email and not verified:
        raise ContractError("google_email_not_verified")
    return {"provider": "google", "provider_subject": sub, "email": email}


@dataclass(frozen=True)
class HealthRecord:
    provider: str
    source_record_id: str
    metric: str
    start_ms: int
    end_ms: int
    payload: Mapping[str, Any]

    def validate(self) -> "HealthRecord":
        if self.provider not in HEALTH_PROVIDER_STATUS:
            raise ContractError("unsupported_health_provider")
        if self.metric not in ALLOWED_HEALTH_METRICS:
            raise ContractError("unsupported_health_metric")
        if not self.source_record_id.strip():
            raise ContractError("health_source_record_id_required")
        if self.start_ms < 0 or self.end_ms < self.start_ms:
            raise ContractError("health_time_range_invalid")
        return self

    @property
    def dedup_key(self) -> str:
        self.validate()
        raw = f"{self.provider}|{self.source_record_id}|{self.metric}|{self.start_ms}|{self.end_ms}".encode()
        return sha256(raw).hexdigest()


def deduplicate_health_records(records: Iterable[HealthRecord]) -> list[HealthRecord]:
    seen: set[str] = set()
    out: list[HealthRecord] = []
    for record in records:
        key = record.dedup_key
        if key in seen:
            continue
        seen.add(key)
        out.append(record)
    return out


def health_permission_plan(metrics: Iterable[str], *, provider: str) -> dict[str, Any]:
    requested = sorted({str(x).strip() for x in metrics if str(x).strip()})
    unknown = [x for x in requested if x not in ALLOWED_HEALTH_METRICS]
    if unknown:
        raise ContractError("unsupported_health_metric:" + ",".join(unknown))
    if provider not in HEALTH_PROVIDER_STATUS:
        raise ContractError("unsupported_health_provider")
    return {
        "provider": provider,
        "metrics": requested,
        "consent_required": True,
        "graceful_absence": True,
        "background_read_default": False,
        "historical_read_default": False,
        "reward_authority": False,
    }


def link_guest_to_identity(*, guest_id: str, identity_subject: str, proof_verified: bool) -> dict[str, str]:
    guest_id = guest_id.strip()
    identity_subject = identity_subject.strip()
    if not guest_id or not identity_subject:
        raise ContractError("guest_and_identity_required")
    if not proof_verified:
        raise ContractError("verified_identity_proof_required")
    if guest_id == identity_subject:
        raise ContractError("guest_identity_collision")
    return {"from": "guest", "guest_id": guest_id, "to": "identity", "identity_subject": identity_subject}


def contract_snapshot() -> str:
    payload = {
        "schema": "thf.shared.integration.v1",
        "products": {k: {kk: (sorted(vv) if isinstance(vv, set) else vv) for kk, vv in v.items()} for k, v in PRODUCTS.items()},
        "health_providers": HEALTH_PROVIDER_STATUS,
        "health_metrics": sorted(ALLOWED_HEALTH_METRICS),
        "truth": {
            "google_oauth_console_configured": False,
            "google_server_signature_verifier_bound": False,
            "health_connect_physical_device_verified": False,
            "samsung_partner_registration_verified": False,
            "physical_device_pass": False,
            "final_or_play_ready": False,
        },
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
