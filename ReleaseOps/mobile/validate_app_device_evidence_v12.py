#!/usr/bin/env python3
"""THF app physical-device evidence validator V12.

V12 layers V11 and binds foreground-sensitive runtime evidence to one physical
Android boot session. A separate SHA-256-bound ADB capture of
/proc/sys/kernel/random/boot_id is required, its raw UUID is independently
hashed by the validator, and every V11 foreground-process provenance record
must carry that same boot-id hash.

This closes cross-reboot/stale-process evidence replay without changing any app
candidate bytes. This is release-control tooling only and cannot promote
FINAL/PLAY_READY.
"""
from __future__ import annotations

import hashlib
import re
import uuid
from pathlib import Path
from typing import Any

from validate_app_device_evidence_v11 import FOREGROUND_CHECKS, _kv_multimap, _one, validate as validate_v11
from validate_app_device_evidence_v9 import _safe_file

BOOT_METHOD = "ADB_CAT_PROC_SYS_KERNEL_RANDOM_BOOT_ID"
STDOUT_BEGIN = "THF_ADB_STDOUT_BEGIN"
STDOUT_END = "THF_ADB_STDOUT_END"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _bounded_stdout(text: str) -> str | None:
    if text.count(STDOUT_BEGIN) != 1 or text.count(STDOUT_END) != 1:
        return None
    start = text.index(STDOUT_BEGIN) + len(STDOUT_BEGIN)
    end = text.index(STDOUT_END)
    if end <= start:
        return None
    value = text[start:end].strip()
    return value if value else None


def _canonical_boot_uuid(raw: str) -> str | None:
    if "\n" in raw or "\r" in raw:
        return None
    try:
        parsed = uuid.UUID(raw)
    except (ValueError, AttributeError):
        return None
    canonical = str(parsed)
    return canonical if raw.lower() == canonical else None


def validate(registry: dict[str, Any], evidence: dict[str, Any], root: Path) -> list[str]:
    errors = list(validate_v11(registry, evidence, root))
    session = evidence.get("session") if isinstance(evidence.get("session"), dict) else {}
    device = evidence.get("device") if isinstance(evidence.get("device"), dict) else {}
    sid = session.get("session_id")
    fingerprint = device.get("fingerprint_sha256")

    boot = evidence.get("device_boot")
    if not isinstance(boot, dict):
        errors.append("V12 device_boot evidence required")
        return errors

    boot_ref = boot.get("evidence_ref")
    boot_path = _safe_file(root, boot_ref)
    if boot_path is None:
        errors.append("V12 boot provenance file required")
        return errors
    expected_file_sha = boot.get("evidence_sha256")
    if not isinstance(expected_file_sha, str) or expected_file_sha != _sha256_file(boot_path):
        errors.append("V12 boot provenance file SHA mismatch")
        return errors

    declared_boot_sha = boot.get("boot_id_sha256")
    if not isinstance(declared_boot_sha, str) or SHA256_RE.fullmatch(declared_boot_sha) is None:
        errors.append("V12 boot_id_sha256 must be lowercase SHA-256")
        return errors

    text = boot_path.read_text(encoding="utf-8", errors="replace")
    kv = _kv_multimap(text)
    expected = {
        "THF_SESSION_ID": sid,
        "THF_DEVICE_FINGERPRINT_SHA256": fingerprint,
        "THF_BOOT_CAPTURE_METHOD": BOOT_METHOD,
        "THF_BOOT_ID_SHA256": declared_boot_sha,
        "THF_ADB_EXIT_CODE": "0",
    }
    for marker, wanted in expected.items():
        if not isinstance(wanted, str) or _one(kv, marker) != wanted:
            errors.append(f"V12 boot provenance {marker} mismatch")

    raw_boot = _bounded_stdout(text)
    canonical_boot = _canonical_boot_uuid(raw_boot) if raw_boot is not None else None
    if canonical_boot is None:
        errors.append("V12 boot provenance requires one canonical raw Android boot UUID")
    else:
        calculated = _sha256_bytes(canonical_boot.encode("utf-8"))
        if calculated != declared_boot_sha:
            errors.append("V12 raw boot UUID does not match declared boot_id_sha256")

    provenance = evidence.get("process_provenance")
    if not isinstance(provenance, dict):
        errors.append("V12 process_provenance required")
        return errors

    process_refs = {
        item.get("evidence_ref")
        for item in provenance.values()
        if isinstance(item, dict) and isinstance(item.get("evidence_ref"), str)
    }
    if boot_ref in process_refs:
        errors.append("V12 boot provenance must be distinct from process provenance files")

    for check in FOREGROUND_CHECKS:
        prefix = f"V12 {check}: "
        item = provenance.get(check)
        path = _safe_file(root, item.get("evidence_ref") if isinstance(item, dict) else None)
        if path is None:
            errors.append(prefix + "process provenance file required")
            continue
        proc_kv = _kv_multimap(path.read_text(encoding="utf-8", errors="replace"))
        if _one(proc_kv, "THF_BOOT_ID_SHA256") != declared_boot_sha:
            errors.append(prefix + "process provenance boot-id mismatch")

    if evidence.get("final_or_play_ready") is not False:
        errors.append("V12 evidence cannot self-promote FINAL/PLAY_READY")
    return errors


__all__ = ["BOOT_METHOD", "FOREGROUND_CHECKS", "validate"]
