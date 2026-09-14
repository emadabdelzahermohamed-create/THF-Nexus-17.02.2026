#!/usr/bin/env python3
"""V11 physical-phone evidence validator.

Extends V10 by binding offline->local-play->online-restored claims to one immutable,
hash-bound ADB connectivity transcript from the same physical-device session/package.
The gate is deliberately fail-closed and never promotes FINAL/PLAY_READY by itself.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("thf_device_v10", HERE / "validate_game_device_evidence_v10.py")
V10 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = V10
SPEC.loader.exec_module(V10)
V9 = V10.V9
V5 = V10.V5
V4 = V10.V4
V3 = V10.V3
SHA = re.compile(r"^[0-9a-f]{64}$")
APPROVED_METHODS = {"adb-shell-connectivity-transition-v1"}
REQUIRED_UNIQUE_VALUES = {
    "THF_OFFLINE_REACHED": "TRUE",
    "THF_LOCAL_MODE_STAYED_LOCAL": "TRUE",
    "THF_ONLINE_STATE_FAKED": "FALSE",
    "THF_ONLINE_RESTORED": "TRUE",
    "THF_NETWORK_PID_SAME": "TRUE",
}
ORDERED_MARKERS = (
    "THF_STAGE=OFFLINE_CONFIRMED",
    "THF_STAGE=LOCAL_GAMEPLAY_OBSERVED",
    "THF_STAGE=ONLINE_RESTORED",
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


def _ordered_once(text: str, markers: tuple[str, ...]) -> bool:
    positions: list[int] = []
    for marker in markers:
        if text.count(marker) != 1:
            return False
        positions.append(text.index(marker))
    return positions == sorted(positions) and len(set(positions)) == len(positions)


def validate_bundle(registry: dict, registry_sha: str, evidence: dict, evidence_root: Path) -> list[str]:
    errors = list(V10.validate_bundle(registry, registry_sha, evidence, evidence_root))
    obs = evidence.get("offline_network_observation")
    if not isinstance(obs, dict):
        errors.append("offline_network_observation: missing record")
        return errors

    session = evidence.get("session")
    sid = session.get("session_id") if isinstance(session, dict) else None
    package = evidence.get("package")
    if obs.get("session_id") != sid:
        errors.append("offline_network_observation.session_id: session_id mismatch")
    if obs.get("package") != package:
        errors.append("offline_network_observation.package: must match exact candidate package")
    if obs.get("method") not in APPROVED_METHODS:
        errors.append("offline_network_observation.method: approved ADB connectivity method required")

    required_true = (
        "offline_reached",
        "online_restored",
        "process_same_pid",
        "local_mode_stayed_local",
        "no_online_state_faked",
    )
    for field in required_true:
        if obs.get(field) is not True:
            errors.append(f"offline_network_observation.{field}: true required")

    started = V5._utc(obs.get("started_at_utc"))
    ended = V5._utc(obs.get("ended_at_utc"))
    s_started = V5._utc(session.get("started_at_utc")) if isinstance(session, dict) else None
    s_ended = V5._utc(session.get("ended_at_utc")) if isinstance(session, dict) else None
    if started is None or ended is None or ended <= started:
        errors.append("offline_network_observation: strict increasing UTC interval required")
    elif s_started is not None and s_ended is not None and not (s_started <= started < ended <= s_ended):
        errors.append("offline_network_observation: interval outside declared session")

    path = V4._safe_evidence_path(evidence_root, obs.get("evidence_ref"))
    declared_sha = str(obs.get("evidence_sha256") or "").lower()
    if path is None or not path.is_file() or path.stat().st_size <= 0:
        errors.append("offline_network_observation.evidence_ref: non-empty evidence file required")
        return errors
    if SHA.fullmatch(declared_sha) is None:
        errors.append("offline_network_observation.evidence_sha256: lowercase SHA-256 required")
    elif _sha256(path) != declared_sha:
        errors.append("offline_network_observation.evidence_sha256: evidence bytes mismatch")

    text = path.read_text(encoding="utf-8", errors="replace")
    if package not in text:
        errors.append("offline_network_observation: package identity absent from transcript")
    if sid and sid not in text:
        errors.append("offline_network_observation: session identity absent from transcript")

    for key, expected in REQUIRED_UNIQUE_VALUES.items():
        actual = _single_value(text, key)
        if actual != expected:
            errors.append(f"offline_network_observation: {key} must occur exactly once with value {expected}")

    if not _ordered_once(text, ORDERED_MARKERS):
        errors.append("offline_network_observation: offline/local/online stages must occur exactly once in strict order")

    before = _single_value(text, "THF_NETWORK_PID_BEFORE")
    after = _single_value(text, "THF_NETWORK_PID_AFTER")
    if before is None or after is None:
        errors.append("offline_network_observation: exactly one network PID-before and PID-after required")
    elif not before.isdigit() or before != after:
        errors.append("offline_network_observation: offline/online transition must preserve the same numeric PID")

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
        print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V11=FAIL")
        print("FINAL_OR_PLAY_READY=FALSE")
        return 1
    print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V11=PASS")
    print(f"PRODUCT={evidence['product']}")
    print(f"EXACT_APK_SHA256={evidence['exact_candidate_sha256']}")
    print("OFFLINE_LOCAL_ONLINE_TRANSITION_BOUND_TO_ADB=TRUE")
    print("LOCAL_MODE_STAYED_LOCAL=TRUE")
    print("ONLINE_STATE_FAKED=FALSE")
    print("NETWORK_TRANSITION_SAME_PID=TRUE")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
