#!/usr/bin/env python3
"""V12 physical-phone evidence validator.

Extends V11 by requiring three independent, SHA-256-bound raw ADB captures for
offline connectivity, local UI/game state, and restored online connectivity.
Every raw capture must bind the same session, package, exact candidate APK,
registry snapshot and physical-device fingerprint. This release-control gate is
fail-closed and never promotes FINAL/PLAY_READY by itself.
"""
from __future__ import annotations

from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
from pathlib import Path
import re
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("thf_device_v11", HERE / "validate_game_device_evidence_v11.py")
V11 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = V11
SPEC.loader.exec_module(V11)
V3, V4 = V11.V3, V11.V4
SHA = re.compile(r"^[0-9a-f]{64}$")
RAW_ORDER = ("offline", "local", "online")
COMMANDS = {
    "offline": "adb shell dumpsys connectivity",
    "local": "adb shell uiautomator dump /dev/tty",
    "online": "adb shell dumpsys connectivity",
}
KIND_MARKERS = {
    "offline": "THF_RAW_CAPTURE_KIND=OFFLINE_CONNECTIVITY",
    "local": "THF_RAW_CAPTURE_KIND=LOCAL_GAME_STATE",
    "online": "THF_RAW_CAPTURE_KIND=ONLINE_CONNECTIVITY",
}
SUMMARY_KEYS = {
    "offline": "THF_RAW_OFFLINE_SHA256",
    "local": "THF_RAW_LOCAL_SHA256",
    "online": "THF_RAW_ONLINE_SHA256",
}


def _utc(v: Any) -> datetime | None:
    if not isinstance(v, str) or not v:
        return None
    try:
        d = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None
    return d.astimezone(timezone.utc) if d.tzinfo else None


def _digest(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _single(text: str, key: str) -> str | None:
    prefix = key + "="
    vals = [x[len(prefix):].strip() for x in text.splitlines() if x.startswith(prefix)]
    return vals[0] if len(vals) == 1 else None


def _candidate(registry: dict, product: Any) -> dict | None:
    rows = [r for r in registry.get("candidates", []) if isinstance(r, dict) and (r.get("app") == product or r.get("name") == product)]
    return rows[0] if len(rows) == 1 else None


def validate_bundle(registry: dict, registry_sha: str, evidence: dict, root: Path) -> list[str]:
    errors = list(V11.validate_bundle(registry, registry_sha, evidence, root))
    row = _candidate(registry, evidence.get("product"))
    if row is None:
        errors.append("V12 requires exactly one authoritative candidate")
        return errors
    obs = evidence.get("offline_network_observation")
    if not isinstance(obs, dict):
        errors.append("V12 offline_network_observation missing")
        return errors
    raw = obs.get("raw_captures")
    if not isinstance(raw, dict) or set(raw) != set(RAW_ORDER):
        errors.append("V12 requires exactly offline/local/online raw_captures")
        return errors

    session = evidence.get("session") if isinstance(evidence.get("session"), dict) else {}
    device = evidence.get("device") if isinstance(evidence.get("device"), dict) else {}
    expected = {
        "THF_SESSION_ID": session.get("session_id"),
        "THF_PACKAGE": row.get("package"),
        "THF_CANDIDATE_SHA256": row.get("apk_sha256"),
        "THF_REGISTRY_SHA256": registry_sha,
        "THF_DEVICE_FINGERPRINT_SHA256": device.get("fingerprint_sha256"),
    }
    start, end = _utc(obs.get("started_at_utc")), _utc(obs.get("ended_at_utc"))
    paths, digests, times = [], [], []
    declared_by_kind: dict[str, str] = {}

    for kind in RAW_ORDER:
        item = raw.get(kind)
        if not isinstance(item, dict):
            errors.append(f"V12 raw {kind} capture object required")
            continue
        if item.get("command") != COMMANDS[kind]:
            errors.append(f"V12 raw {kind} approved ADB command required")
        p = V4._safe_evidence_path(root, item.get("evidence_ref"))
        declared = str(item.get("evidence_sha256") or "").lower()
        if p is None or not p.is_file() or p.stat().st_size <= 0:
            errors.append(f"V12 raw {kind} non-empty evidence file required")
            continue
        if SHA.fullmatch(declared) is None:
            errors.append(f"V12 raw {kind} lowercase SHA-256 required")
            continue
        if _digest(p) != declared:
            errors.append(f"V12 raw {kind} evidence SHA mismatch")
        paths.append(p.resolve()); digests.append(declared); declared_by_kind[kind] = declared

        captured = _utc(item.get("captured_at_utc"))
        if captured is None:
            errors.append(f"V12 raw {kind} UTC capture timestamp required")
        else:
            times.append(captured)
            if start is None or end is None or not (start <= captured <= end):
                errors.append(f"V12 raw {kind} timestamp outside network observation")

        text = p.read_text(encoding="utf-8", errors="replace")
        for key, value in expected.items():
            if _single(text, key) != value:
                errors.append(f"V12 raw {kind} exact identity mismatch: {key}")
        if KIND_MARKERS[kind] not in text.splitlines():
            errors.append(f"V12 raw {kind} capture-kind marker required")
        if _single(text, "THF_CAPTURED_AT_UTC") != item.get("captured_at_utc"):
            errors.append(f"V12 raw {kind} timestamp binding mismatch")
        if _single(text, "THF_ADB_COMMAND") != COMMANDS[kind]:
            errors.append(f"V12 raw {kind} command binding mismatch")
        if _single(text, "THF_ADB_EXIT_CODE") != "0":
            errors.append(f"V12 raw {kind} successful ADB exit code required")

    if len(paths) == 3 and len(set(paths)) != 3:
        errors.append("V12 raw captures must use three distinct files")
    if len(digests) == 3 and len(set(digests)) != 3:
        errors.append("V12 raw captures must have three distinct SHA-256 values")
    if len(times) == 3 and not (times[0] < times[1] < times[2]):
        errors.append("V12 raw capture timestamps must be strictly offline < local < online")

    summary = V4._safe_evidence_path(root, obs.get("evidence_ref"))
    if summary is not None and summary.is_file():
        text = summary.read_text(encoding="utf-8", errors="replace")
        for kind, key in SUMMARY_KEYS.items():
            if _single(text, key) != declared_by_kind.get(kind):
                errors.append(f"V12 summary raw SHA binding mismatch: {key}")
    if evidence.get("final_or_play_ready") is not False:
        errors.append("V12 cannot self-promote FINAL/PLAY_READY")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("registry", type=Path); ap.add_argument("evidence", type=Path); ap.add_argument("evidence_root", type=Path); ns = ap.parse_args()
    registry, registry_sha = V3.load_json(ns.registry); evidence, _ = V3.load_json(ns.evidence)
    errors = validate_bundle(registry, registry_sha, evidence, ns.evidence_root)
    if errors:
        for e in errors: print("ERROR: " + e, file=sys.stderr)
        print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V12=FAIL\nFINAL_OR_PLAY_READY=FALSE"); return 1
    print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V12=PASS")
    print(f"PRODUCT={evidence['product']}\nEXACT_APK_SHA256={evidence['exact_candidate_sha256']}")
    print("RAW_OFFLINE_LOCAL_ONLINE_ADB_CHAIN=TRUE\nFINAL_OR_PLAY_READY=FALSE"); return 0


if __name__ == "__main__": raise SystemExit(main())
