#!/usr/bin/env python3
"""V7 physical-phone evidence validator.

Extends V6 by proving that the APK bytes actually installed on the physical phone match
the exact registered candidate APK SHA-256. Pre-install hashing alone is insufficient:
V7 requires a post-install byte read from the package's real /data/app/.../base.apk and
binds that identity proof to the same physical-device session as all other observations.

This validator is fail-closed and never promotes FINAL/PLAY_READY by itself.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("thf_device_v6", HERE / "validate_game_device_evidence_v6.py")
V6 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = V6
SPEC.loader.exec_module(V6)
V5 = V6.V5
V4 = V6.V4
V3 = V6.V3
SHA = re.compile(r"^[0-9a-f]{64}$")


def validate_bundle(registry: dict, registry_sha: str, evidence: dict, evidence_root: Path) -> list[str]:
    errors = list(V6.validate_bundle(registry, registry_sha, evidence, evidence_root))
    objective = evidence.get("objective")
    if not isinstance(objective, dict):
        errors.append("objective: missing record")
        return errors

    installed_sha = objective.get("installed_apk_sha256")
    expected_sha = evidence.get("exact_candidate_sha256")
    if not isinstance(installed_sha, str) or SHA.fullmatch(installed_sha) is None:
        errors.append("objective.installed_apk_sha256: lowercase SHA-256 required")
    elif installed_sha != expected_sha:
        errors.append("objective.installed_apk_sha256: installed bytes do not match exact candidate")

    if objective.get("installed_apk_sha_verified") is not True:
        errors.append("objective.installed_apk_sha_verified: true required")

    paths = objective.get("installed_code_paths")
    if not isinstance(paths, list) or len(paths) != 1:
        errors.append("objective.installed_code_paths: exactly one installed base APK required")
    else:
        path = paths[0]
        if not isinstance(path, str) or not path.startswith("/data/app/") or not path.endswith("/base.apk"):
            errors.append("objective.installed_code_paths: physical /data/app/.../base.apk path required")

    method = objective.get("installed_apk_hash_method")
    if method not in ("adb-exec-out-cat", "adb-pull"):
        errors.append("objective.installed_apk_hash_method: approved byte-read method required")

    if objective.get("package_dump_present") is not True:
        errors.append("objective.package_dump_present: true required")

    session = evidence.get("session")
    if not isinstance(session, dict):
        errors.append("session: missing record")
    else:
        sid = session.get("session_id")
        if objective.get("installed_apk_session_id") != sid:
            errors.append("objective.installed_apk_session_id: session_id mismatch")
        observed = V5._utc(objective.get("installed_apk_observed_at_utc"))
        started = V5._utc(session.get("started_at_utc"))
        ended = V5._utc(session.get("ended_at_utc"))
        if observed is None:
            errors.append("objective.installed_apk_observed_at_utc: strict UTC timestamp required")
        elif started is not None and ended is not None and not (started <= observed <= ended):
            errors.append("objective.installed_apk_observed_at_utc: observation outside declared session interval")

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
        print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V7=FAIL")
        print("FINAL_OR_PLAY_READY=FALSE")
        return 1
    print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V7=PASS")
    print(f"PRODUCT={evidence['product']}")
    print(f"EXACT_APK_SHA256={evidence['exact_candidate_sha256']}")
    print("INSTALLED_APK_BYTES_MATCH_CANDIDATE=TRUE")
    print("INSTALLED_APK_IDENTITY_SESSION_BOUND=TRUE")
    print("SINGLE_DEVICE_SESSION_BOUND=TRUE")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
