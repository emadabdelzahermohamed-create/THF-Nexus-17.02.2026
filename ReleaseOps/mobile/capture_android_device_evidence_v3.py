#!/usr/bin/env python3
"""Capture objective physical Android evidence for an exact registered THF game APK.

V3 changes:
- derives package/SHA from the current device-candidate registry rather than CLI duplication;
- binds output to SHA-256 of the exact registry bytes;
- rejects emulators/QEMU/ranchu/goldfish devices;
- proves background/resume by retaining the same PID (no force-stop on resume);
- emits product-specific manual evidence slots but never auto-promotes them.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

from validate_game_device_evidence_v3 import COMMON_MANUAL, PRODUCT_MANUAL


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(cmd: list[str], *, timeout: int = 30, check: bool = False) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    if check and cp.returncode != 0:
        raise RuntimeError(f"command failed ({cp.returncode}): {' '.join(cmd)}\n{cp.stdout}")
    return cp


def one_device(adb: str) -> str:
    cp = run([adb, "devices"], check=True)
    rows = []
    for line in cp.stdout.splitlines()[1:]:
        cols = line.strip().split()
        if len(cols) >= 2 and cols[1] == "device":
            rows.append(cols[0])
    if len(rows) != 1:
        raise RuntimeError(f"exactly one authorized adb device required; found {len(rows)}")
    return rows[0]


def prop(adb: str, serial: str, key: str) -> str:
    return run([adb, "-s", serial, "shell", "getprop", key]).stdout.strip()


def shell(adb: str, serial: str, *args: str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return run([adb, "-s", serial, "shell", *args], timeout=timeout)


def foreground_launch(adb: str, serial: str, package: str) -> tuple[bool, str]:
    cp = shell(adb, serial, "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1", timeout=30)
    time.sleep(4)
    pid = shell(adb, serial, "pidof", package).stdout.strip()
    return cp.returncode == 0 and bool(pid), pid


def cold_launch(adb: str, serial: str, package: str) -> tuple[bool, str]:
    shell(adb, serial, "am", "force-stop", package)
    time.sleep(1)
    return foreground_launch(adb, serial, package)


def resume_without_restart(adb: str, serial: str, package: str, original_pid: str) -> tuple[bool, str]:
    shell(adb, serial, "input", "keyevent", "KEYCODE_HOME")
    time.sleep(2)
    background_pid = shell(adb, serial, "pidof", package).stdout.strip()
    if not background_pid or background_pid != original_pid:
        return False, background_pid
    resumed, resumed_pid = foreground_launch(adb, serial, package)
    return resumed and resumed_pid == original_pid, resumed_pid


def candidate(registry: dict, product: str) -> dict:
    rows = [r for r in registry.get("candidates", []) if isinstance(r, dict) and r.get("app") == product]
    if len(rows) != 1:
        raise RuntimeError(f"current registry must contain exactly one candidate for {product}; found {len(rows)}")
    return rows[0]


def detect_emulator(adb: str, serial: str) -> tuple[bool, dict[str, str]]:
    keys = {
        "ro.kernel.qemu": prop(adb, serial, "ro.kernel.qemu"),
        "ro.boot.qemu": prop(adb, serial, "ro.boot.qemu"),
        "ro.hardware": prop(adb, serial, "ro.hardware"),
        "ro.product.model": prop(adb, serial, "ro.product.model"),
        "ro.product.manufacturer": prop(adb, serial, "ro.product.manufacturer"),
        "ro.build.fingerprint": prop(adb, serial, "ro.build.fingerprint"),
    }
    joined = " ".join(keys.values()).lower()
    emulator = (
        keys["ro.kernel.qemu"] == "1"
        or keys["ro.boot.qemu"] == "1"
        or any(x in joined for x in ("ranchu", "goldfish", "sdk_gphone", "generic_x86", "android sdk built for", "emulator"))
    )
    return emulator, keys


def manual_template(product: str) -> dict:
    return {
        key: {"pass": False, "observed_at_utc": "", "evidence_ref": ""}
        for key in COMMON_MANUAL + PRODUCT_MANUAL[product]
    }


def collect(args: argparse.Namespace) -> dict:
    registry_path = Path(args.registry).resolve()
    raw_registry = registry_path.read_bytes()
    registry = json.loads(raw_registry)
    registry_sha = sha256_bytes(raw_registry)
    row = candidate(registry, args.product)
    package = str(row["package"])
    expected_sha = str(row["apk_sha256"]).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
        raise RuntimeError("registry candidate APK SHA invalid")

    apk = Path(args.apk).resolve()
    if not apk.is_file():
        raise RuntimeError(f"APK missing: {apk}")
    actual_sha = sha256_file(apk)
    if actual_sha != expected_sha:
        raise RuntimeError(f"exact candidate SHA mismatch: registry={expected_sha} actual={actual_sha}")

    serial = one_device(args.adb)
    emulator_detected, props = detect_emulator(args.adb, serial)
    if emulator_detected:
        raise RuntimeError("physical phone required; emulator/QEMU device detected")

    device_identity = "\n".join((serial, props["ro.build.fingerprint"], props["ro.product.model"], props["ro.product.manufacturer"]))
    fingerprint_sha = hashlib.sha256(device_identity.encode("utf-8", "replace")).hexdigest()

    before_log = run([args.adb, "-s", serial, "logcat", "-c"])
    install = run([args.adb, "-s", serial, "install", "-r", "-t", str(apk)], timeout=180)
    install_pass = install.returncode == 0 and "Success" in install.stdout

    cold_launch_pass = False
    background_resume_pass = False
    pid = ""
    if install_pass:
        cold_launch_pass, pid = cold_launch(args.adb, serial, package)
        if cold_launch_pass and pid:
            background_resume_pass, resumed_pid = resume_without_restart(args.adb, serial, package, pid)
            pid = resumed_pid or pid

    meminfo = shell(args.adb, serial, "dumpsys", "meminfo", package, timeout=45).stdout if install_pass else ""
    gfxinfo = shell(args.adb, serial, "dumpsys", "gfxinfo", package, "framestats", timeout=45).stdout if install_pass else ""
    thermal = shell(args.adb, serial, "dumpsys", "thermalservice", timeout=45).stdout if install_pass else ""
    display = shell(args.adb, serial, "dumpsys", "display", timeout=45).stdout if install_pass else ""
    window = shell(args.adb, serial, "dumpsys", "window", "windows", timeout=45).stdout if install_pass else ""
    package_dump = shell(args.adb, serial, "dumpsys", "package", package, timeout=45).stdout if install_pass else ""
    logcat = run([args.adb, "-s", serial, "logcat", "-d", "-v", "threadtime"], timeout=45).stdout

    total_pss_kb = None
    m = re.search(r"^\s*TOTAL\s+(\d+)", meminfo, re.M)
    if m:
        total_pss_kb = int(m.group(1))
    frame_rows = sum(1 for line in gfxinfo.splitlines() if re.match(r"^\s*\d+,\d+,", line))
    fatal_markers = [m for m in ("FATAL EXCEPTION", "ANR in ", "Fatal signal ", "Process has died:") if m in logcat]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "schema": "thf-android-device-evidence-v3",
        "captured_at_utc": now,
        "product": args.product,
        "registry_sha256": registry_sha,
        "package": package,
        "exact_candidate_sha256": actual_sha,
        "device": {
            "physical_device": True,
            "emulator_detected": False,
            "fingerprint_sha256": fingerprint_sha,
            "manufacturer": props["ro.product.manufacturer"],
            "model": props["ro.product.model"],
            "android_release": prop(args.adb, serial, "ro.build.version.release"),
            "sdk": prop(args.adb, serial, "ro.build.version.sdk"),
            "serial_suffix_redacted": serial[-4:] if len(serial) >= 4 else "redacted",
        },
        "objective": {
            "install_pass": install_pass,
            "cold_launch_pass": cold_launch_pass,
            "background_resume_pass": background_resume_pass,
            "same_pid_resume_required": True,
            "pid_observed": bool(pid),
            "total_pss_kb": total_pss_kb,
            "framestats_rows": frame_rows,
            "fatal_runtime_markers": fatal_markers,
            "display_snapshot_present": bool(display.strip()),
            "window_snapshot_present": bool(window.strip()),
            "package_dump_present": bool(package_dump.strip()),
            "thermal_snapshot_present": bool(thermal.strip()),
            "logcat_cleared_before_test": before_log.returncode == 0,
            "crash_free_smoke_pass": install_pass and cold_launch_pass and background_resume_pass and not fatal_markers,
            "install_output_tail": install.stdout[-2000:],
        },
        "performance_observation": {
            "fps_observed": None,
            "ram_mb_observed": (round(total_pss_kb / 1024.0, 2) if total_pss_kb else None),
            "thermal_status_observed": None,
            "observation_seconds": None,
        },
        "manual_observations": manual_template(args.product),
        "online_state_not_faked": False,
        "local_mode_genuinely_local": False,
        "final_or_play_ready": False,
        "notes": [
            "Objective evidence only; manual gameplay fields intentionally remain false until observed on this exact APK/device.",
            "Background/resume PASS requires the same process PID before and after HOME/foreground transition.",
            "No arbitrary performance threshold is applied; FPS/RAM/thermal observations must be recorded during the gameplay session.",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True)
    ap.add_argument("--product", required=True, choices=sorted(PRODUCT_MANUAL))
    ap.add_argument("--apk", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--adb", default=os.environ.get("ADB", "adb"))
    args = ap.parse_args()
    try:
        result = collect(args)
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "CAPTURED_OBJECTIVE_ONLY",
        "out": str(out),
        "product": result["product"],
        "exact_candidate_sha256": result["exact_candidate_sha256"],
        "physical_device": True,
        "final_or_play_ready": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
