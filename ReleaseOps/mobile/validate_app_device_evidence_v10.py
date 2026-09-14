#!/usr/bin/env python3
"""THF app physical-device evidence validator V10.

V10 layers V9 and rejects metadata-only raw ADB captures. Each V9 raw file must
contain a bounded raw-stdout section whose semantics match the claimed stage:
offline connectivity has no VALIDATED network, local UI contains the exact app
package in a uiautomator hierarchy, and restored connectivity contains a
VALIDATED network. This is release-control tooling only and cannot promote
FINAL/PLAY_READY.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from validate_app_device_evidence_v9 import RAW_CAPTURE_ORDER, _candidate, _safe_file, validate as validate_v9

STDOUT_BEGIN = "THF_ADB_STDOUT_BEGIN"
STDOUT_END = "THF_ADB_STDOUT_END"
VALIDATED_RE = re.compile(r"(?:^|[\s,;:\[\]()])VALIDATED(?:$|[\s,;:\[\]()])", re.IGNORECASE)


def _stdout(text: str) -> str | None:
    if text.count(STDOUT_BEGIN) != 1 or text.count(STDOUT_END) != 1:
        return None
    start = text.index(STDOUT_BEGIN) + len(STDOUT_BEGIN)
    end = text.index(STDOUT_END)
    if end <= start:
        return None
    payload = text[start:end].strip()
    return payload if payload else None


def _has_connectivity_shape(payload: str) -> bool:
    lower = payload.lower()
    return any(marker in lower for marker in ("networkagentinfo", "networkcapabilities", "networkrequest", "connectivity"))


def validate(registry: dict[str, Any], evidence: dict[str, Any], root: Path) -> list[str]:
    errors = list(validate_v9(registry, evidence, root))
    row = _candidate(registry, evidence.get("product"))
    if row is None:
        errors.append("V10 requires exactly one authoritative candidate")
        return errors
    obs = evidence.get("offline_network_observation")
    raw = obs.get("raw_captures") if isinstance(obs, dict) else None
    if not isinstance(raw, dict) or set(raw) != set(RAW_CAPTURE_ORDER):
        errors.append("V10 requires V9 offline/local/online raw captures")
        return errors

    payloads: dict[str, str] = {}
    for kind in RAW_CAPTURE_ORDER:
        item = raw.get(kind)
        path = _safe_file(root, item.get("evidence_ref") if isinstance(item, dict) else None)
        if path is None:
            errors.append(f"V10 raw {kind} evidence file required")
            continue
        payload = _stdout(path.read_text(encoding="utf-8", errors="replace"))
        if payload is None:
            errors.append(f"V10 raw {kind} bounded ADB stdout required")
            continue
        payloads[kind] = payload

    offline = payloads.get("offline")
    if offline is not None:
        if not _has_connectivity_shape(offline):
            errors.append("V10 offline raw stdout lacks connectivity structure")
        if VALIDATED_RE.search(offline):
            errors.append("V10 offline raw stdout unexpectedly contains VALIDATED network")

    online = payloads.get("online")
    if online is not None:
        if not _has_connectivity_shape(online):
            errors.append("V10 online raw stdout lacks connectivity structure")
        if VALIDATED_RE.search(online) is None:
            errors.append("V10 online raw stdout must contain VALIDATED network")

    local = payloads.get("local")
    if local is not None:
        package = str(row.get("package") or "")
        if "<hierarchy" not in local or "<node" not in local:
            errors.append("V10 local raw stdout must contain uiautomator hierarchy")
        if not package or re.search(rf'\bpackage=["\']{re.escape(package)}["\']', local) is None:
            errors.append("V10 local raw stdout must contain exact candidate package")

    if evidence.get("final_or_play_ready") is not False:
        errors.append("V10 evidence cannot self-promote FINAL/PLAY_READY")
    return errors


__all__ = ["STDOUT_BEGIN", "STDOUT_END", "VALIDATED_RE", "validate"]
