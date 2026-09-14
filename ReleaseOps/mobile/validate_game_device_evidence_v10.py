#!/usr/bin/env python3
"""V10 physical-phone evidence validator.

Extends V9 by binding touch/orientation/background-resume claims to one immutable,
hash-bound ADB lifecycle transcript from the same physical-device session/package.
It is deliberately fail-closed and never promotes FINAL/PLAY_READY by itself.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("thf_device_v9", HERE / "validate_game_device_evidence_v9.py")
V9 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = V9
SPEC.loader.exec_module(V9)
V5 = V9.V5
V4 = V9.V4
V3 = V9.V3
SHA = re.compile(r"^[0-9a-f]{64}$")
APPROVED_METHODS = {"adb-shell-lifecycle-transcript-v1"}
REQUIRED_MARKERS = (
    "THF_TOUCH_OBSERVED=TRUE",
    "THF_SENSOR_LANDSCAPE_OBSERVED=TRUE",
    "THF_EXPANDABLE_ASPECT_OBSERVED=TRUE",
    "THF_SAFE_AREA_OBSERVED=TRUE",
    "THF_BACKGROUND_PID_BEFORE=",
    "THF_BACKGROUND_PID_AFTER=",
    "THF_BACKGROUND_RESUME_SAME_PID=TRUE",
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _single_value(text: str, key: str) -> str | None:
    prefix = key + "="
    values = [line[len(prefix):].strip() for line in text.splitlines() if line.startswith(prefix)]
    return values[0] if len(values) == 1 else None


def validate_bundle(registry: dict, registry_sha: str, evidence: dict, evidence_root: Path) -> list[str]:
    errors = list(V9.validate_bundle(registry, registry_sha, evidence, evidence_root))
    obs = evidence.get("lifecycle_touch_orientation_observation")
    if not isinstance(obs, dict):
        errors.append("lifecycle_touch_orientation_observation: missing record")
        return errors

    session = evidence.get("session")
    sid = session.get("session_id") if isinstance(session, dict) else None
    if obs.get("session_id") != sid:
        errors.append("lifecycle_touch_orientation_observation.session_id: session_id mismatch")
    if obs.get("package") != evidence.get("package"):
        errors.append("lifecycle_touch_orientation_observation.package: must match exact candidate package")
    if obs.get("method") not in APPROVED_METHODS:
        errors.append("lifecycle_touch_orientation_observation.method: approved ADB method required")

    for field in ("touch_observed", "sensor_landscape_observed", "expandable_aspect_observed", "safe_area_observed", "background_resume_same_pid"):
        if obs.get(field) is not True:
            errors.append(f"lifecycle_touch_orientation_observation.{field}: true required")

    started = V5._utc(obs.get("started_at_utc"))
    ended = V5._utc(obs.get("ended_at_utc"))
    s_started = V5._utc(session.get("started_at_utc")) if isinstance(session, dict) else None
    s_ended = V5._utc(session.get("ended_at_utc")) if isinstance(session, dict) else None
    if started is None or ended is None or ended <= started:
        errors.append("lifecycle_touch_orientation_observation: strict increasing UTC interval required")
    elif s_started is not None and s_ended is not None and not (s_started <= started < ended <= s_ended):
        errors.append("lifecycle_touch_orientation_observation: interval outside declared session")

    path = V4._safe_evidence_path(evidence_root, obs.get("evidence_ref"))
    declared_sha = str(obs.get("evidence_sha256") or "").lower()
    if path is None or not path.is_file() or path.stat().st_size <= 0:
        errors.append("lifecycle_touch_orientation_observation.evidence_ref: non-empty evidence file required")
        return errors
    if SHA.fullmatch(declared_sha) is None:
        errors.append("lifecycle_touch_orientation_observation.evidence_sha256: lowercase SHA-256 required")
    elif _sha256(path) != declared_sha:
        errors.append("lifecycle_touch_orientation_observation.evidence_sha256: evidence bytes mismatch")

    text = path.read_text(encoding="utf-8", errors="replace")
    if evidence.get("package") not in text:
        errors.append("lifecycle_touch_orientation_observation: package identity absent from transcript")
    if sid and sid not in text:
        errors.append("lifecycle_touch_orientation_observation: session identity absent from transcript")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"lifecycle_touch_orientation_observation: required marker absent: {marker}")

    before = _single_value(text, "THF_BACKGROUND_PID_BEFORE")
    after = _single_value(text, "THF_BACKGROUND_PID_AFTER")
    if before is None or after is None:
        errors.append("lifecycle_touch_orientation_observation: exactly one PID-before and PID-after required")
    elif not before.isdigit() or before != after:
        errors.append("lifecycle_touch_orientation_observation: background/resume must preserve the same numeric PID")

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
        print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V10=FAIL")
        print("FINAL_OR_PLAY_READY=FALSE")
        return 1
    print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V10=PASS")
    print(f"PRODUCT={evidence['product']}")
    print(f"EXACT_APK_SHA256={evidence['exact_candidate_sha256']}")
    print("TOUCH_ORIENTATION_LIFECYCLE_BOUND_TO_ADB=TRUE")
    print("BACKGROUND_RESUME_SAME_PID=TRUE")
    print("CRASH_FREE_CLAIM_BOUND_TO_LOGCAT=TRUE")
    print("INSTALLED_APK_BYTES_MATCH_CANDIDATE=TRUE")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
