#!/usr/bin/env python3
"""Fail-closed validator for THF application physical-device evidence.

This validator never promotes a candidate. It binds a phone evidence bundle to the
current authoritative app registry and requires proof that the bytes installed on the
physical phone equal the exact registered APK SHA-256.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

HEX64 = re.compile(r"^[0-9a-f]{64}$")
DATA_APK = re.compile(r"^/data/app/[A-Za-z0-9_~.=/+\-]+/base\.apk$")
ALLOWED_HASH_METHODS = {"adb-exec-out-cat", "adb-pull"}


def parse_utc(value: object) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("UTC timestamp missing")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return dt.astimezone(timezone.utc)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_file(root: Path, ref: object) -> Path:
    if not isinstance(ref, str) or not ref or ref.startswith("/"):
        raise ValueError("evidence_ref must be a safe relative path")
    target = (root / ref).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("evidence_ref escapes evidence root") from exc
    if not target.is_file() or target.stat().st_size <= 0:
        raise ValueError(f"evidence file missing/empty: {ref}")
    return target


def current_candidate(registry: dict, product: str) -> dict:
    rows = [r for r in registry.get("candidates", []) if isinstance(r, dict) and r.get("name") == product]
    if len(rows) != 1:
        raise ValueError(f"registry must contain exactly one current candidate for {product}")
    return rows[0]


def validate(registry: dict, evidence: dict, root: Path) -> list[str]:
    errors: list[str] = []
    try:
        product = evidence.get("product")
        if not isinstance(product, str) or not product:
            raise ValueError("product missing")
        row = current_candidate(registry, product)
        expected_sha = str(row.get("apk_sha256") or "").lower()
        expected_package = row.get("package")
        if HEX64.fullmatch(expected_sha) is None:
            raise ValueError("registry candidate SHA invalid")
        if row.get("status") != "PENDING_PHYSICAL_PHONE":
            raise ValueError("current candidate truth must remain PENDING_PHYSICAL_PHONE before acceptance")
        if evidence.get("package") != expected_package:
            raise ValueError("package does not match current registry candidate")
        if str(evidence.get("exact_candidate_sha256") or "").lower() != expected_sha:
            raise ValueError("evidence candidate SHA does not match current registry candidate")

        device = evidence.get("device") or {}
        if device.get("physical_device") is not True or device.get("emulator_detected") is not False:
            raise ValueError("real physical Android device required")
        if HEX64.fullmatch(str(device.get("fingerprint_sha256") or "").lower()) is None:
            raise ValueError("device fingerprint SHA missing/invalid")

        session = evidence.get("session") or {}
        sid = session.get("session_id")
        if not isinstance(sid, str) or not sid.strip():
            raise ValueError("session_id missing")
        started = parse_utc(session.get("started_at_utc"))
        ended = parse_utc(session.get("ended_at_utc"))
        if ended < started:
            raise ValueError("session end precedes start")

        objective = evidence.get("objective") or {}
        if objective.get("installed_apk_sha_verified") is not True:
            raise ValueError("installed APK SHA is not verified")
        if str(objective.get("installed_apk_sha256") or "").lower() != expected_sha:
            raise ValueError("installed phone APK bytes do not equal exact candidate SHA")
        paths = objective.get("installed_code_paths")
        if not isinstance(paths, list) or len(paths) != 1 or not isinstance(paths[0], str) or DATA_APK.fullmatch(paths[0]) is None:
            raise ValueError("exactly one /data/app/.../base.apk code path required")
        if objective.get("installed_apk_hash_method") not in ALLOWED_HASH_METHODS:
            raise ValueError("unapproved installed APK byte-read/hash method")
        if objective.get("installed_apk_session_id") != sid:
            raise ValueError("installed APK identity proof is not bound to this device session")
        observed = parse_utc(objective.get("installed_apk_observed_at_utc"))
        if not (started <= observed <= ended):
            raise ValueError("installed APK identity timestamp lies outside device session")
        if objective.get("package_dump_present") is not True:
            raise ValueError("package registration dump is required")

        capture = safe_file(root, objective.get("evidence_ref"))
        recorded_capture_sha = str(objective.get("evidence_sha256") or "").lower()
        if HEX64.fullmatch(recorded_capture_sha) is None or sha256_file(capture) != recorded_capture_sha:
            raise ValueError("objective capture SHA mismatch")

        checks = evidence.get("checks")
        required = registry.get("required_checks", [])
        if not isinstance(checks, dict):
            raise ValueError("checks map missing")
        missing = [name for name in required if (checks.get(name) or {}).get("pass") is not True]
        if missing:
            raise ValueError("required physical checks not PASS: " + ",".join(missing))
        for name in required:
            item = checks[name]
            p = safe_file(root, item.get("evidence_ref"))
            digest = str(item.get("evidence_sha256") or "").lower()
            if HEX64.fullmatch(digest) is None or sha256_file(p) != digest:
                raise ValueError(f"evidence SHA mismatch for check {name}")
            observed_check = parse_utc(item.get("observed_at_utc"))
            if not (started <= observed_check <= ended):
                raise ValueError(f"check {name} timestamp lies outside device session")

        if evidence.get("final_or_play_ready") is not False:
            raise ValueError("evidence tooling must not self-promote FINAL/PLAY_READY")
    except (KeyError, TypeError, ValueError) as exc:
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
    print(json.dumps({"status": "APP_PHYSICAL_EVIDENCE_VALID", "product": evidence["product"], "exact_candidate_sha256": evidence["exact_candidate_sha256"], "installed_bytes_verified": True, "final_or_play_ready": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
