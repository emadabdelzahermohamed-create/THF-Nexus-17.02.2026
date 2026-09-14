#!/usr/bin/env python3
"""Fail closed when backend-reachability evidence is not bound to current app source lineage."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CORE_NAME = "core"


def _read_matrix(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for lineno, row in enumerate(reader, 1):
            if not row or all(not cell.strip() for cell in row):
                continue
            if len(row) != 4:
                raise ValueError(f"matrix line {lineno}: expected 4 TSV fields, got {len(row)}")
            app, checkpoint, source_sha256, source_locator = (cell.strip() for cell in row)
            if not app or not checkpoint or not source_locator:
                raise ValueError(f"matrix line {lineno}: blank app/checkpoint/source locator")
            if not SHA256_RE.fullmatch(source_sha256):
                raise ValueError(f"matrix line {lineno}: invalid SHA-256 for {app}")
            rows.append({
                "app": app,
                "checkpoint": checkpoint,
                "source_sha256": source_sha256,
                "source_locator": source_locator,
            })
    return rows


def validate(matrix_path: Path, registry_path: Path) -> dict[str, object]:
    rows = _read_matrix(matrix_path)
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if registry.get("policy") != "MOBILE_REAL_FUNCTION_RELEASE_POLICY":
        raise ValueError("registry policy is not MOBILE_REAL_FUNCTION_RELEASE_POLICY")
    if registry.get("truth_boundary", {}).get("final_or_play_ready") is not False:
        raise ValueError("registry truth boundary must remain non-final")

    candidates = registry.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("registry candidates missing")
    current = {item.get("name"): item for item in candidates if item.get("name") != CORE_NAME}
    if len(current) != len(candidates) - 1:
        raise ValueError("candidate names are blank or duplicated")

    seen: set[str] = set()
    for row in rows:
        app = row["app"]
        if app in seen:
            raise ValueError(f"duplicate backend matrix app: {app}")
        seen.add(app)
    expected = set(current)
    if seen != expected:
        missing = sorted(expected - seen)
        extra = sorted(seen - expected)
        raise ValueError(f"backend matrix app set drift: missing={missing} extra={extra}")

    superseded = {
        item.get("source_sha256")
        for item in registry.get("superseded_candidates", [])
        if isinstance(item, dict) and item.get("source_sha256")
    }
    bound: list[dict[str, str]] = []
    for row in rows:
        app = row["app"]
        source_sha = row["source_sha256"]
        if source_sha in superseded:
            raise ValueError(f"{app}: backend evidence points at superseded source SHA {source_sha}")
        candidate = current[app]
        authoritative = candidate.get("source_sha256")
        if source_sha != authoritative:
            raise ValueError(
                f"{app}: backend matrix SHA {source_sha} != authoritative candidate SHA {authoritative}"
            )
        if candidate.get("status") != "PENDING_PHYSICAL_PHONE":
            raise ValueError(f"{app}: unexpected candidate status {candidate.get('status')!r}")
        bound.append({
            "app": app,
            "checkpoint": row["checkpoint"],
            "source_sha256": source_sha,
            "candidate_status": candidate["status"],
        })

    return {
        "schema": "thf.apps.backend_reachability.lineage.v1",
        "status": "PASS",
        "policy": "MOBILE_REAL_FUNCTION_RELEASE_POLICY",
        "bound_app_count": len(bound),
        "bound_apps": bound,
        "superseded_source_rejected": True,
        "physical_device_pass": False,
        "final_or_play_ready": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("matrix", type=Path)
    parser.add_argument("registry", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = validate(args.matrix, args.registry)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("BACKEND_REACHABILITY_LINEAGE=PASS")
    print(f"BOUND_APP_COUNT={report['bound_app_count']}")
    print("SUPERSEDED_SOURCE_REJECTED=TRUE")
    print("PHYSICAL_DEVICE_PASS=FALSE")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
