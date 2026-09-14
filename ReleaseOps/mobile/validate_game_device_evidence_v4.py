#!/usr/bin/env python3
"""V4 physical-phone evidence validator: V3 truth checks + real evidence files.

V3 validates semantic fields. V4 additionally requires every manual observation to
reference an existing, non-empty file inside an evidence bundle and binds that file
with SHA-256. This prevents placeholder evidence_ref strings from satisfying release
acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("thf_device_v3", HERE / "validate_game_device_evidence_v3.py")
V3 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = V3
SPEC.loader.exec_module(V3)
SHA = re.compile(r"^[0-9a-f]{64}$")


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_evidence_path(root: Path, ref: str) -> Path | None:
    if not isinstance(ref, str) or not ref.strip():
        return None
    p = Path(ref)
    if p.is_absolute() or ".." in p.parts:
        return None
    root = root.resolve()
    target = (root / p).resolve()
    if target == root or root not in target.parents:
        return None
    return target


def validate_bundle(registry: dict, registry_sha: str, evidence: dict, evidence_root: Path) -> list[str]:
    errors = list(V3.validate(registry, registry_sha, evidence))
    product = evidence.get("product")
    required = ()
    if product in V3.PRODUCT_MANUAL:
        required = V3.COMMON_MANUAL + V3.PRODUCT_MANUAL[product]
    observations = evidence.get("manual_observations") if isinstance(evidence.get("manual_observations"), dict) else {}
    for key in required:
        row = observations.get(key)
        if not isinstance(row, dict):
            continue
        ref = row.get("evidence_ref")
        target = _safe_evidence_path(evidence_root, ref)
        if target is None:
            errors.append(f"manual_observations.{key}: unsafe evidence_ref")
            continue
        if not target.is_file():
            errors.append(f"manual_observations.{key}: evidence file missing")
            continue
        if target.stat().st_size <= 0:
            errors.append(f"manual_observations.{key}: evidence file empty")
            continue
        expected = str(row.get("evidence_sha256") or "").lower()
        if not SHA.fullmatch(expected):
            errors.append(f"manual_observations.{key}: evidence_sha256 required")
            continue
        actual = _sha(target)
        if actual != expected:
            errors.append(f"manual_observations.{key}: evidence SHA mismatch")
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
        print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V4=FAIL")
        print("FINAL_OR_PLAY_READY=FALSE")
        return 1
    print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V4=PASS")
    print(f"PRODUCT={evidence['product']}")
    print(f"EXACT_APK_SHA256={evidence['exact_candidate_sha256']}")
    print("EVIDENCE_FILES_SHA256_BOUND=TRUE")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
