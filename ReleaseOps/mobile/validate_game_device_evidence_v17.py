#!/usr/bin/env python3
"""V17: bind all gameplay capability process proofs to one Android boot session.

V16 binds foreground-process provenance to the physical device, exact APK, registry and
observation timestamp. V17 additionally requires the Linux/Android boot UUID captured
from /proc/sys/kernel/random/boot_id to be present in every capability process proof,
and requires every required capability in one acceptance bundle to carry the exact same
boot UUID. This rejects same-device evidence replay across a reboot.

This validator is fail-closed and cannot promote FINAL/PLAY_READY by itself.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys
import uuid

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("thf_device_v16", HERE / "validate_game_device_evidence_v16.py")
V16 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = V16
SPEC.loader.exec_module(V16)
V14, V3, V4, V15 = V16.V14, V16.V3, V16.V4, V16.V15

BOOT_METHOD = "ADB_CAT_PROC_BOOT_ID"
BOOT_COMMAND = "cat /proc/sys/kernel/random/boot_id"


def _boot_uuid(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = uuid.UUID(value.strip())
    except (ValueError, AttributeError):
        return None
    canonical = str(parsed)
    return canonical if value.strip().lower() == canonical else None


def validate_bundle(registry: dict, registry_sha: str, evidence: dict, evidence_root: Path) -> list[str]:
    errors = list(V16.validate_bundle(registry, registry_sha, evidence, evidence_root))
    product = evidence.get("product")
    proc = evidence.get("process_provenance") if isinstance(evidence.get("process_provenance"), dict) else {}

    req = dict(V14.BASE)
    req.update(V14.PRODUCT.get(product, {}))
    seen_boot_ids: dict[str, str] = {}

    for key in req:
        row = proc.get(key) if isinstance(proc.get(key), dict) else {}
        path = V4._safe_evidence_path(evidence_root, row.get("evidence_ref"))
        if path is None or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")

        raw_boot = V15.one(text, "THF_ANDROID_BOOT_ID")
        boot_id = _boot_uuid(raw_boot)
        if boot_id is None:
            errors.append(f"V17 {key}: canonical Android boot UUID required")
        else:
            seen_boot_ids[key] = boot_id

        if V15.one(text, "THF_BOOT_ID_CAPTURE_METHOD") != BOOT_METHOD:
            errors.append(f"V17 {key}: THF_BOOT_ID_CAPTURE_METHOD mismatch")
        if V15.one(text, "THF_BOOT_ID_CAPTURE_COMMAND") != BOOT_COMMAND:
            errors.append(f"V17 {key}: THF_BOOT_ID_CAPTURE_COMMAND mismatch")
        if V15.one(text, "THF_BOOT_ID_CAPTURE_EXIT_CODE") != "0":
            errors.append(f"V17 {key}: THF_BOOT_ID_CAPTURE_EXIT_CODE mismatch")

    if len(seen_boot_ids) == len(req) and len(set(seen_boot_ids.values())) != 1:
        errors.append("V17: required gameplay capability proofs span multiple Android boot sessions")

    if evidence.get("final_or_play_ready") is not False:
        errors.append("V17 cannot self-promote FINAL/PLAY_READY")
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
        print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V17=FAIL")
        print("FINAL_OR_PLAY_READY=FALSE")
        return 1
    print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V17=PASS")
    print("ANDROID_BOOT_SESSION_BOUND=TRUE")
    print("CROSS_REBOOT_GAMEPLAY_EVIDENCE_REJECTED=TRUE")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
