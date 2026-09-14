#!/usr/bin/env python3
"""THF app physical-device evidence V4.

Layers on V3 and binds crash-free claims to a non-empty SHA-256-bound ADB logcat
capture from the same physical-device session and exact package. Fail-closed; this
tool can never promote a candidate to FINAL/PLAY_READY.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from validate_app_device_evidence_v3 import validate as validate_v3, safe_file

HEX64 = re.compile(r"^[0-9a-f]{64}$")
APPROVED_METHODS = {"adb-logcat-epoch-package-filter", "adb-logcat-pid-filter"}
FATAL_MARKERS = (
    "FATAL EXCEPTION",
    "AndroidRuntime",
    "Fatal signal",
    "ANR in ",
    "am_crash",
    "am_anr",
)


def parse_utc(value: object) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("UTC timestamp missing")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return dt.astimezone(timezone.utc)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(registry: dict, evidence: dict, root: Path) -> list[str]:
    errors = list(validate_v3(registry, evidence, root))
    if errors:
        return errors
    try:
        crash = evidence.get("crash_observation")
        if not isinstance(crash, dict):
            raise ValueError("crash_observation missing")

        session = evidence["session"]
        sid = session["session_id"]
        package = evidence["package"]
        if crash.get("session_id") != sid:
            raise ValueError("crash_observation session_id mismatch")
        if crash.get("package") != package:
            raise ValueError("crash_observation package mismatch")
        if crash.get("method") not in APPROVED_METHODS:
            raise ValueError("approved adb logcat capture method required")
        if crash.get("process_alive_after_core_journey") is not True:
            raise ValueError("process_alive_after_core_journey=true required")
        if crash.get("crash_free") is not True:
            raise ValueError("crash_free=true required")

        started = parse_utc(crash.get("started_at_utc"))
        ended = parse_utc(crash.get("ended_at_utc"))
        s_started = parse_utc(session.get("started_at_utc"))
        s_ended = parse_utc(session.get("ended_at_utc"))
        if ended <= started:
            raise ValueError("crash observation requires a strict increasing UTC interval")
        if not (s_started <= started < ended <= s_ended):
            raise ValueError("crash observation interval lies outside device session")

        path = safe_file(root, crash.get("evidence_ref"))
        declared = str(crash.get("evidence_sha256") or "").lower()
        if HEX64.fullmatch(declared) is None:
            raise ValueError("crash observation evidence SHA-256 missing/invalid")
        if sha256_file(path) != declared:
            raise ValueError("crash observation evidence SHA mismatch")

        text = path.read_text(encoding="utf-8", errors="replace")
        if package not in text:
            raise ValueError("package identity absent from logcat evidence")
        for marker in FATAL_MARKERS:
            if marker in text:
                raise ValueError(f"fatal marker present in logcat evidence: {marker}")

        if evidence.get("final_or_play_ready") is not False:
            raise ValueError("evidence tooling must not self-promote FINAL/PLAY_READY")
    except (KeyError, TypeError, ValueError, OSError) as exc:
        errors.append(str(exc))
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True, type=Path)
    ap.add_argument("--evidence", required=True, type=Path)
    ap.add_argument("--evidence-root", required=True, type=Path)
    ns = ap.parse_args()
    try:
        registry = json.loads(ns.registry.read_text(encoding="utf-8"))
        evidence = json.loads(ns.evidence.read_text(encoding="utf-8"))
        errors = validate(registry, evidence, ns.evidence_root.resolve())
    except Exception as exc:
        errors = [str(exc)]
    if errors:
        print(json.dumps({"status": "BLOCKED", "errors": errors, "final_or_play_ready": False}, indent=2), file=sys.stderr)
        return 2
    print(json.dumps({
        "status": "APP_PHYSICAL_EVIDENCE_V4_VALID",
        "product": evidence["product"],
        "exact_candidate_sha256": evidence["exact_candidate_sha256"],
        "crash_free_claim_bound_to_logcat": True,
        "final_or_play_ready": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
