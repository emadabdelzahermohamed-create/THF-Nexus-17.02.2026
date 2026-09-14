#!/usr/bin/env python3
"""V6 physical-phone evidence validator.

Extends V5 by requiring the objective ADB/runtime capture and performance capture to
reference real non-empty files inside the evidence bundle and bind each file by SHA-256.
This prevents typed JSON claims for install/launch/PSS/framestats/thermal/FPS from being
accepted without immutable capture evidence. V6 never promotes FINAL/PLAY_READY itself.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("thf_device_v5", HERE / "validate_game_device_evidence_v5.py")
V5 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = V5
SPEC.loader.exec_module(V5)
V4 = V5.V4
V3 = V5.V3
SHA = re.compile(r"^[0-9a-f]{64}$")


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _verify_capture(errors: list[str], namespace: str, row: object, evidence_root: Path) -> None:
    if not isinstance(row, dict):
        errors.append(f"{namespace}: missing record")
        return
    target = V4._safe_evidence_path(evidence_root, row.get("evidence_ref"))
    if target is None:
        errors.append(f"{namespace}: unsafe evidence_ref")
        return
    if not target.is_file():
        errors.append(f"{namespace}: evidence file missing")
        return
    if target.stat().st_size <= 0:
        errors.append(f"{namespace}: evidence file empty")
        return
    expected = str(row.get("evidence_sha256") or "").lower()
    if SHA.fullmatch(expected) is None:
        errors.append(f"{namespace}: evidence_sha256 required")
        return
    if _sha(target) != expected:
        errors.append(f"{namespace}: evidence SHA mismatch")


def validate_bundle(registry: dict, registry_sha: str, evidence: dict, evidence_root: Path) -> list[str]:
    errors = list(V5.validate_bundle(registry, registry_sha, evidence, evidence_root))
    _verify_capture(errors, "objective", evidence.get("objective"), evidence_root)
    _verify_capture(errors, "performance_observation", evidence.get("performance_observation"), evidence_root)
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
        print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V6=FAIL")
        print("FINAL_OR_PLAY_READY=FALSE")
        return 1
    print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V6=PASS")
    print(f"PRODUCT={evidence['product']}")
    print(f"EXACT_APK_SHA256={evidence['exact_candidate_sha256']}")
    print("SINGLE_DEVICE_SESSION_BOUND=TRUE")
    print("OBJECTIVE_CAPTURE_SHA256_BOUND=TRUE")
    print("PERFORMANCE_CAPTURE_SHA256_BOUND=TRUE")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
