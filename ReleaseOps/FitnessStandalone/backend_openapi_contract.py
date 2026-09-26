#!/usr/bin/env python3
"""Fail-closed OpenAPI audit for the immutable Fitness backend source.

Only route/method names and aggregate contract checks are emitted. The exact
source and schema bodies stay outside the public evidence artifact.
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from pathlib import Path


HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


def _operations(spec: dict[str, object]) -> list[tuple[str, str, dict[str, object]]]:
    operations = []
    for path, path_item in spec.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() in HTTP_METHODS and isinstance(operation, dict):
                operations.append((str(path), method.lower(), operation))
    return sorted(operations)


def analyze_openapi(
    spec: dict[str, object], source_sha256: str, recorded_at: str
) -> dict[str, object]:
    operations = _operations(spec)
    paths = sorted({path for path, _, _ in operations})
    route_methods = [f"{method.upper()} {path}" for path, method, _ in operations]

    def has_route(methods: set[str], pattern: str) -> bool:
        matcher = re.compile(pattern, re.I)
        return any(method in methods and matcher.search(path) for path, method, _ in operations)

    security_schemes = (
        spec.get("components", {}).get("securitySchemes", {})
        if isinstance(spec.get("components"), dict)
        else {}
    )
    global_security = spec.get("security")
    mutation_operations = [
        (path, method, operation)
        for path, method, operation in operations
        if method in {"post", "put", "patch", "delete"}
        and not re.search(r"/(?:auth/)?login/?$", path, re.I)
    ]
    secured_mutations = [
        f"{method.upper()} {path}"
        for path, method, operation in mutation_operations
        if operation.get("security") or global_security
    ]

    schema_text = json.dumps(
        spec.get("components", {}).get("schemas", {}),
        sort_keys=True,
        separators=(",", ":"),
    ).lower()
    checks = {
        "openapi_operations_present": bool(operations),
        "auth_login_route_present": has_route({"post"}, r"/(?:auth/)?login/?$"),
        "auth_logout_route_present": has_route(
            {"post", "delete"}, r"/(?:auth/)?logout/?$"
        ),
        "session_or_current_user_route_present": has_route(
            {"get", "post", "delete"}, r"/(?:session|me|current[-_]?user)/?$"
        ),
        "account_deletion_route_present": has_route(
            {"delete"}, r"/(?:account|users?|profile|me)(?:/|$)"
        ),
        "explicit_sync_route_present": has_route(
            {"get", "post", "put", "patch"}, r"sync"
        ),
        "reports_or_progress_route_present": has_route(
            {"get", "post"}, r"(?:reports?|progress)"
        ),
        "health_ingestion_route_present": any(
            method in {"post", "put", "patch"}
            and "health" in path.lower()
            and path.rstrip("/").lower() != "/health"
            for path, method, _ in operations
        ),
        "workout_set_and_proof_routes_present": has_route(
            {"post", "put", "patch"}, r"/sets/?$"
        )
        and has_route({"post", "put", "patch"}, r"/proof/?$"),
        "security_schemes_declared": bool(security_schemes),
        "all_mutations_declare_security": bool(mutation_operations)
        and len(secured_mutations) == len(mutation_operations),
        "server_authority_schema_declared": any(
            marker in schema_text
            for marker in ("expectedset", "acceptedset", "setsequence", "trustedscore")
        ),
        "health_provenance_dedup_schema_declared": any(
            marker in schema_text for marker in ("provenance", "sourceid", "dedup")
        ),
    }
    issue_by_check = {
        "openapi_operations_present": "OPENAPI_OPERATIONS_MISSING",
        "auth_login_route_present": "AUTH_LOGIN_ROUTE_MISSING",
        "auth_logout_route_present": "AUTH_LOGOUT_ROUTE_MISSING",
        "session_or_current_user_route_present": "SESSION_ROUTE_MISSING",
        "account_deletion_route_present": "ACCOUNT_DELETION_ROUTE_MISSING",
        "explicit_sync_route_present": "DATA_SYNC_ROUTE_MISSING",
        "reports_or_progress_route_present": "REPORTS_ROUTE_MISSING",
        "health_ingestion_route_present": "HEALTH_INGESTION_ROUTE_MISSING",
        "workout_set_and_proof_routes_present": "WORKOUT_SET_PROOF_ROUTE_MISSING",
        "security_schemes_declared": "OPENAPI_SECURITY_SCHEME_MISSING",
        "all_mutations_declare_security": "MUTATION_SECURITY_DECLARATION_MISSING",
        "server_authority_schema_declared": "SERVER_AUTHORITY_SCHEMA_MISSING",
        "health_provenance_dedup_schema_declared": "HEALTH_PROVENANCE_DEDUP_SCHEMA_MISSING",
    }
    issues = sorted(issue_by_check[name] for name, passed in checks.items() if not passed)
    return {
        "schema": "thf-fitness-backend-openapi-contract-v1",
        "lane": "backend",
        "scope": "release_gate_only",
        "result": "PROGRESS" if not issues else "BLOCKED",
        "final": False,
        "source_sha256": source_sha256,
        "openapi_version": spec.get("openapi"),
        "route_count": len(paths),
        "operation_count": len(operations),
        "routes": route_methods,
        "security_scheme_names": sorted(str(name) for name in security_schemes),
        "mutation_count": len(mutation_operations),
        "secured_mutation_count": len(secured_mutations),
        "checks": checks,
        "issues": issues,
        "recorded_at": recorded_at,
        "next_action": (
            "Add missing authenticated auth/session/account/sync contracts and declared security; "
            "add server-authoritative set sequencing plus Health ingestion provenance/deduplication, "
            "then rerun exact-source tests and authenticated non-destructive production E2E."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--module", default="app.main")
    parser.add_argument("--attribute", default="app")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--recorded-at", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expect", choices=("PROGRESS", "BLOCKED"), required=True)
    args = parser.parse_args()

    try:
        sys.path.insert(0, str(args.source_root.resolve()))
        module = importlib.import_module(args.module)
        application = getattr(module, args.attribute)
        report = analyze_openapi(
            application.openapi(), args.source_sha256, args.recorded_at
        )
    except (AttributeError, ImportError, OSError, TypeError, ValueError) as exc:
        report = {
            "schema": "thf-fitness-backend-openapi-contract-v1",
            "lane": "backend",
            "scope": "release_gate_only",
            "result": "BLOCKED",
            "final": False,
            "source_sha256": args.source_sha256,
            "issues": [f"OPENAPI_AUDIT_ERROR:{type(exc).__name__}:{exc}"],
            "recorded_at": args.recorded_at,
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["result"] == args.expect else 2


if __name__ == "__main__":
    raise SystemExit(main())
