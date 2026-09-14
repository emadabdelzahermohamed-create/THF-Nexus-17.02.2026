#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-f]{64}$")


def fail(errors, message):
    errors.append(message)


def parse_kv(path):
    out = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key in out:
            raise ValueError(f"duplicate evidence key: {key}")
        out[key] = value
    return out


def authority_by_name(state):
    result = {"core": state.get("core", {})}
    result.update({item.get("name"): item for item in state.get("apps", [])})
    return result


def main():
    ap = argparse.ArgumentParser(description="Fail closed when QA/debug mobile artifacts can contaminate THF release authority.")
    ap.add_argument("registry", type=Path)
    ap.add_argument("state", type=Path)
    ap.add_argument("physical_registry", type=Path)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ns = ap.parse_args()

    errors = []
    registry = json.loads(ns.registry.read_text())
    state = json.loads(ns.state.read_text())
    physical = json.loads(ns.physical_registry.read_text())
    root = ns.repo_root.resolve()

    if registry.get("schema") != 1:
        fail(errors, "auxiliary registry schema must be 1")
    tb = registry.get("truth_boundary", {})
    required_false = (
        "release_authority",
        "physical_release_evidence_eligible",
        "production_signing_eligible",
        "play_upload_eligible",
        "final_or_play_ready",
    )
    for key in required_false:
        if tb.get(key) is not False:
            fail(errors, f"auxiliary truth boundary must keep {key}=false")

    production = authority_by_name(state)
    physical_by_name = {item.get("name"): item for item in physical.get("candidates", [])}
    artifacts = registry.get("artifacts", [])
    if not artifacts:
        fail(errors, "auxiliary artifact registry must not be empty")

    seen_ids = set()
    seen_apk = set()
    seen_packages = set()
    validated = 0

    for item in artifacts:
        ident = item.get("id", "<missing>")
        app = item.get("app")
        if ident in seen_ids:
            fail(errors, f"duplicate auxiliary artifact id: {ident}")
        seen_ids.add(ident)

        for key in ("source_sha256", "apk_sha256", "production_candidate_apk_sha256"):
            if not HEX64.fullmatch(str(item.get(key, ""))):
                fail(errors, f"{ident}: invalid {key}")

        if item.get("apk_sha256") in seen_apk:
            fail(errors, f"{ident}: duplicate auxiliary APK SHA")
        seen_apk.add(item.get("apk_sha256"))
        if item.get("package") in seen_packages:
            fail(errors, f"{ident}: duplicate auxiliary package")
        seen_packages.add(item.get("package"))

        for key in ("release_authority", "physical_release_evidence_eligible", "backend_dependent_features_accepted", "production_signing", "play_upload", "final_or_play_ready"):
            if item.get(key) is not False:
                fail(errors, f"{ident}: {key} must be false")
        if item.get("debug_signed") is not True:
            fail(errors, f"{ident}: debug_signed must be true for this QA-only registry")
        if item.get("target_sdk") != 36:
            fail(errors, f"{ident}: targetSdk must be 36")
        if not str(item.get("package", "")).endswith(".debug"):
            fail(errors, f"{ident}: auxiliary package must use isolated .debug identity")

        authoritative = production.get(app)
        device_authority = physical_by_name.get(app)
        if not authoritative or not device_authority:
            fail(errors, f"{ident}: unknown production app authority: {app}")
            continue

        expected_prod_pkg = authoritative.get("package")
        expected_prod_sha = authoritative.get("apk_sha256")
        if item.get("production_candidate_package") != expected_prod_pkg:
            fail(errors, f"{ident}: production candidate package lineage drift")
        if item.get("production_candidate_apk_sha256") != expected_prod_sha:
            fail(errors, f"{ident}: production candidate APK lineage drift")
        if (device_authority.get("package"), device_authority.get("apk_sha256")) != (expected_prod_pkg, expected_prod_sha):
            fail(errors, f"{ident}: state/physical production authority drift")
        if item.get("package") == expected_prod_pkg:
            fail(errors, f"{ident}: QA package aliases production package")
        if item.get("apk_sha256") == expected_prod_sha:
            fail(errors, f"{ident}: QA APK aliases production candidate SHA")
        if any(c.get("apk_sha256") == item.get("apk_sha256") or c.get("package") == item.get("package") for c in physical.get("candidates", [])):
            fail(errors, f"{ident}: QA artifact appears in physical release authority registry")

        paths = {}
        for key in ("artifact_path", "evidence_path", "checkpoint_path"):
            rel = item.get(key, "")
            path = (root / rel).resolve()
            try:
                path.relative_to(root)
            except ValueError:
                fail(errors, f"{ident}: {key} escapes repository root")
                continue
            paths[key] = path
            if not path.is_file():
                fail(errors, f"{ident}: missing {key}: {rel}")

        evidence_path = paths.get("evidence_path")
        if evidence_path and evidence_path.is_file():
            try:
                ev = parse_kv(evidence_path)
            except ValueError as exc:
                fail(errors, f"{ident}: {exc}")
                ev = {}
            exact = {
                "purpose": str(item.get("purpose")),
                "source_sha256": item.get("source_sha256"),
                "package": item.get("package"),
                "versionCode": str(item.get("version_code")),
                "versionName": item.get("version_name"),
                "targetSdk": str(item.get("target_sdk")),
                "apk_sha256": item.get("apk_sha256"),
                "apk_size_bytes": str(item.get("apk_size_bytes")),
                "production_signing": "false",
                "play_upload": "false",
                "backend_dependent_features": "NOT_ACCEPTED_IN_THIS_CANDIDATE",
            }
            for key, expected in exact.items():
                if ev.get(key) != expected:
                    fail(errors, f"{ident}: evidence mismatch for {key}")

        checkpoint_path = paths.get("checkpoint_path")
        if checkpoint_path and checkpoint_path.is_file():
            text = checkpoint_path.read_text()
            required_markers = (
                "not the authoritative production release candidate",
                "This artifact is NOT FINAL and is not Play-ready.",
                item.get("package", ""),
                item.get("apk_sha256", ""),
            )
            for marker in required_markers:
                if marker not in text:
                    fail(errors, f"{ident}: checkpoint missing release-boundary marker: {marker}")

        validated += 1

    report = {
        "schema": 1,
        "validation": "FAIL" if errors else "PASS",
        "registered_auxiliary_artifacts": len(artifacts),
        "validated_auxiliary_artifacts": validated,
        "production_authority_contamination": bool(errors),
        "final_or_play_ready": False,
        "errors": errors,
        "truth": "Auxiliary/debug artifacts may support local QA but cannot replace authoritative release candidates or physical release evidence."
    }
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
