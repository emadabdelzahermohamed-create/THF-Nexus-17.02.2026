#!/usr/bin/env python3
"""V16: bind foreground-process provenance to the exact device, candidate, registry and observation time.

V15 proves that semantic gameplay evidence belongs to the resumed foreground package/PID.
V16 closes replay/substitution gaps by requiring each foreground-process capture to bind to
(1) the physical-device fingerprint, (2) exact installed candidate APK SHA, (3) current
registry SHA, and (4) the exact manual observation timestamp inside the same device session.
It also requires successful raw dumpsys-activity and pidof command exit markers.

This validator is fail-closed and cannot promote FINAL/PLAY_READY by itself.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("thf_device_v15", HERE / "validate_game_device_evidence_v15.py")
V15 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = V15
SPEC.loader.exec_module(V15)
V14, V3, V4 = V15.V14, V15.V3, V15.V4


def _utc(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def validate_bundle(registry: dict, registry_sha: str, evidence: dict, evidence_root: Path) -> list[str]:
    errors = list(V15.validate_bundle(registry, registry_sha, evidence, evidence_root))
    product = evidence.get("product")
    obs = evidence.get("manual_observations") if isinstance(evidence.get("manual_observations"), dict) else {}
    proc = evidence.get("process_provenance") if isinstance(evidence.get("process_provenance"), dict) else {}
    session = evidence.get("session") if isinstance(evidence.get("session"), dict) else {}
    device = evidence.get("device") if isinstance(evidence.get("device"), dict) else {}
    exact_apk_sha = evidence.get("exact_candidate_sha256")
    fingerprint = device.get("fingerprint_sha256")
    started = _utc(session.get("started_at_utc"))
    ended = _utc(session.get("ended_at_utc"))

    req = dict(V14.BASE)
    req.update(V14.PRODUCT.get(product, {}))
    for key in req:
        gameplay = obs.get(key) if isinstance(obs.get(key), dict) else {}
        row = proc.get(key) if isinstance(proc.get(key), dict) else {}
        path = V4._safe_evidence_path(evidence_root, row.get("evidence_ref"))
        if path is None or not path.is_file():
            # V15 already reports the missing provenance file. Avoid duplicate low-value errors.
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        checks = {
            "THF_DEVICE_FINGERPRINT_SHA256": fingerprint,
            "THF_EXACT_APK_SHA256": exact_apk_sha,
            "THF_REGISTRY_SHA256": registry_sha,
            "THF_OBSERVED_AT_UTC": gameplay.get("observed_at_utc"),
            "THF_ACTIVITY_DUMPSYS_EXIT_CODE": "0",
            "THF_PIDOF_EXIT_CODE": "0",
        }
        for marker, want in checks.items():
            if not isinstance(want, str) or V15.one(text, marker) != want:
                errors.append(f"V16 {key}: {marker} mismatch")

        observed = _utc(V15.one(text, "THF_OBSERVED_AT_UTC"))
        if observed is None:
            errors.append(f"V16 {key}: strict UTC process observation timestamp required")
        elif started is not None and ended is not None and not (started <= observed <= ended):
            errors.append(f"V16 {key}: process observation outside declared session interval")

    if evidence.get("final_or_play_ready") is not False:
        errors.append("V16 cannot self-promote FINAL/PLAY_READY")
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
        print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V16=FAIL")
        print("FINAL_OR_PLAY_READY=FALSE")
        return 1
    print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V16=PASS")
    print("FOREGROUND_PROVENANCE_DEVICE_BOUND=TRUE")
    print("FOREGROUND_PROVENANCE_EXACT_APK_BOUND=TRUE")
    print("FOREGROUND_PROVENANCE_REGISTRY_BOUND=TRUE")
    print("FOREGROUND_PROVENANCE_OBSERVATION_TIME_BOUND=TRUE")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
