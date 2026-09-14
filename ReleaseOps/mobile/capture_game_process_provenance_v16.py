#!/usr/bin/env python3
"""Capture V16 foreground-process provenance for one already-observed gameplay capability.

This helper does not create gameplay PASS. It only captures process identity for a manual
observation that already has a real, SHA-bound gameplay evidence file. It verifies the
same physical-device fingerprint, exact package, exact candidate/registry bindings, and
that the package is the currently resumed Android activity with a live PID.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

SHA = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)


def one_device(adb: str) -> str:
    cp = run([adb, "devices"])
    if cp.returncode != 0:
        raise RuntimeError("adb devices failed")
    rows = []
    for line in cp.stdout.splitlines()[1:]:
        cols = line.strip().split()
        if len(cols) >= 2 and cols[1] == "device":
            rows.append(cols[0])
    if len(rows) != 1:
        raise RuntimeError(f"exactly one authorized adb device required; found {len(rows)}")
    return rows[0]


def shell(adb: str, serial: str, *args: str) -> subprocess.CompletedProcess[str]:
    return run([adb, "-s", serial, "shell", *args])


def prop(adb: str, serial: str, key: str) -> str:
    cp = shell(adb, serial, "getprop", key)
    if cp.returncode != 0:
        raise RuntimeError(f"getprop failed: {key}")
    return cp.stdout.strip()


def device_fingerprint(adb: str, serial: str) -> tuple[str, dict[str, str]]:
    props = {
        "ro.build.fingerprint": prop(adb, serial, "ro.build.fingerprint"),
        "ro.product.model": prop(adb, serial, "ro.product.model"),
        "ro.product.manufacturer": prop(adb, serial, "ro.product.manufacturer"),
        "ro.kernel.qemu": prop(adb, serial, "ro.kernel.qemu"),
        "ro.boot.qemu": prop(adb, serial, "ro.boot.qemu"),
        "ro.hardware": prop(adb, serial, "ro.hardware"),
    }
    joined = " ".join(props.values()).lower()
    if props["ro.kernel.qemu"] == "1" or props["ro.boot.qemu"] == "1" or any(
        token in joined for token in ("ranchu", "goldfish", "sdk_gphone", "generic_x86", "android sdk built for", "emulator")
    ):
        raise RuntimeError("physical phone required; emulator/QEMU device detected")
    identity = "\n".join((serial, props["ro.build.fingerprint"], props["ro.product.model"], props["ro.product.manufacturer"]))
    return hashlib.sha256(identity.encode("utf-8", "replace")).hexdigest(), props


def load_evidence(path: Path, capability: str, evidence_root: Path) -> tuple[dict, dict, str]:
    evidence = json.loads(path.read_text(encoding="utf-8"))
    package = evidence.get("package")
    if not isinstance(package, str) or not package.strip():
        raise RuntimeError("evidence package missing")
    exact_sha = evidence.get("exact_candidate_sha256")
    registry_sha = evidence.get("registry_sha256")
    if not isinstance(exact_sha, str) or SHA.fullmatch(exact_sha) is None:
        raise RuntimeError("evidence exact candidate SHA invalid")
    if not isinstance(registry_sha, str) or SHA.fullmatch(registry_sha) is None:
        raise RuntimeError("evidence registry SHA invalid")
    row = (evidence.get("manual_observations") or {}).get(capability)
    if not isinstance(row, dict) or row.get("pass") is not True:
        raise RuntimeError("capability must already have a manual PASS observation")
    observed = row.get("observed_at_utc")
    if not isinstance(observed, str) or not observed.endswith("Z"):
        raise RuntimeError("capability observed_at_utc missing/invalid")
    ref = row.get("evidence_ref")
    if not isinstance(ref, str) or not ref.strip():
        raise RuntimeError("capability gameplay evidence_ref missing")
    root = evidence_root.resolve()
    gameplay = (root / ref).resolve()
    if root != gameplay and root not in gameplay.parents:
        raise RuntimeError("unsafe gameplay evidence_ref")
    if not gameplay.is_file() or gameplay.stat().st_size <= 0:
        raise RuntimeError("gameplay evidence file missing/empty")
    gameplay_sha = row.get("evidence_sha256")
    if not isinstance(gameplay_sha, str) or SHA.fullmatch(gameplay_sha) is None or sha256_file(gameplay) != gameplay_sha:
        raise RuntimeError("gameplay evidence SHA mismatch")
    return evidence, row, gameplay_sha


def capture(evidence_path: Path, capability: str, evidence_root: Path, out: Path, adb: str = "adb") -> dict:
    evidence, observation, gameplay_sha = load_evidence(evidence_path, capability, evidence_root)
    serial = one_device(adb)
    fp, _ = device_fingerprint(adb, serial)
    expected_fp = ((evidence.get("device") or {}).get("fingerprint_sha256"))
    if fp != expected_fp:
        raise RuntimeError("connected physical device fingerprint does not match evidence session")

    package = evidence["package"]
    activities = shell(adb, serial, "dumpsys", "activity", "activities")
    pidof = shell(adb, serial, "pidof", package)
    if activities.returncode != 0:
        raise RuntimeError("dumpsys activity activities failed")
    if pidof.returncode != 0:
        raise RuntimeError("pidof failed")
    pid = pidof.stdout.strip()
    if not re.fullmatch(r"[1-9]\d*", pid):
        raise RuntimeError("one live numeric package PID required")

    resumed_lines = [line.strip() for line in activities.stdout.splitlines() if "mResumedActivity" in line or "topResumedActivity" in line]
    if not resumed_lines or not any(package in line for line in resumed_lines):
        raise RuntimeError("exact game package is not the resumed foreground activity")

    session = evidence.get("session") or {}
    sid = session.get("session_id")
    if not isinstance(sid, str) or not sid:
        raise RuntimeError("session_id missing")

    lines = [
        "THF_SESSION_ID=" + sid,
        "THF_PACKAGE=" + package,
        "THF_CAPABILITY=" + capability,
        "THF_FOREGROUND_PACKAGE=" + package,
        "THF_FOREGROUND_PID=" + pid,
        "THF_RESUMED_PID=" + pid,
        "THF_ACTIVITY_RESUMED=TRUE",
        "THF_PROCESS_ALIVE_AFTER=TRUE",
        "THF_PROCESS_CAPTURE_METHOD=ADB_DUMPSYS_ACTIVITY_PIDOF",
        "THF_GAMEPLAY_EVIDENCE_SHA256=" + gameplay_sha,
        "THF_DEVICE_FINGERPRINT_SHA256=" + fp,
        "THF_EXACT_APK_SHA256=" + evidence["exact_candidate_sha256"],
        "THF_REGISTRY_SHA256=" + evidence["registry_sha256"],
        "THF_OBSERVED_AT_UTC=" + observation["observed_at_utc"],
        "THF_ACTIVITY_DUMPSYS_EXIT_CODE=0",
        "THF_PIDOF_EXIT_CODE=0",
        "",
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    digest = sha256_file(out)
    return {
        "status": "CAPTURED_V16_PROCESS_PROVENANCE",
        "capability": capability,
        "package": package,
        "pid": int(pid),
        "evidence_ref": str(out),
        "evidence_sha256": digest,
        "final_or_play_ready": False,
    }


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
