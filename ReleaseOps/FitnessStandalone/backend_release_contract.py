#!/usr/bin/env python3
"""Inventory release-critical Fitness backend contracts without exposing source.

The output contains paths, route literals and aggregate marker counts only. It
does not copy credentials, environment values or source snippets into evidence.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


TEXT_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".json"}
ROUTE_PATTERNS = (
    re.compile(r"\b(?:app|router)\.(?:get|post|put|patch|delete)\s*\(\s*['\"]([^'\"]+)"),
    re.compile(r"\b(?:GET|POST|PUT|PATCH|DELETE)\s+(/api/[A-Za-z0-9_./:{}-]+)"),
)
CATEGORIES = {
    "auth_session": re.compile(r"\b(?:auth|login|logout|oauth|session|cookie|csrf)\b", re.I),
    "user_scope": re.compile(
        r"\b(?:userId|user_id|currentUser|current_user|principal|ownerId|owner_id)\b", re.I
    ),
    "sync_reports": re.compile(r"\b(?:sync|workout|progress|report|history)\b", re.I),
    "health_ingestion": re.compile(r"\b(?:health|steps|heart|sleep|exerciseSession)\b", re.I),
    "health_provenance_dedup": re.compile(r"\b(?:provenance|dedup(?:lication)?|sourceId)\b", re.I),
    "server_authority": re.compile(
        r"\b(?:server.?authoritative|anti.?cheat|trustedScore|ranked|leaderboard|competition)\b",
        re.I,
    ),
}
SET_SEQUENCE_MARKERS = ("exercise_out_of_order", "stale_set_sequence", "acceptedSet", "expectedSet")


def _text_files(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            # Only exclusions *inside* the inspected source root are relevant.
            # CI intentionally extracts the immutable source below ``build/``;
            # checking the absolute path therefore discarded every source file.
            relative_parts = path.relative_to(root).parts
            if not any(
                part in {"node_modules", ".git", "build", "dist"}
                for part in relative_parts
            ):
                files.append(path)
    return sorted(files)


def inventory(root: Path, source_sha256: str, recorded_at: str) -> dict[str, object]:
    files = _text_files(root)
    backend_files = [
        path
        for path in files
        if "backend" in {part.lower() for part in path.parts}
        or path.name.lower() in {"main.py", "server.py", "index.ts", "index.js"}
    ]
    counts = {name: 0 for name in CATEGORIES}
    marker_files: dict[str, set[str]] = {name: set() for name in CATEGORIES}
    sequence_files: dict[str, set[str]] = {marker: set() for marker in SET_SEQUENCE_MARKERS}
    routes: set[str] = set()

    for path in backend_files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        relative = str(path.relative_to(root))
        for pattern in ROUTE_PATTERNS:
            routes.update(match.group(1) for match in pattern.finditer(text))
        for name, pattern in CATEGORIES.items():
            found = pattern.findall(text)
            counts[name] += len(found)
            if found:
                marker_files[name].add(relative)
        for marker in SET_SEQUENCE_MARKERS:
            if marker in text:
                sequence_files[marker].add(relative)

    checks = {
        "backend_source_present": bool(backend_files),
        "routes_present": bool(routes),
        "auth_session_contract_present": counts["auth_session"] > 0,
        "authenticated_user_scope_present": counts["user_scope"] > 0,
        "sync_report_contract_present": counts["sync_reports"] > 0,
        "server_authority_contract_present": counts["server_authority"] > 0,
        "set_sequence_contract_complete": all(sequence_files[marker] for marker in SET_SEQUENCE_MARKERS),
        "health_ingestion_contract_present": counts["health_ingestion"] > 0,
        "health_provenance_dedup_present": counts["health_provenance_dedup"] > 0,
    }
    release_critical = (
        "backend_source_present",
        "routes_present",
        "auth_session_contract_present",
        "authenticated_user_scope_present",
        "sync_report_contract_present",
        "server_authority_contract_present",
        "set_sequence_contract_complete",
    )
    result = "PROGRESS" if all(checks[name] for name in release_critical) else "BLOCKED"
    blockers = [name for name, passed in checks.items() if not passed]
    return {
        "schema": "thf-fitness-backend-release-contract-v1",
        "lane": "backend",
        "scope": "release_gate_only",
        "result": result,
        "final": False,
        "source": {
            "sha256": source_sha256,
            "file_count": len(files),
            "backend_file_count": len(backend_files),
            "backend_files": [str(path.relative_to(root)) for path in backend_files],
        },
        "routes": sorted(routes),
        "marker_counts": counts,
        "marker_files": {name: sorted(paths) for name, paths in marker_files.items()},
        "set_sequence_marker_files": {
            marker: sorted(paths) for marker, paths in sequence_files.items()
        },
        "checks": checks,
        "open_checks": blockers,
        "recorded_at": recorded_at,
        "next_action": (
            "Use authenticated non-destructive production E2E to prove login, scoped workout write, "
            "second-client sync, logout/session revocation and account deletion. Keep Health ingestion, "
            "deduplication and provenance fail-closed unless exact source and runtime evidence pass."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--recorded-at", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expect", choices=("PROGRESS", "BLOCKED"), required=True)
    args = parser.parse_args()
    report = inventory(args.root, args.source_sha256, args.recorded_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["result"] == args.expect else 2


if __name__ == "__main__":
    raise SystemExit(main())
