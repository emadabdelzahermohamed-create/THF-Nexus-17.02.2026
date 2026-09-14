#!/usr/bin/env python3
"""THF app physical-device evidence validator V8.

V8 layers V7 and requires one immutable SHA-256-bound ADB transcript proving
OFFLINE_CONFIRMED -> LOCAL_APP_OPERATION_OBSERVED -> ONLINE_RESTORED inside the
same physical-phone session/package/candidate/source/device identity. Tooling is
fail-closed and cannot promote FINAL/PLAY_READY.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
from typing import Any

from validate_app_device_evidence_v7 import validate as validate_v7

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
APPROVED_NETWORK_METHOD = "adb-shell-connectivity-transition-v1"
REQUIRED_UNIQUE_VALUES = {
    "THF_OFFLINE_REACHED": "TRUE",
    "THF_LOCAL_MODE_STAYED_LOCAL": "TRUE",
    "THF_ONLINE_STATE_FAKED": "FALSE",
    "THF_ONLINE_RESTORED": "TRUE",
    "THF_NETWORK_PID_SAME": "TRUE",
}
ORDERED_MARKERS = (
    "THF_STAGE=OFFLINE_CONFIRMED",
    "THF_STAGE=LOCAL_APP_OPERATION_OBSERVED",
    "THF_STAGE=ONLINE_RESTORED",
)


def _utc(v: Any) -> datetime | None:
    if not isinstance(v, str) or not v:
        return None
    try:
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt.astimezone(timezone.utc) if dt.tzinfo else None


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
    p = (root / ref).resolve()
    try:
        p.relative_to(root)
    except ValueError:
        return None
    return p if p.is_file() else None


def _single(text: str, key: str) -> str | None:
    prefix = key + "="
    vals = [line[len(prefix):].strip() for line in text.splitlines() if line.startswith(prefix)]
    return vals[0] if len(vals) == 1 else None


def _ordered_once(text: str) -> bool:
    pos = []
    for marker in ORDERED_MARKERS:
        if text.count(marker) != 1:
            return False
        pos.append(text.index(marker))
    return pos == sorted(pos) and len(set(pos)) == len(pos)


def _candidate(registry: dict[str, Any], product: Any) -> dict[str, Any] | None:
    rows = [r for r in registry.get("candidates", []) if isinstance(r, dict) and r.get("name") == product]
    return rows[0] if len(rows) == 1 else None


def validate(registry: dict[str, Any], evidence: dict[str, Any], root: Path) -> list[str]:
    errors = list(validate_v7(registry, evidence, root))
    row = _candidate(registry, evidence.get("product"))
    if row is None:
        errors.append("V8 requires exactly one authoritative candidate")
        return errors
    obs = evidence.get("offline_network_observation")
    if not isinstance(obs, dict):
        errors.append("offline_network_observation missing")
        return errors

    session = evidence.get("session") if isinstance(evidence.get("session"), dict) else {}
    device = evidence.get("device") if isinstance(evidence.get("device"), dict) else {}
    expected = {
        "session_id": session.get("session_id"),
        "package": row.get("package"),
        "candidate_sha256": row.get("apk_sha256"),
        "source_sha256": row.get("source_sha256"),
        "device_fingerprint_sha256": device.get("fingerprint_sha256"),
    }
    for field, value in expected.items():
        if obs.get(field) != value:
            errors.append(f"offline network observation {field} mismatch")
    if obs.get("method") != APPROVED_NETWORK_METHOD:
        errors.append("offline network observation approved ADB method required")
    for field in ("offline_reached", "local_mode_stayed_local", "no_online_state_faked", "online_restored", "process_same_pid"):
        if obs.get(field) is not True:
            errors.append(f"offline network observation {field}=true required")

    started, ended = _utc(obs.get("started_at_utc")), _utc(obs.get("ended_at_utc"))
    s0, s1 = _utc(session.get("started_at_utc")), _utc(session.get("ended_at_utc"))
    if started is None or ended is None or ended <= started:
        errors.append("offline network observation strict increasing UTC interval required")
    elif s0 is None or s1 is None or not (s0 <= started < ended <= s1):
        errors.append("offline network observation interval outside declared session")

    path = _safe_file(root, obs.get("evidence_ref"))
    declared = obs.get("evidence_sha256")
    if path is None or path.stat().st_size <= 0:
        errors.append("offline network observation non-empty evidence file required")
        return errors
    if not isinstance(declared, str) or not SHA256_RE.fullmatch(declared):
        errors.append("offline network observation lowercase SHA-256 required")
    elif _sha256(path) != declared:
        errors.append("offline network observation evidence SHA mismatch")

    text = path.read_text(encoding="utf-8", errors="replace")
    transcript_expected = {
        "THF_SESSION_ID": expected["session_id"],
        "THF_PACKAGE": expected["package"],
        "THF_CANDIDATE_SHA256": expected["candidate_sha256"],
        "THF_SOURCE_SHA256": expected["source_sha256"],
        "THF_DEVICE_FINGERPRINT_SHA256": expected["device_fingerprint_sha256"],
        "THF_OBS_STARTED_AT_UTC": obs.get("started_at_utc"),
        "THF_OBS_ENDED_AT_UTC": obs.get("ended_at_utc"),
    }
    for key, value in transcript_expected.items():
        if _single(text, key) != value:
            errors.append(f"offline network transcript exact value mismatch: {key}")
    for key, value in REQUIRED_UNIQUE_VALUES.items():
        if _single(text, key) != value:
            errors.append(f"offline network transcript {key} must occur exactly once with value {value}")
    if not _ordered_once(text):
        errors.append("offline network stages must occur exactly once in strict order")
    before, after = _single(text, "THF_NETWORK_PID_BEFORE"), _single(text, "THF_NETWORK_PID_AFTER")
    if before is None or after is None or not before.isdigit() or before != after:
        errors.append("offline network transition must preserve same numeric PID")
    if evidence.get("final_or_play_ready") is not False:
        errors.append("V8 evidence cannot self-promote FINAL/PLAY_READY")
    return errors


__all__ = ["APPROVED_NETWORK_METHOD", "REQUIRED_UNIQUE_VALUES", "ORDERED_MARKERS", "validate"]
