#!/usr/bin/env python3
"""THF app physical-device evidence validator V9.

V9 layers V8 and prevents the offline/local/online lifecycle transcript from
being accepted as the sole network-transition artifact. It requires three
separate SHA-256-bound raw ADB captures (offline connectivity, local UI state,
online connectivity), each bound to the same session/package/candidate/source/
device identity and to strictly increasing capture timestamps. The V8 summary
transcript must bind the exact SHA-256 of all three raw captures.

This is release-control tooling only. It never promotes FINAL/PLAY_READY.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
from typing import Any

from validate_app_device_evidence_v8 import validate as validate_v8

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RAW_CAPTURE_ORDER = ("offline", "local", "online")
APPROVED_RAW_COMMANDS = {
    "offline": "adb shell dumpsys connectivity",
    "local": "adb shell uiautomator dump /dev/tty",
    "online": "adb shell dumpsys connectivity",
}
RAW_KIND_MARKERS = {
    "offline": "THF_RAW_CAPTURE_KIND=OFFLINE_CONNECTIVITY",
    "local": "THF_RAW_CAPTURE_KIND=LOCAL_UI_STATE",
    "online": "THF_RAW_CAPTURE_KIND=ONLINE_CONNECTIVITY",
}
SUMMARY_SHA_KEYS = {
    "offline": "THF_RAW_OFFLINE_SHA256",
    "local": "THF_RAW_LOCAL_SHA256",
    "online": "THF_RAW_ONLINE_SHA256",
}


def _utc(v: Any) -> datetime | None:
    if not isinstance(v, str) or not v:
        return None
    try:
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt.astimezone(timezone.utc) if dt.tzinfo else None


def _safe_file(root: Path, ref: Any) -> Path | None:
    if not isinstance(ref, str) or not ref or "\x00" in ref:
        return None
    base = root.resolve()
    p = (base / ref).resolve()
    try:
        p.relative_to(base)
    except ValueError:
        return None
    return p if p.is_file() else None


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _single(text: str, key: str) -> str | None:
    prefix = key + "="
    vals = [line[len(prefix):].strip() for line in text.splitlines() if line.startswith(prefix)]
    return vals[0] if len(vals) == 1 else None


def _candidate(registry: dict[str, Any], product: Any) -> dict[str, Any] | None:
    rows = [r for r in registry.get("candidates", []) if isinstance(r, dict) and r.get("name") == product]
    return rows[0] if len(rows) == 1 else None


def validate(registry: dict[str, Any], evidence: dict[str, Any], root: Path) -> list[str]:
    errors = list(validate_v8(registry, evidence, root))
    row = _candidate(registry, evidence.get("product"))
    if row is None:
        errors.append("V9 requires exactly one authoritative candidate")
        return errors

    obs = evidence.get("offline_network_observation")
    if not isinstance(obs, dict):
        errors.append("V9 offline_network_observation missing")
        return errors
    raw = obs.get("raw_captures")
    if not isinstance(raw, dict) or set(raw) != set(RAW_CAPTURE_ORDER):
        errors.append("V9 requires exactly offline/local/online raw_captures")
        return errors

    session = evidence.get("session") if isinstance(evidence.get("session"), dict) else {}
    device = evidence.get("device") if isinstance(evidence.get("device"), dict) else {}
    expected = {
        "THF_SESSION_ID": session.get("session_id"),
        "THF_PACKAGE": row.get("package"),
        "THF_CANDIDATE_SHA256": row.get("apk_sha256"),
        "THF_SOURCE_SHA256": row.get("source_sha256"),
        "THF_DEVICE_FINGERPRINT_SHA256": device.get("fingerprint_sha256"),
    }
    obs_start, obs_end = _utc(obs.get("started_at_utc")), _utc(obs.get("ended_at_utc"))

    paths: list[Path] = []
    digests: list[str] = []
    times: list[datetime] = []
    declared_by_kind: dict[str, str] = {}

    for kind in RAW_CAPTURE_ORDER:
        item = raw.get(kind)
        if not isinstance(item, dict):
            errors.append(f"V9 raw {kind} capture object required")
            continue
        if item.get("command") != APPROVED_RAW_COMMANDS[kind]:
            errors.append(f"V9 raw {kind} approved ADB command required")

        path = _safe_file(root, item.get("evidence_ref"))
        declared = item.get("evidence_sha256")
        if path is None or path.stat().st_size <= 0:
            errors.append(f"V9 raw {kind} non-empty evidence file required")
            continue
        if not isinstance(declared, str) or not SHA256_RE.fullmatch(declared):
            errors.append(f"V9 raw {kind} lowercase SHA-256 required")
            continue
        if _digest(path) != declared:
            errors.append(f"V9 raw {kind} evidence SHA mismatch")
        paths.append(path.resolve())
        digests.append(declared)
        declared_by_kind[kind] = declared

        captured = _utc(item.get("captured_at_utc"))
        if captured is None:
            errors.append(f"V9 raw {kind} UTC capture timestamp required")
        else:
            times.append(captured)
            if obs_start is None or obs_end is None or not (obs_start <= captured <= obs_end):
                errors.append(f"V9 raw {kind} timestamp outside offline network observation")

        text = path.read_text(encoding="utf-8", errors="replace")
        for key, value in expected.items():
            if _single(text, key) != value:
                errors.append(f"V9 raw {kind} exact identity mismatch: {key}")
        if RAW_KIND_MARKERS[kind] not in text.splitlines():
            errors.append(f"V9 raw {kind} capture-kind marker required")
        if _single(text, "THF_CAPTURED_AT_UTC") != item.get("captured_at_utc"):
            errors.append(f"V9 raw {kind} timestamp binding mismatch")
        if _single(text, "THF_ADB_COMMAND") != APPROVED_RAW_COMMANDS[kind]:
            errors.append(f"V9 raw {kind} command binding mismatch")
        if _single(text, "THF_ADB_EXIT_CODE") != "0":
            errors.append(f"V9 raw {kind} successful ADB exit code required")

    if len(paths) == 3 and len(set(paths)) != 3:
        errors.append("V9 raw captures must use three distinct files")
    if len(digests) == 3 and len(set(digests)) != 3:
        errors.append("V9 raw captures must have three distinct SHA-256 values")
    if len(times) == 3 and not (times[0] < times[1] < times[2]):
        errors.append("V9 raw capture timestamps must be strictly offline < local < online")

    summary_path = _safe_file(root, obs.get("evidence_ref"))
    if summary_path is not None:
        summary = summary_path.read_text(encoding="utf-8", errors="replace")
        for kind, key in SUMMARY_SHA_KEYS.items():
            if _single(summary, key) != declared_by_kind.get(kind):
                errors.append(f"V9 summary transcript raw SHA binding mismatch: {key}")

    if evidence.get("final_or_play_ready") is not False:
        errors.append("V9 evidence cannot self-promote FINAL/PLAY_READY")
    return errors


__all__ = ["APPROVED_RAW_COMMANDS", "RAW_CAPTURE_ORDER", "RAW_KIND_MARKERS", "SUMMARY_SHA_KEYS", "validate"]
