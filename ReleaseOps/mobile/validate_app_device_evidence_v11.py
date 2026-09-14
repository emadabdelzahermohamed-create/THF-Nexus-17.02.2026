#!/usr/bin/env python3
"""THF app physical-device evidence validator V11.

V11 layers V10 and binds foreground-sensitive semantic observations to the
actual resumed process for the exact authoritative app candidate. A separate,
SHA-256-bound process-provenance capture is required per foreground-sensitive
check. This prevents stale/background/wrapper/other-package evidence from
satisfying physical-device acceptance.

This is release-control tooling only and cannot promote FINAL/PLAY_READY.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from validate_app_device_evidence_v10 import validate as validate_v10
from validate_app_device_evidence_v9 import _candidate, _safe_file

PID_RE = re.compile(r"^[1-9]\d*$")
PROCESS_METHOD = "ADB_DUMPSYS_ACTIVITY_PIDOF"
FOREGROUND_CHECKS = (
    "launch",
    "touch",
    "responsive_layout",
    "orientation",
    "background_resume",
    "offline_network",
    "core_user_journey",
    "accessibility",
    "rtl",
    "localization_20_language_readiness",
    "notification_receive",
    "notification_tap_deeplink",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _kv_multimap(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for raw in text.splitlines():
        if "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        if key:
            out.setdefault(key, []).append(value.strip())
    return out


def _one(kv: dict[str, list[str]], key: str) -> str | None:
    values = kv.get(key, [])
    return values[0] if len(values) == 1 else None


def validate(registry: dict[str, Any], evidence: dict[str, Any], root: Path) -> list[str]:
    errors = list(validate_v10(registry, evidence, root))
    row = _candidate(registry, evidence.get("product"))
    if row is None:
        errors.append("V11 requires exactly one authoritative candidate")
        return errors

    semantic = evidence.get("semantic_observations")
    if not isinstance(semantic, dict):
        errors.append("V11 semantic_observations required")
        return errors

    provenance = evidence.get("process_provenance")
    if not isinstance(provenance, dict):
        errors.append("V11 process_provenance required")
        return errors
    if set(provenance) != set(FOREGROUND_CHECKS):
        errors.append("V11 process_provenance must contain exactly foreground-sensitive checks")

    session = evidence.get("session") if isinstance(evidence.get("session"), dict) else {}
    device = evidence.get("device") if isinstance(evidence.get("device"), dict) else {}
    sid = session.get("session_id")
    package = row.get("package")
    candidate_sha = row.get("apk_sha256")
    source_sha = row.get("source_sha256")
    fingerprint = device.get("fingerprint_sha256")

    seen_refs: set[str] = set()
    for check in FOREGROUND_CHECKS:
        prefix = f"V11 {check}: "
        semantic_row = semantic.get(check)
        semantic_sha = semantic_row.get("evidence_sha256") if isinstance(semantic_row, dict) else None
        semantic_ref = semantic_row.get("evidence_ref") if isinstance(semantic_row, dict) else None
        raw_ref = semantic_row.get("raw_evidence_ref") if isinstance(semantic_row, dict) else None
        if not isinstance(semantic_sha, str) or len(semantic_sha) != 64:
            errors.append(prefix + "semantic evidence SHA required")

        item = provenance.get(check)
        if not isinstance(item, dict):
            errors.append(prefix + "process provenance entry required")
            continue
        ref = item.get("evidence_ref")
        if isinstance(ref, str):
            if ref in seen_refs:
                errors.append(prefix + "process provenance file must be unique per check")
            seen_refs.add(ref)
        if ref in (semantic_ref, raw_ref):
            errors.append(prefix + "process provenance must be distinct from semantic/raw evidence")

        path = _safe_file(root, ref)
        if path is None:
            errors.append(prefix + "foreground process provenance file required")
            continue
        expected_sha = item.get("evidence_sha256")
        if not isinstance(expected_sha, str) or expected_sha != _sha256(path):
            errors.append(prefix + "process provenance SHA mismatch")
            continue

        text = path.read_text(encoding="utf-8", errors="replace")
        kv = _kv_multimap(text)
        expected = {
            "THF_SESSION_ID": sid,
            "THF_PACKAGE": package,
            "THF_CANDIDATE_SHA256": candidate_sha,
            "THF_SOURCE_SHA256": source_sha,
            "THF_DEVICE_FINGERPRINT_SHA256": fingerprint,
            "THF_CHECK": check,
            "THF_FOREGROUND_PACKAGE": package,
            "THF_PROCESS_CAPTURE_METHOD": PROCESS_METHOD,
            "THF_PROCESS_ALIVE_AFTER": "TRUE",
            "THF_SEMANTIC_EVIDENCE_SHA256": semantic_sha,
            "THF_ACTIVITY_RESUMED": "TRUE",
        }
        for marker, wanted in expected.items():
            if not isinstance(wanted, str) or _one(kv, marker) != wanted:
                errors.append(prefix + f"{marker} mismatch")

        pid = _one(kv, "THF_FOREGROUND_PID")
        resumed = _one(kv, "THF_RESUMED_PID")
        if not (pid and PID_RE.fullmatch(pid)):
            errors.append(prefix + "valid foreground PID required")
        if resumed != pid:
            errors.append(prefix + "resumed PID must equal foreground PID")

    if evidence.get("final_or_play_ready") is not False:
        errors.append("V11 evidence cannot self-promote FINAL/PLAY_READY")
    return errors


__all__ = ["FOREGROUND_CHECKS", "PROCESS_METHOD", "validate"]
