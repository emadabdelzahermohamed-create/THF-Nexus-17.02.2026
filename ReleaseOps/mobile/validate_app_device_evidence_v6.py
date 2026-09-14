#!/usr/bin/env python3
"""THF app physical-device evidence validator V6.

V6 layers V5 and binds touch/orientation/background-resume claims to one
immutable, SHA-256-bound ADB lifecycle transcript from the same physical-device
session, exact package, exact APK candidate and authoritative source.

This is release-control tooling only. It never promotes FINAL/PLAY_READY.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
from typing import Any

from validate_app_device_evidence_v5 import validate as validate_v5

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
APPROVED_LIFECYCLE_METHOD = "adb-shell-lifecycle-transcript-v1"
REQUIRED_MARKERS = (
    "THF_TOUCH_OBSERVED=TRUE",
    "THF_PORTRAIT_OBSERVED=TRUE",
    "THF_LANDSCAPE_OBSERVED=TRUE",
    "THF_RESPONSIVE_LAYOUT_OBSERVED=TRUE",
    "THF_SAFE_AREA_OBSERVED=TRUE",
    "THF_BACKGROUND_PID_BEFORE=",
    "THF_BACKGROUND_PID_AFTER=",
    "THF_BACKGROUND_RESUME_SAME_PID=TRUE",
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


def _single_value(text: str, key: str) -> str | None:
    prefix = key + "="
    values = [line[len(prefix):].strip() for line in text.splitlines() if line.startswith(prefix)]
    return values[0] if len(values) == 1 else None


def _candidate(registry: dict[str, Any], product: Any) -> dict[str, Any] | None:
    rows = [r for r in registry.get("candidates", []) if isinstance(r, dict) and r.get("name") == product]
    return rows[0] if len(rows) == 1 else None


def validate(registry: dict[str, Any], evidence: dict[str, Any], root: Path) -> list[str]:
    errors = list(validate_v5(registry, evidence, root))
    row = _candidate(registry, evidence.get("product"))
    if row is None:
        errors.append("V6 requires exactly one authoritative candidate")
        return errors

    obs = evidence.get("lifecycle_touch_orientation_observation")
    if not isinstance(obs, dict):
        errors.append("lifecycle_touch_orientation_observation missing")
        return errors

    session = evidence.get("session") if isinstance(evidence.get("session"), dict) else {}
    sid = session.get("session_id")
    package = row.get("package")
    candidate_sha = row.get("apk_sha256")
    source_sha = row.get("source_sha256")

    if obs.get("session_id") != sid:
        errors.append("lifecycle observation session_id mismatch")
    if obs.get("package") != package or evidence.get("package") != package:
        errors.append("lifecycle observation package mismatch")
    if obs.get("candidate_sha256") != candidate_sha:
        errors.append("lifecycle observation candidate SHA mismatch")
    if obs.get("source_sha256") != source_sha:
        errors.append("lifecycle observation source SHA mismatch")
    if obs.get("method") != APPROVED_LIFECYCLE_METHOD:
        errors.append("lifecycle observation approved ADB method required")

    for field in (
        "touch_observed", "portrait_observed", "landscape_observed",
        "responsive_layout_observed", "safe_area_observed",
        "background_resume_same_pid",
    ):
        if obs.get(field) is not True:
            errors.append(f"lifecycle observation {field}=true required")

    started = _parse_ts(obs.get("started_at_utc"))
    ended = _parse_ts(obs.get("ended_at_utc"))
    session_started = _parse_ts(session.get("started_at_utc"))
    session_ended = _parse_ts(session.get("ended_at_utc"))
    if started is None or ended is None or ended <= started:
        errors.append("lifecycle observation strict increasing UTC interval required")
    elif session_started is None or session_ended is None or not (session_started <= started < ended <= session_ended):
        errors.append("lifecycle observation interval outside declared session")

    path = _safe_file(root, obs.get("evidence_ref"))
    declared_sha = obs.get("evidence_sha256")
    if path is None or path.stat().st_size <= 0:
        errors.append("lifecycle observation non-empty evidence file required")
        return errors
    if not isinstance(declared_sha, str) or not SHA256_RE.fullmatch(declared_sha):
        errors.append("lifecycle observation lowercase SHA-256 required")
    elif _sha256(path) != declared_sha:
        errors.append("lifecycle observation evidence SHA mismatch")

    text = path.read_text(encoding="utf-8", errors="replace")
    identity_markers = (
        f"THF_SESSION_ID={sid}",
        f"THF_PACKAGE={package}",
        f"THF_CANDIDATE_SHA256={candidate_sha}",
        f"THF_SOURCE_SHA256={source_sha}",
    )
    for marker in identity_markers + REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"lifecycle observation required marker absent: {marker}")

    before = _single_value(text, "THF_BACKGROUND_PID_BEFORE")
    after = _single_value(text, "THF_BACKGROUND_PID_AFTER")
    if before is None or after is None:
        errors.append("lifecycle observation exactly one PID-before and PID-after required")
    elif not before.isdigit() or before != after:
        errors.append("lifecycle observation background/resume must preserve same numeric PID")

    # The three separately-probed policy checks must all exist and point into
    # the same declared phone session; V6's transcript proves their continuity.
    semantic = evidence.get("semantic_observations") if isinstance(evidence.get("semantic_observations"), dict) else {}
    for check in ("touch", "orientation", "background_resume"):
        if check in registry.get("required_checks", []):
            item = semantic.get(check)
            if not isinstance(item, dict) or item.get("pass") is not True:
                errors.append(f"lifecycle observation requires passing semantic check {check}")

    if evidence.get("final_or_play_ready") is not False:
        errors.append("V6 evidence cannot self-promote FINAL/PLAY_READY")
    return errors


__all__ = ["APPROVED_LIFECYCLE_METHOD", "REQUIRED_MARKERS", "validate"]
