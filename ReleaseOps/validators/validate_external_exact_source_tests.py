#!/usr/bin/env python3
import argparse, json, re, sys
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
EXPECTED = {
    "spark": ("com.topherofit.thf.spark", "dc312dc65e681e914c3421a20362cd0fba0c1e692a7becdb66d7d17a0b6299a0"),
    "rush": ("com.topherofit.thf.rush", "bd7e365ded07fd569020fff1c699d74322fd5c767b16ac6336f2bc99f8b5958b"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("registry", type=Path)
    ns = ap.parse_args()
    d = json.loads(ns.registry.read_text())
    errors = []
    if d.get("schema") != 1:
        errors.append("schema must be 1")
    tb = d.get("truth_boundary", {})
    if tb.get("final_or_play_ready") is not False:
        errors.append("external tests must not promote final readiness")
    if tb.get("source_archives_mutated") is not False:
        errors.append("authoritative source archives must remain immutable")
    if tb.get("physical_device_evidence") is not False:
        errors.append("external source tests cannot claim physical-device evidence")
    wf = d.get("workflow", {})
    if wf.get("path") != ".github/workflows/thf-spark-rush-real-regression-v2.yml":
        errors.append("unexpected workflow path")
    if not HEX40.fullmatch(str(wf.get("commit", ""))):
        errors.append("invalid workflow commit")
    if not isinstance(wf.get("run_id"), int) or wf["run_id"] <= 0:
        errors.append("invalid workflow run_id")
    apps = d.get("apps", {})
    if set(apps) != set(EXPECTED):
        errors.append("registry must contain exactly spark and rush")
    repo = ns.registry.parents[2]
    for name, (pkg, source_sha) in EXPECTED.items():
        a = apps.get(name, {})
        if a.get("package") != pkg:
            errors.append(f"{name}: package drift")
        if a.get("source_sha256") != source_sha:
            errors.append(f"{name}: source SHA drift")
        if a.get("source_embedded_tests") is not False:
            errors.append(f"{name}: source archive embedded-test truth changed without new authoritative source")
        if a.get("result") != "PASS":
            errors.append(f"{name}: regression result not PASS")
        if not isinstance(a.get("executed_test_count"), int) or a["executed_test_count"] < 6:
            errors.append(f"{name}: insufficient executed regression count")
        if not isinstance(a.get("artifact_id"), int) or a["artifact_id"] <= 0:
            errors.append(f"{name}: invalid artifact id")
        if not HEX64.fullmatch(str(a.get("artifact_digest", ""))):
            errors.append(f"{name}: invalid artifact digest")
        rel = a.get("external_regression_path", "")
        p = repo / rel
        if not p.is_file():
            errors.append(f"{name}: regression pack missing: {rel}")
        elif source_sha not in p.read_text():
            errors.append(f"{name}: regression pack is not visibly bound to source SHA")
    print(json.dumps({"validation": "FAIL" if errors else "PASS", "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
