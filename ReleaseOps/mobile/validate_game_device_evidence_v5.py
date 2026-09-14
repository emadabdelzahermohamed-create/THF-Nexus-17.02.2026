#!/usr/bin/env python3
"""V5 physical-phone evidence validator: V4 file integrity + one-session binding.

V5 prevents mixing observations captured in different phone sessions. Every manual and
authority observation must bind to one session_id and have an observed_at_utc timestamp
inside the declared session interval. This remains an evidence validator only and can
never promote FINAL/PLAY_READY by itself.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("thf_device_v4", HERE / "validate_game_device_evidence_v4.py")
V4 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = V4
SPEC.loader.exec_module(V4)
V3 = V4.V3

SESSION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{15,127}$")


def _utc(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def validate_bundle(registry: dict, registry_sha: str, evidence: dict, evidence_root: Path) -> list[str]:
    errors = list(V4.validate_bundle(registry, registry_sha, evidence, evidence_root))
    session = evidence.get("session")
    if not isinstance(session, dict):
        errors.append("session: missing record")
        return errors

    sid = session.get("session_id")
    if not isinstance(sid, str) or SESSION_ID.fullmatch(sid) is None:
        errors.append("session.session_id: stable nontrivial id required")
        sid = None
    started = _utc(session.get("started_at_utc"))
    ended = _utc(session.get("ended_at_utc"))
    if started is None:
        errors.append("session.started_at_utc: strict UTC timestamp required")
    if ended is None:
        errors.append("session.ended_at_utc: strict UTC timestamp required")
    if started is not None and ended is not None and ended <= started:
        errors.append("session interval must end after it starts")

    product = evidence.get("product")
    manual_keys = ()
    if product in V3.PRODUCT_MANUAL:
        manual_keys = V3.COMMON_MANUAL + V3.PRODUCT_MANUAL[product]
    groups = (
        ("manual_observations", manual_keys),
        ("authority_observations", V4.AUTHORITY_OBSERVATIONS),
    )
    for namespace, keys in groups:
        rows = evidence.get(namespace)
        if not isinstance(rows, dict):
            continue
        for key in keys:
            row = rows.get(key)
            if not isinstance(row, dict):
                continue
            if sid is not None and row.get("session_id") != sid:
                errors.append(f"{namespace}.{key}: session_id mismatch")
            observed = _utc(row.get("observed_at_utc"))
            if observed is None:
                errors.append(f"{namespace}.{key}: strict UTC observed_at_utc required")
            elif started is not None and ended is not None and not (started <= observed <= ended):
                errors.append(f"{namespace}.{key}: observation outside declared session interval")

    objective = evidence.get("objective")
    if isinstance(objective, dict):
        if sid is not None and objective.get("session_id") != sid:
            errors.append("objective.session_id mismatch")
        captured = _utc(objective.get("captured_at_utc"))
        if captured is None:
            errors.append("objective.captured_at_utc: strict UTC timestamp required")
        elif started is not None and ended is not None and not (started <= captured <= ended):
            errors.append("objective capture outside declared session interval")

    performance = evidence.get("performance_observation")
    if isinstance(performance, dict):
        if sid is not None and performance.get("session_id") != sid:
            errors.append("performance_observation.session_id mismatch")
        captured = _utc(performance.get("captured_at_utc"))
        if captured is None:
            errors.append("performance_observation.captured_at_utc: strict UTC timestamp required")
        elif started is not None and ended is not None and not (started <= captured <= ended):
            errors.append("performance observation outside declared session interval")
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
        print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V5=FAIL")
        print("FINAL_OR_PLAY_READY=FALSE")
        return 1
    print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V5=PASS")
    print(f"PRODUCT={evidence['product']}")
    print(f"EXACT_APK_SHA256={evidence['exact_candidate_sha256']}")
    print("SINGLE_DEVICE_SESSION_BOUND=TRUE")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
