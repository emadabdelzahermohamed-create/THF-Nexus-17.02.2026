#!/usr/bin/env python3
"""V9 physical-phone evidence validator.

Extends V8 by binding crash-free claims to an immutable, hash-bound logcat capture
from the same physical-device session and exact package. The validator is fail-closed
and never promotes FINAL/PLAY_READY by itself.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("thf_device_v8", HERE / "validate_game_device_evidence_v8.py")
V8 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = V8
SPEC.loader.exec_module(V8)
V7 = V8.V7
V6 = V8.V6
V5 = V8.V5
V4 = V8.V4
V3 = V8.V3
SHA = re.compile(r"^[0-9a-f]{64}$")

FATAL_MARKERS = (
    "FATAL EXCEPTION",
    "AndroidRuntime",
    "Fatal signal",
    "ANR in ",
    "am_crash",
    "am_anr",
)
APPROVED_METHODS = {"adb-logcat-epoch-package-filter", "adb-logcat-pid-filter"}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_bundle(registry: dict, registry_sha: str, evidence: dict, evidence_root: Path) -> list[str]:
    errors = list(V8.validate_bundle(registry, registry_sha, evidence, evidence_root))
    crash = evidence.get("crash_observation")
    if not isinstance(crash, dict):
        errors.append("crash_observation: missing record")
        return errors

    session = evidence.get("session")
    sid = session.get("session_id") if isinstance(session, dict) else None
    if crash.get("session_id") != sid:
        errors.append("crash_observation.session_id: session_id mismatch")

    if crash.get("package") != evidence.get("package"):
        errors.append("crash_observation.package: must match exact candidate package")
    if crash.get("method") not in APPROVED_METHODS:
        errors.append("crash_observation.method: approved adb logcat method required")
    if crash.get("process_alive_after_core_gameplay") is not True:
        errors.append("crash_observation.process_alive_after_core_gameplay: true required")
    if crash.get("crash_free") is not True:
        errors.append("crash_observation.crash_free: true required")

    started = V5._utc(crash.get("started_at_utc"))
    ended = V5._utc(crash.get("ended_at_utc"))
    s_started = V5._utc(session.get("started_at_utc")) if isinstance(session, dict) else None
    s_ended = V5._utc(session.get("ended_at_utc")) if isinstance(session, dict) else None
    if started is None or ended is None or ended <= started:
        errors.append("crash_observation: strict increasing UTC interval required")
    elif s_started is not None and s_ended is not None and not (s_started <= started < ended <= s_ended):
        errors.append("crash_observation: interval outside declared session")

    ref = crash.get("evidence_ref")
    path = V4._safe_evidence_path(evidence_root, ref)
    declared_sha = str(crash.get("evidence_sha256") or "").lower()
    if path is None or not path.is_file() or path.stat().st_size <= 0:
        errors.append("crash_observation.evidence_ref: non-empty evidence file required")
        return errors
    if SHA.fullmatch(declared_sha) is None:
        errors.append("crash_observation.evidence_sha256: lowercase SHA-256 required")
    elif _sha256(path) != declared_sha:
        errors.append("crash_observation.evidence_sha256: evidence bytes mismatch")

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        errors.append(f"crash_observation: logcat evidence unreadable: {exc}")
        return errors

    if evidence.get("package") not in text:
        errors.append("crash_observation: package identity absent from logcat evidence")
    for marker in FATAL_MARKERS:
        if marker in text:
            errors.append(f"crash_observation: fatal marker present: {marker}")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("registry", type=Path)
    ap.add_argument("evidence", type=Path)
    ap.add_argument("evidence_root", type=Path)
    ns = ap.parse_args()
    registry, registry_sha = V3.load_json(ns.registry)
    evidence, _ = V3.load_json(ns.evidence)
    errors = validate_bundle(registry, registry_sha, evidence, ns.evidence_root)
    if errors:
        for err in errors:
            print("ERROR: " + err, file=sys.stderr)
        print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V9=FAIL")
        print("FINAL_OR_PLAY_READY=FALSE")
        return 1
    print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V9=PASS")
    print(f"PRODUCT={evidence['product']}")
    print(f"EXACT_APK_SHA256={evidence['exact_candidate_sha256']}")
    print("CRASH_FREE_CLAIM_BOUND_TO_LOGCAT=TRUE")
    print("INSTALLED_APK_BYTES_MATCH_CANDIDATE=TRUE")
    print("PERFORMANCE_VALUES_MATCH_HASH_BOUND_CAPTURE=TRUE")
    print("SINGLE_DEVICE_SESSION_BOUND=TRUE")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
