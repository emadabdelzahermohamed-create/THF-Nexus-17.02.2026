#!/usr/bin/env python3
"""THF app physical-device evidence validator V7.

V7 layers V6 and closes two evidence-substitution gaps:
1. lifecycle transcript identity markers must be unique exact key/value records,
   not substring matches;
2. the transcript is bound to the declared physical-device fingerprint and to
   the observation interval itself.

This is release-control tooling only. It cannot promote FINAL/PLAY_READY.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from validate_app_device_evidence_v6 import validate as validate_v6

REQUIRED_EXACT_KEYS = (
    "THF_SESSION_ID",
    "THF_PACKAGE",
    "THF_CANDIDATE_SHA256",
    "THF_SOURCE_SHA256",
    "THF_DEVICE_FINGERPRINT_SHA256",
    "THF_OBS_STARTED_AT_UTC",
    "THF_OBS_ENDED_AT_UTC",
    "THF_TOUCH_OBSERVED",
    "THF_PORTRAIT_OBSERVED",
    "THF_LANDSCAPE_OBSERVED",
    "THF_RESPONSIVE_LAYOUT_OBSERVED",
    "THF_SAFE_AREA_OBSERVED",
    "THF_BACKGROUND_PID_BEFORE",
    "THF_BACKGROUND_PID_AFTER",
    "THF_BACKGROUND_RESUME_SAME_PID",
)


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


def _kv_multimap(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for raw in text.splitlines():
        if "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        if not key:
            continue
        out.setdefault(key, []).append(value.strip())
    return out


def validate(registry: dict[str, Any], evidence: dict[str, Any], root: Path) -> list[str]:
    errors = list(validate_v6(registry, evidence, root))
    obs = evidence.get("lifecycle_touch_orientation_observation")
    if not isinstance(obs, dict):
        errors.append("V7 lifecycle observation required")
        return errors

    path = _safe_file(root, obs.get("evidence_ref"))
    if path is None:
        errors.append("V7 lifecycle transcript file required")
        return errors

    device = evidence.get("device") if isinstance(evidence.get("device"), dict) else {}
    fingerprint = device.get("fingerprint_sha256")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        errors.append("V7 physical-device fingerprint SHA-256 required")
        return errors

    text = path.read_text(encoding="utf-8", errors="replace")
    kv = _kv_multimap(text)
    expected = {
        "THF_SESSION_ID": obs.get("session_id"),
        "THF_PACKAGE": obs.get("package"),
        "THF_CANDIDATE_SHA256": obs.get("candidate_sha256"),
        "THF_SOURCE_SHA256": obs.get("source_sha256"),
        "THF_DEVICE_FINGERPRINT_SHA256": fingerprint,
        "THF_OBS_STARTED_AT_UTC": obs.get("started_at_utc"),
        "THF_OBS_ENDED_AT_UTC": obs.get("ended_at_utc"),
        "THF_TOUCH_OBSERVED": "TRUE",
        "THF_PORTRAIT_OBSERVED": "TRUE",
        "THF_LANDSCAPE_OBSERVED": "TRUE",
        "THF_RESPONSIVE_LAYOUT_OBSERVED": "TRUE",
        "THF_SAFE_AREA_OBSERVED": "TRUE",
        "THF_BACKGROUND_RESUME_SAME_PID": "TRUE",
    }

    for key in REQUIRED_EXACT_KEYS:
        values = kv.get(key, [])
        if len(values) != 1:
            errors.append(f"V7 lifecycle transcript requires exactly one {key}")
            continue
        if key in expected and values[0] != expected[key]:
            errors.append(f"V7 lifecycle transcript exact value mismatch: {key}")

    before = kv.get("THF_BACKGROUND_PID_BEFORE", [])
    after = kv.get("THF_BACKGROUND_PID_AFTER", [])
    if len(before) == 1 and len(after) == 1:
        if not before[0].isdigit() or before[0] != after[0]:
            errors.append("V7 lifecycle transcript requires one identical numeric PID before/after")

    # Device evidence cannot be silently downgraded while presenting a bound
    # transcript as physical-phone proof.
    if device.get("physical_device") is not True or device.get("emulator_detected") is not False:
        errors.append("V7 requires declared physical device and emulator_detected=false")

    if evidence.get("final_or_play_ready") is not False:
        errors.append("V7 evidence cannot self-promote FINAL/PLAY_READY")
    return errors


__all__ = ["REQUIRED_EXACT_KEYS", "validate"]
