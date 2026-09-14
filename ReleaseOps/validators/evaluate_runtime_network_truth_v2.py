#!/usr/bin/env python3
"""Classify runtime network evidence without confusing third-party URL reachability with THF backend proof."""
from __future__ import annotations

import argparse
import json
import urllib.parse
from pathlib import Path


def evaluate(runtime_dir: Path, registry_path: Path) -> dict[str, object]:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    candidates = [x for x in registry.get("candidates", []) if x.get("name") != "core"]
    if not candidates:
        raise ValueError("no app candidates in registry")

    apps: list[dict[str, object]] = []
    for candidate in candidates:
        app = candidate.get("name")
        source_sha = candidate.get("source_sha256")
        path = runtime_dir / f"{app}.runtime.json"
        if not path.is_file():
            raise ValueError(f"{app}: missing runtime endpoint audit {path}")
        audit = json.loads(path.read_text(encoding="utf-8"))
        if audit.get("runtime_placeholder_urls"):
            raise ValueError(f"{app}: placeholder runtime URL remains")
        if audit.get("runtime_insecure_urls"):
            raise ValueError(f"{app}: insecure runtime URL remains")

        config_files = set(audit.get("build_config_endpoint_runtime_files") or [])
        pass_files = set(audit.get("pass_or_auth_runtime_files") or [])
        refs: list[dict[str, str]] = []
        backend_literals: list[dict[str, str]] = []
        for item in audit.get("runtime_urls") or []:
            url = item.get("url", "")
            rel = item.get("file", "")
            parsed = urllib.parse.urlsplit(url)
            scheme = parsed.scheme.lower()
            if scheme not in {"https", "wss"} or not parsed.hostname:
                continue
            ref = {"url": url, "file": rel}
            refs.append(ref)
            if rel in config_files:
                backend_literals.append(ref)

        network_indirection_present = bool(config_files or pass_files)
        reason = (
            "ORIGIN_LITERAL_PRESENT_BUT_HEALTH_AUTH_UNPROVEN"
            if backend_literals
            else "NO_SOURCE_BOUND_BACKEND_LITERAL_ENDPOINT"
        )
        apps.append({
            "app": app,
            "source_sha256": source_sha,
            "candidate_status": candidate.get("status"),
            "network_indirection_present": network_indirection_present,
            "runtime_https_wss_reference_count": len(refs),
            "source_bound_backend_literal_count": len(backend_literals),
            "source_bound_backend_literals": backend_literals,
            "backend_health_auth_proof": False,
            "network_release_ready": False,
            "reason": reason,
        })

    return {
        "schema": "thf.apps.runtime_network_truth.v2",
        "policy": "MOBILE_REAL_FUNCTION_RELEASE_POLICY",
        "app_count": len(apps),
        "apps": apps,
        "third_party_or_literal_origin_response_is_backend_proof": False,
        "backend_health_auth_proof": False,
        "network_release_ready": False,
        "physical_device_pass": False,
        "final_or_play_ready": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("runtime_dir", type=Path)
    parser.add_argument("registry", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = evaluate(args.runtime_dir, args.registry)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"NETWORK_TRUTH_APP_COUNT={report['app_count']}")
    print("THIRD_PARTY_ORIGIN_IS_BACKEND_PROOF=FALSE")
    print("BACKEND_HEALTH_AUTH_PROOF=FALSE")
    print("NETWORK_RELEASE_READY=FALSE")
    print("PHYSICAL_DEVICE_PASS=FALSE")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
