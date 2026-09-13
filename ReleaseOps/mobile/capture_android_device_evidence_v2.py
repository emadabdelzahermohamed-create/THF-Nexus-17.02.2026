#!/usr/bin/env python3
"""Capture objective Android device evidence for an exact THF candidate APK.

This collector is intentionally fail-closed. It NEVER turns manual gameplay/touch/
orientation/network assertions into PASS automatically. It only proves objective facts
that adb can observe and emits explicit false values for human-observation gates.

No production signing, Play publishing, cloud mutation, or secret handling occurs here.
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
import time


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], *, timeout: int = 30, check: bool = False) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    if check and cp.returncode != 0:
        raise RuntimeError(f"command failed ({cp.returncode}): {' '.join(cmd)}\n{cp.stdout}")
    return cp


def one_device(adb: str) -> str:
    cp = run([adb, 'devices'], check=True)
    rows=[]
    for line in cp.stdout.splitlines()[1:]:
        cols=line.strip().split()
        if len(cols) >= 2 and cols[1] == 'device':
            rows.append(cols[0])
    if len(rows) != 1:
        raise RuntimeError(f'exactly one authorized adb device required; found {len(rows)}')
    return rows[0]


def prop(adb: str, serial: str, key: str) -> str:
    return run([adb, '-s', serial, 'shell', 'getprop', key]).stdout.strip()


def shell(adb: str, serial: str, *args: str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return run([adb, '-s', serial, 'shell', *args], timeout=timeout)


def launch_package(adb: str, serial: str, package: str) -> tuple[bool, str]:
    shell(adb, serial, 'am', 'force-stop', package)
    cp = shell(adb, serial, 'monkey', '-p', package, '-c', 'android.intent.category.LAUNCHER', '1', timeout=30)
    time.sleep(4)
    pid = shell(adb, serial, 'pidof', package).stdout.strip()
    return cp.returncode == 0 and bool(pid), pid


def collect(args: argparse.Namespace) -> dict:
    apk = Path(args.apk).resolve()
    if not apk.is_file():
        raise RuntimeError(f'APK missing: {apk}')
    actual_sha = sha256_file(apk)
    if actual_sha.lower() != args.expected_sha256.lower():
        raise RuntimeError(f'exact candidate SHA mismatch: expected={args.expected_sha256.lower()} actual={actual_sha.lower()}')

    serial = one_device(args.adb)
    before_log = run([args.adb, '-s', serial, 'logcat', '-c'])
    install = run([args.adb, '-s', serial, 'install', '-r', '-t', str(apk)], timeout=180)
    install_pass = install.returncode == 0 and 'Success' in install.stdout

    launch_pass = False
    pid = ''
    background_resume_pass = False
    if install_pass:
        launch_pass, pid = launch_package(args.adb, serial, args.package)
        if launch_pass:
            shell(args.adb, serial, 'input', 'keyevent', 'KEYCODE_HOME')
            time.sleep(1)
            resumed, resumed_pid = launch_package(args.adb, serial, args.package)
            background_resume_pass = resumed and bool(resumed_pid)
            pid = resumed_pid or pid

    meminfo = shell(args.adb, serial, 'dumpsys', 'meminfo', args.package, timeout=45).stdout if install_pass else ''
    gfxinfo = shell(args.adb, serial, 'dumpsys', 'gfxinfo', args.package, 'framestats', timeout=45).stdout if install_pass else ''
    thermal = shell(args.adb, serial, 'dumpsys', 'thermalservice', timeout=45).stdout if install_pass else ''
    display = shell(args.adb, serial, 'dumpsys', 'display', timeout=45).stdout if install_pass else ''
    window = shell(args.adb, serial, 'dumpsys', 'window', 'windows', timeout=45).stdout if install_pass else ''
    package_dump = shell(args.adb, serial, 'dumpsys', 'package', args.package, timeout=45).stdout if install_pass else ''
    logcat = run([args.adb, '-s', serial, 'logcat', '-d', '-v', 'threadtime'], timeout=45).stdout

    total_pss_kb = None
    m = re.search(r'^\s*TOTAL\s+(\d+)', meminfo, re.M)
    if m:
        total_pss_kb = int(m.group(1))
    frame_rows = sum(1 for line in gfxinfo.splitlines() if re.match(r'^\s*\d+,\d+,', line))
    fatal_markers = []
    for marker in ('FATAL EXCEPTION', 'ANR in ', 'Fatal signal ', 'Process has died:'):
        if marker in logcat:
            fatal_markers.append(marker)

    result = {
        'schema': 'thf-android-device-evidence-v2',
        'product': args.product,
        'package': args.package,
        'exact_candidate_sha256': actual_sha,
        'device': {
            'serial_redacted': serial[-4:] if len(serial) >= 4 else 'redacted',
            'manufacturer': prop(args.adb, serial, 'ro.product.manufacturer'),
            'model': prop(args.adb, serial, 'ro.product.model'),
            'android_release': prop(args.adb, serial, 'ro.build.version.release'),
            'sdk': prop(args.adb, serial, 'ro.build.version.sdk'),
        },
        'objective': {
            'install_output': install.stdout[-2000:],
            'pid_observed': bool(pid),
            'total_pss_kb': total_pss_kb,
            'framestats_rows': frame_rows,
            'fatal_runtime_markers': fatal_markers,
            'display_snapshot_present': bool(display.strip()),
            'window_snapshot_present': bool(window.strip()),
            'package_dump_present': bool(package_dump.strip()),
            'thermal_snapshot_present': bool(thermal.strip()),
            'logcat_cleared_before_test': before_log.returncode == 0,
        },
        'install_pass': install_pass,
        'launch_pass': launch_pass,
        'background_resume_pass': background_resume_pass,
        'crash_free_smoke_pass': install_pass and launch_pass and background_resume_pass and not fatal_markers,
        # Manual/interactive observations remain false until a human/device lab verifies them.
        'touch_pass': False,
        'orientation_layout_pass': False,
        'offline_network_transition_pass': False,
        'core_user_journey_pass': False,
        'backend_https_pass': False,
        'backend_health_auth_pass': False,
        'avatar_or_player_load_pass': False,
        'movement_camera_pass': False,
        'gameplay_interaction_pass': False,
        'combat_pass': False,
        'sensor_motion_pass': False,
        'fps_ram_thermal_observed': bool(total_pss_kb is not None and frame_rows >= 0 and thermal.strip()),
        'final_status': 'DEVICE_INCOMPLETE',
        'notes': [
            'Objective adb evidence captured without production signing or publishing.',
            'Manual gameplay/touch/orientation/offline-network gates are intentionally not auto-promoted.',
        ],
    }
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--product', required=True)
    ap.add_argument('--package', required=True)
    ap.add_argument('--apk', required=True)
    ap.add_argument('--expected-sha256', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--adb', default=os.environ.get('ADB', 'adb'))
    args = ap.parse_args()
    if not re.fullmatch(r'[0-9a-fA-F]{64}', args.expected_sha256):
        raise SystemExit('expected SHA-256 must be exactly 64 hex characters')
    try:
        result = collect(args)
    except Exception as exc:
        print(json.dumps({'status': 'BLOCKED', 'error': str(exc)}, indent=2), file=sys.stderr)
        return 2
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'CAPTURED', 'out': str(out), 'exact_candidate_sha256': result['exact_candidate_sha256']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
