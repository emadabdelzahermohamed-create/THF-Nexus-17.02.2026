#!/usr/bin/env python3
"""Capture V17 foreground-process provenance with Android boot-session binding.

This helper delegates all V16 physical-device/package/APK/registry/gameplay checks to the
V16 capture helper, then captures /proc/sys/kernel/random/boot_id from the same physical
phone and appends a canonical boot UUID proof. It never creates gameplay PASS or promotes
FINAL/PLAY_READY.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("capture_game_process_v16", HERE / "capture_game_process_provenance_v16.py")
V16 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = V16
SPEC.loader.exec_module(V16)

BOOT_METHOD = "ADB_CAT_PROC_BOOT_ID"
BOOT_COMMAND = "cat /proc/sys/kernel/random/boot_id"


def canonical_boot_id(value: str) -> str:
    raw = value.strip().lower()
    try:
        parsed = str(uuid.UUID(raw))
    except ValueError as exc:
        raise RuntimeError("device returned invalid Android boot UUID") from exc
    if raw != parsed:
        raise RuntimeError("device returned non-canonical Android boot UUID")
    return parsed


def capture(evidence_path: Path, capability: str, evidence_root: Path, out: Path, adb: str = "adb") -> dict:
    result = V16.capture(evidence_path, capability, evidence_root, out, adb)

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    serial = V16.one_device(adb)
    fingerprint, _ = V16.device_fingerprint(adb, serial)
    expected = ((evidence.get("device") or {}).get("fingerprint_sha256"))
    if fingerprint != expected:
        raise RuntimeError("connected physical device changed before boot-id capture")

    cp = V16.shell(adb, serial, "cat", "/proc/sys/kernel/random/boot_id")
    if cp.returncode != 0:
        raise RuntimeError("Android boot-id capture failed")
    boot_id = canonical_boot_id(cp.stdout)

    with out.open("a", encoding="utf-8") as f:
        f.write("THF_ANDROID_BOOT_ID=" + boot_id + "\n")
        f.write("THF_BOOT_ID_CAPTURE_METHOD=" + BOOT_METHOD + "\n")
        f.write("THF_BOOT_ID_CAPTURE_COMMAND=" + BOOT_COMMAND + "\n")
        f.write("THF_BOOT_ID_CAPTURE_EXIT_CODE=0\n")

    result = dict(result)
    result.update({
        "status": "CAPTURED_V17_BOOT_BOUND_PROCESS_PROVENANCE",
        "android_boot_id": boot_id,
        "evidence_sha256": V16.sha256_file(out),
        "final_or_play_ready": False,
    })
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--evidence-root", type=Path, required=True)
    ap.add_argument("--capability", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--adb", default=os.environ.get("ADB", "adb"))
    ns = ap.parse_args()
    try:
        result = capture(ns.evidence, ns.capability, ns.evidence_root, ns.out, ns.adb)
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc), "final_or_play_ready": False}, indent=2), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
