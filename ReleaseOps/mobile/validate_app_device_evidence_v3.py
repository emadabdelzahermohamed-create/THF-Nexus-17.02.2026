#!/usr/bin/env python3
"""THF app physical-device evidence V3.

Layers on V2 and additionally binds the *contents* of objective/check capture files
to one physical-device session, one package, the exact registered APK SHA-256, and
the authoritative source SHA-256. This tool is fail-closed and can never promote a
candidate to FINAL/PLAY_READY.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from validate_app_device_evidence_v2 import validate as validate_v2, safe_file

HEX64 = re.compile(r"^[0-9a-f]{64}$")

REQUIRED_OBJECTIVE_KEYS = {
    "THF_APP_OBJECTIVE_V3", "SESSION_ID", "PACKAGE", "CANDIDATE_SHA256",
    "SOURCE_SHA256", "INSTALLED_APK_SHA256", "HASH_METHOD", "CODE_PATH",
    "PACKAGE_DUMP_PRESENT", "OBSERVED_AT_UTC",
}
REQUIRED_CHECK_KEYS = {
    "THF_APP_EVIDENCE_V3", "SESSION_ID", "PACKAGE", "CANDIDATE_SHA256",
    "SOURCE_SHA256", "CHECK", "RESULT", "OBSERVED_AT_UTC",
}


def parse_canonical_capture(path: Path, required: set[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"non-canonical capture line in {path.name}")
        key, value = line.split("=", 1)
        key = key.strip(); value = value.strip()
        if not key or not value:
            raise ValueError(f"empty canonical capture field in {path.name}")
        if key in values:
            raise ValueError(f"duplicate canonical capture field {key} in {path.name}")
        values[key] = value
    missing = sorted(required - set(values))
    if missing:
        raise ValueError(f"missing canonical capture fields in {path.name}: {','.join(missing)}")
    return values


def current_row(registry: dict, product: str) -> dict:
    rows = [r for r in registry.get("candidates", []) if isinstance(r, dict) and r.get("name") == product]
    if len(rows) != 1:
        raise ValueError(f"registry must contain exactly one current candidate for {product}")
    return rows[0]


def validate(registry: dict, evidence: dict, root: Path) -> list[str]:
    base = validate_v2(registry, evidence, root)
    if base:
        return base
    errors: list[str] = []
    try:
        product = evidence["product"]
        row = current_row(registry, product)
        package = evidence["package"]
        candidate = str(evidence["exact_candidate_sha256"]).lower()
        source_sha = str(row.get("source_sha256") or "").lower()
        if HEX64.fullmatch(source_sha) is None:
            raise ValueError("authoritative candidate source SHA missing/invalid")
        session = evidence["session"]
        sid = session["session_id"]
        objective = evidence["objective"]

        objective_path = safe_file(root, objective["evidence_ref"])
        obj = parse_canonical_capture(objective_path, REQUIRED_OBJECTIVE_KEYS)
        expected_obj = {
            "THF_APP_OBJECTIVE_V3": "1", "SESSION_ID": sid, "PACKAGE": package,
            "CANDIDATE_SHA256": candidate, "SOURCE_SHA256": source_sha,
            "INSTALLED_APK_SHA256": candidate,
            "HASH_METHOD": objective["installed_apk_hash_method"],
            "CODE_PATH": objective["installed_code_paths"][0],
            "PACKAGE_DUMP_PRESENT": "true",
            "OBSERVED_AT_UTC": objective["installed_apk_observed_at_utc"],
        }
        for key, expected in expected_obj.items():
            if obj.get(key) != str(expected):
                raise ValueError(f"objective capture {key} does not match authoritative/structured evidence")

        required_checks = registry.get("required_checks", [])
        for check_name in required_checks:
            item = evidence["checks"][check_name]
            capture_path = safe_file(root, item["evidence_ref"])
            cap = parse_canonical_capture(capture_path, REQUIRED_CHECK_KEYS)
            expected = {
                "THF_APP_EVIDENCE_V3": "1", "SESSION_ID": sid, "PACKAGE": package,
                "CANDIDATE_SHA256": candidate, "SOURCE_SHA256": source_sha,
                "CHECK": check_name, "RESULT": "PASS",
                "OBSERVED_AT_UTC": item["observed_at_utc"],
            }
            for key, expected_value in expected.items():
                if cap.get(key) != str(expected_value):
                    raise ValueError(f"check capture {check_name} field {key} does not match authoritative/structured evidence")

        if evidence.get("final_or_play_ready") is not False:
            raise ValueError("evidence tooling must not self-promote FINAL/PLAY_READY")
    except (KeyError, TypeError, ValueError, UnicodeDecodeError) as exc:
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
        "status": "APP_PHYSICAL_EVIDENCE_V3_VALID",
        "product": evidence["product"],
        "exact_candidate_sha256": evidence["exact_candidate_sha256"],
        "source_sha256": current_row(registry, evidence["product"])["source_sha256"],
        "capture_contents_bound": True,
        "final_or_play_ready": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
