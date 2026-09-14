#!/usr/bin/env python3
"""V8 physical-phone evidence validator.

Extends V7 by binding typed FPS/RAM/thermal observations to the same immutable
objective ADB capture used for install/launch/runtime evidence. V8 prevents a
performance JSON record from claiming arbitrary values that are unrelated to the
hash-bound objective capture. It remains fail-closed and never promotes
FINAL/PLAY_READY by itself.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("thf_device_v7", HERE / "validate_game_device_evidence_v7.py")
V7 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = V7
SPEC.loader.exec_module(V7)
V6 = V7.V6
V5 = V7.V5
V4 = V7.V4
V3 = V7.V3
SHA = re.compile(r"^[0-9a-f]{64}$")

APPROVED_FPS_METHODS = {"dumpsys-gfxinfo-framestats", "surfaceflinger-latency"}
APPROVED_RAM_METHODS = {"dumpsys-meminfo-total-pss"}
APPROVED_THERMAL_METHODS = {"dumpsys-thermalservice"}


def _close(a: object, b: object, tolerance: float = 0.02) -> bool:
    return isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(float(a) - float(b)) <= tolerance


def validate_bundle(registry: dict, registry_sha: str, evidence: dict, evidence_root: Path) -> list[str]:
    errors = list(V7.validate_bundle(registry, registry_sha, evidence, evidence_root))
    objective = evidence.get("objective")
    performance = evidence.get("performance_observation")
    if not isinstance(objective, dict) or not isinstance(performance, dict):
        return errors

    provenance = performance.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("performance_observation.provenance: missing record")
        return errors

    objective_sha = str(objective.get("evidence_sha256") or "").lower()
    bound_sha = str(provenance.get("objective_evidence_sha256") or "").lower()
    if SHA.fullmatch(bound_sha) is None:
        errors.append("performance_observation.provenance.objective_evidence_sha256: lowercase SHA-256 required")
    elif bound_sha != objective_sha:
        errors.append("performance_observation.provenance.objective_evidence_sha256: must match objective capture SHA")

    if provenance.get("fps_method") not in APPROVED_FPS_METHODS:
        errors.append("performance_observation.provenance.fps_method: approved runtime method required")
    if provenance.get("ram_method") not in APPROVED_RAM_METHODS:
        errors.append("performance_observation.provenance.ram_method: dumpsys meminfo TOTAL PSS required")
    if provenance.get("thermal_method") not in APPROVED_THERMAL_METHODS:
        errors.append("performance_observation.provenance.thermal_method: dumpsys thermalservice required")

    source_pss = provenance.get("ram_source_total_pss_kb")
    objective_pss = objective.get("total_pss_kb")
    if not isinstance(source_pss, int) or source_pss <= 0:
        errors.append("performance_observation.provenance.ram_source_total_pss_kb: positive integer required")
    elif source_pss != objective_pss:
        errors.append("performance_observation.provenance.ram_source_total_pss_kb: must equal objective total_pss_kb")
    expected_ram_mb = round(source_pss / 1024.0, 2) if isinstance(source_pss, int) and source_pss > 0 else None
    if expected_ram_mb is not None and not _close(performance.get("ram_mb_observed"), expected_ram_mb):
        errors.append("performance_observation.ram_mb_observed: must be derived from objective TOTAL PSS")

    source_frames = provenance.get("fps_source_framestats_rows")
    objective_frames = objective.get("framestats_rows")
    if not isinstance(source_frames, int) or source_frames <= 0:
        errors.append("performance_observation.provenance.fps_source_framestats_rows: positive integer required")
    elif source_frames != objective_frames:
        errors.append("performance_observation.provenance.fps_source_framestats_rows: must equal objective framestats_rows")

    if provenance.get("thermal_source_snapshot_present") is not True or objective.get("thermal_snapshot_present") is not True:
        errors.append("performance_observation.provenance.thermal_source_snapshot_present: objective thermal snapshot required")

    sid = evidence.get("session", {}).get("session_id") if isinstance(evidence.get("session"), dict) else None
    if provenance.get("session_id") != sid:
        errors.append("performance_observation.provenance.session_id: session_id mismatch")

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
        print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V8=FAIL")
        print("FINAL_OR_PLAY_READY=FALSE")
        return 1
    print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V8=PASS")
    print(f"PRODUCT={evidence['product']}")
    print(f"EXACT_APK_SHA256={evidence['exact_candidate_sha256']}")
    print("PERFORMANCE_VALUES_BOUND_TO_OBJECTIVE_CAPTURE=TRUE")
    print("INSTALLED_APK_BYTES_MATCH_CANDIDATE=TRUE")
    print("SINGLE_DEVICE_SESSION_BOUND=TRUE")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
