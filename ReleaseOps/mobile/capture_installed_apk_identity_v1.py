#!/usr/bin/env python3
"""Bind a THF physical-device evidence bundle to the APK bytes installed on the phone.

The tool is intentionally narrow: it does not infer gameplay PASS. It verifies the
connected physical device matches the evidence device fingerprint, resolves the real
package code path with `pm path`, reads the installed base.apk bytes through ADB, hashes
them, and requires an exact match with exact_candidate_sha256.

It also appends the identity transcript to the existing objective capture file and
re-hashes that file so V6/V7 evidence integrity remains consistent.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("thf_capture_v3", HERE / "capture_android_device_evidence_v3.py")
V3CAP = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = V3CAP
SPEC.loader.exec_module(V3CAP)
HEX64 = re.compile(r"^[0-9a-f]{64}$")
DATA_APK = re.compile(r"^/data/app/[A-Za-z0-9_~.=/+-]+/base\.apk$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_pm_paths(text: str) -> list[str]:
    paths=[]
    for raw in text.splitlines():
        line=raw.strip()
        if line.startswith('package:'):
            path=line[len('package:'):]
            if path:
                paths.append(path)
    return paths


def safe_capture_path(root: Path, ref: object) -> Path:
    if not isinstance(ref, str) or not ref or ref.startswith('/'):
        raise RuntimeError('objective evidence_ref must be a safe relative path')
    target=(root/ref).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise RuntimeError('objective evidence_ref escapes evidence root') from exc
    if not target.is_file():
        raise RuntimeError('objective evidence file missing')
    return target


def binary_exec(adb: str, serial: str, *args: str, timeout: int = 120) -> bytes:
    cp=subprocess.run([adb,'-s',serial,'exec-out',*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    if cp.returncode != 0:
        raise RuntimeError(f"adb exec-out failed ({cp.returncode}): {cp.stderr.decode('utf-8','replace')[-1000:]}")
    return cp.stdout


def bind_identity(evidence_path: Path, evidence_root: Path, adb: str) -> dict:
    evidence=json.loads(evidence_path.read_text(encoding='utf-8'))
    package=evidence.get('package')
    expected=str(evidence.get('exact_candidate_sha256') or '').lower()
    if not isinstance(package,str) or not package:
        raise RuntimeError('evidence package missing')
    if HEX64.fullmatch(expected) is None:
        raise RuntimeError('exact candidate SHA invalid')

    serial=V3CAP.one_device(adb)
    emulator,props=V3CAP.detect_emulator(adb,serial)
    if emulator:
        raise RuntimeError('physical phone required; emulator/QEMU device detected')
    device_identity='\n'.join((serial,props['ro.build.fingerprint'],props['ro.product.model'],props['ro.product.manufacturer']))
    actual_fingerprint=hashlib.sha256(device_identity.encode('utf-8','replace')).hexdigest()
    recorded=((evidence.get('device') or {}).get('fingerprint_sha256'))
    if recorded != actual_fingerprint:
        raise RuntimeError('connected phone does not match evidence device fingerprint')

    pm=V3CAP.shell(adb,serial,'pm','path',package,timeout=30)
    if pm.returncode != 0:
        raise RuntimeError('pm path failed for evidence package')
    paths=parse_pm_paths(pm.stdout)
    if len(paths) != 1:
        raise RuntimeError(f'exactly one installed base APK required; found {len(paths)} code paths')
    installed_path=paths[0]
    if DATA_APK.fullmatch(installed_path) is None:
        raise RuntimeError(f'unexpected installed APK path: {installed_path}')

    installed_bytes=binary_exec(adb,serial,'cat',installed_path,timeout=180)
    if not installed_bytes:
        raise RuntimeError('installed base.apk byte read was empty')
    installed_sha=sha256_bytes(installed_bytes)
    if installed_sha != expected:
        raise RuntimeError(f'installed APK SHA mismatch: expected={expected} installed={installed_sha}')

    session=evidence.get('session') or {}
    sid=session.get('session_id')
    now=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    objective=evidence.get('objective')
    if not isinstance(objective,dict):
        raise RuntimeError('objective evidence record missing')
    capture=safe_capture_path(evidence_root,objective.get('evidence_ref'))
    transcript=(
        f"\nINSTALLED_APK_IDENTITY_V1\npackage={package}\ncode_path={installed_path}\n"
        f"installed_apk_sha256={installed_sha}\nmethod=adb-exec-out-cat\nobserved_at_utc={now}\n"
    ).encode('utf-8')
    with capture.open('ab') as f:
        f.write(transcript)
    objective['evidence_sha256']=V3CAP.sha256_file(capture)
    objective['installed_apk_sha256']=installed_sha
    objective['installed_apk_sha_verified']=True
    objective['installed_code_paths']=paths
    objective['installed_apk_hash_method']='adb-exec-out-cat'
    objective['installed_apk_session_id']=sid
    objective['installed_apk_observed_at_utc']=now
    evidence_path.write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return {'package':package,'installed_apk_sha256':installed_sha,'code_path':installed_path,'session_id':sid,'final_or_play_ready':False}


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--evidence',required=True,type=Path)
    ap.add_argument('--evidence-root',required=True,type=Path)
    ap.add_argument('--adb',default='adb')
    ns=ap.parse_args()
    try:
        result=bind_identity(ns.evidence.resolve(),ns.evidence_root.resolve(),ns.adb)
    except Exception as exc:
        print(json.dumps({'status':'BLOCKED','error':str(exc),'final_or_play_ready':False},indent=2),file=sys.stderr)
        return 2
    print(json.dumps({'status':'INSTALLED_APK_IDENTITY_BOUND',**result},indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
