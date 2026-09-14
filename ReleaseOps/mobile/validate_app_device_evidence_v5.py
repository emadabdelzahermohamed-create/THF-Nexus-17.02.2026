#!/usr/bin/env python3
"""THF app physical-device evidence validator V5.

V5 layers V4 and closes the self-declared-check gap: a canonical check file that
merely says RESULT=PASS is not sufficient. Every required check except
``crash_free`` must also be bound to an approved probe method plus a distinct,
hashed raw capture from the same physical-device session.

This is release-control tooling only. It never promotes a candidate by itself.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
from typing import Any

from validate_app_device_evidence_v4 import validate as validate_v4


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

# One method per release-policy check keeps evidence semantics reviewable and
# prevents a generic/manual text attachment from satisfying unrelated checks.
APPROVED_METHODS: dict[str, str] = {
    "install": "adb-install-result",
    "launch": "adb-activity-pid",
    "touch": "adb-input-uiautomator-transition",
    "responsive_layout": "adb-uiautomator-display-bounds",
    "orientation": "adb-rotation-uiautomator",
    "background_resume": "adb-home-resume-same-pid",
    "offline_network": "adb-connectivity-local-state-transition",
    "core_user_journey": "adb-uiautomator-journey",
    "accessibility": "adb-accessibility-uiautomator-audit",
    "data_saver": "adb-netpolicy-restrict-background",
    "rtl": "adb-locale-rtl-uiautomator",
    "localization_20_language_readiness": "device-locale-matrix-20-render",
    "notification_permission": "adb-appops-post-notification",
    "notification_channel": "adb-dumpsys-notification-channel",
    "notification_receive": "adb-logcat-notification-receiver",
    "notification_tap_deeplink": "adb-am-start-deeplink-observation",
}

# Minimal signatures expected in raw command captures. These are deliberately
# structural rather than UI copy so localization cannot cause false failures.
RAW_MARKERS: dict[str, tuple[str, ...]] = {
    "install": ("Success",),
    "launch": ("ACTIVITY", "PID"),
    "touch": ("BEFORE_UI_SHA256=", "AFTER_UI_SHA256="),
    "responsive_layout": ("DISPLAY_BOUNDS=", "UI_BOUNDS="),
    "orientation": ("PORTRAIT_UI_SHA256=", "LANDSCAPE_UI_SHA256="),
    "background_resume": ("PID_BEFORE=", "PID_AFTER="),
    "offline_network": ("NETWORK_ON=", "NETWORK_OFF=", "LOCAL_STATE_PRESERVED="),
    "core_user_journey": ("JOURNEY_START=", "JOURNEY_END="),
    "accessibility": ("A11Y_NODE_COUNT=", "UNLABELED_ACTIONABLE_COUNT="),
    "data_saver": ("RESTRICT_BACKGROUND_BEFORE=", "RESTRICT_BACKGROUND_AFTER="),
    "rtl": ("LOCALE=", "LAYOUT_DIRECTION=RTL", "UI_SHA256="),
    "localization_20_language_readiness": ("LOCALE_COUNT=20", "FAILED_LOCALES=0"),
    "notification_permission": ("POST_NOTIFICATION=",),
    "notification_channel": ("CHANNEL_ID=", "CHANNEL_IMPORTANCE="),
    "notification_receive": ("NOTIFICATION_RECEIVED=",),
    "notification_tap_deeplink": ("DEEPLINK_URI=", "RESOLVED_PACKAGE="),
}

CANONICAL_FIELDS = (
    "THF_APP_SEMANTIC_V5",
    "SESSION_ID",
    "PACKAGE",
    "CANDIDATE_SHA256",
    "SOURCE_SHA256",
    "CHECK",
    "METHOD",
    "RESULT",
    "OBSERVED_AT_UTC",
    "RAW_EVIDENCE_SHA256",
)


def _parse_ts(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None
    return dt.astimezone(timezone.utc)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_file(root: Path, ref: Any) -> Path | None:
    if not isinstance(ref, str) or not ref or "\x00" in ref:
        return None
    root = root.resolve()
    candidate = (root / ref).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def _canonical(path: Path) -> tuple[dict[str, str], list[str]]:
    values: dict[str, str] = {}
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return {}, [f"semantic capture unreadable: {exc}"]
    for line in lines:
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip(); value = value.strip()
        if key in values:
            errors.append(f"duplicate semantic field {key}")
        else:
            values[key] = value
    for key in CANONICAL_FIELDS:
        if not values.get(key):
            errors.append(f"missing semantic field {key}")
    return values, errors


def _candidate(registry: dict[str, Any], product: Any) -> dict[str, Any] | None:
    rows = [r for r in registry.get("candidates", []) if isinstance(r, dict) and r.get("name") == product]
    return rows[0] if len(rows) == 1 else None


def validate(registry: dict[str, Any], evidence: dict[str, Any], root: Path) -> list[str]:
    errors = list(validate_v4(registry, evidence, root))
    product = evidence.get("product")
    row = _candidate(registry, product)
    if row is None:
        errors.append("V5 requires exactly one authoritative candidate")
        return errors

    required = registry.get("required_checks")
    if not isinstance(required, list) or not required:
        errors.append("registry required_checks missing")
        return errors
    unsupported = sorted(set(required) - set(APPROVED_METHODS) - {"crash_free"})
    if unsupported:
        errors.append(f"required checks lack V5 approved methods: {unsupported}")

    semantic = evidence.get("semantic_observations")
    if not isinstance(semantic, dict):
        errors.append("semantic_observations missing")
        return errors

    expected = set(required) - {"crash_free"}
    extras = set(semantic) - expected
    missing = expected - set(semantic)
    if missing:
        errors.append(f"semantic observations missing checks: {sorted(missing)}")
    if extras:
        errors.append(f"semantic observations contain unregistered checks: {sorted(extras)}")

    session = evidence.get("session") if isinstance(evidence.get("session"), dict) else {}
    sid = session.get("session_id")
    start = _parse_ts(session.get("started_at_utc")); end = _parse_ts(session.get("ended_at_utc"))
    package = row.get("package"); candidate_sha = row.get("apk_sha256"); source_sha = row.get("source_sha256")

    for check in sorted(expected & set(semantic)):
        item = semantic.get(check)
        prefix = f"semantic {check}: "
        if not isinstance(item, dict):
            errors.append(prefix + "entry must be object"); continue
        method = item.get("method")
        if method != APPROVED_METHODS.get(check):
            errors.append(prefix + "unapproved or wrong probe method")
        if item.get("pass") is not True:
            errors.append(prefix + "pass must be true")
        observed = _parse_ts(item.get("observed_at_utc"))
        if not observed or not start or not end or not (start <= observed <= end):
            errors.append(prefix + "observation timestamp outside session")

        semantic_path = _safe_file(root, item.get("evidence_ref"))
        semantic_sha = item.get("evidence_sha256")
        if semantic_path is None:
            errors.append(prefix + "semantic evidence file missing")
            continue
        if not isinstance(semantic_sha, str) or not SHA256_RE.fullmatch(semantic_sha) or _sha256(semantic_path) != semantic_sha:
            errors.append(prefix + "semantic evidence SHA mismatch")

        raw_path = _safe_file(root, item.get("raw_evidence_ref"))
        raw_sha = item.get("raw_evidence_sha256")
        if raw_path is None:
            errors.append(prefix + "raw probe capture missing")
            continue
        if raw_path == semantic_path:
            errors.append(prefix + "raw capture must be distinct from semantic manifest")
        if not isinstance(raw_sha, str) or not SHA256_RE.fullmatch(raw_sha) or _sha256(raw_path) != raw_sha:
            errors.append(prefix + "raw probe capture SHA mismatch")
            continue
        if raw_path.stat().st_size <= 0:
            errors.append(prefix + "raw probe capture empty")
            continue
        try:
            raw_text = raw_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            errors.append(prefix + f"raw capture unreadable: {exc}"); continue
        for marker in RAW_MARKERS.get(check, ()):
            if marker not in raw_text:
                errors.append(prefix + f"raw capture missing marker {marker}")

        fields, field_errors = _canonical(semantic_path)
        errors.extend(prefix + msg for msg in field_errors)
        if field_errors:
            continue
        expected_fields = {
            "THF_APP_SEMANTIC_V5": "1",
            "SESSION_ID": str(sid),
            "PACKAGE": str(package),
            "CANDIDATE_SHA256": str(candidate_sha),
            "SOURCE_SHA256": str(source_sha),
            "CHECK": check,
            "METHOD": APPROVED_METHODS.get(check, ""),
            "RESULT": "PASS",
            "OBSERVED_AT_UTC": str(item.get("observed_at_utc")),
            "RAW_EVIDENCE_SHA256": str(raw_sha),
        }
        for key, expected_value in expected_fields.items():
            if fields.get(key) != expected_value:
                errors.append(prefix + f"canonical {key} mismatch")

    if evidence.get("final_or_play_ready") is not False:
        errors.append("V5 evidence cannot self-promote FINAL/PLAY_READY")
    return errors


__all__ = ["APPROVED_METHODS", "RAW_MARKERS", "validate"]
