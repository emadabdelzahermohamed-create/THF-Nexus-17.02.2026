#!/usr/bin/env python3
"""Fail-closed lock between authoritative THF game sources and device candidates.

This validator deliberately does not infer PLAY_READY. It only proves that the
source bytes currently designated authoritative still match the source SHA
recorded for each exact device candidate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_APPS = {
    "terra",
    "rift",
    "spark",
    "rush",
    "learn_games",
    "fitness_games",
}


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate(registry: dict, observed: dict) -> list[str]:
    errors: list[str] = []

    if registry.get("schema") != "thf-game-device-candidates-v1":
        errors.append("registry_schema_invalid")
    if registry.get("final_or_play_ready") is not False:
        errors.append("registry_must_not_self_promote")
    if registry.get("physical_device_status") != "PENDING":
        errors.append("physical_device_status_must_remain_PENDING")
    if observed.get("schema") != "thf-game-authoritative-source-observation-v1":
        errors.append("observation_schema_invalid")
    if observed.get("read_only") is not True:
        errors.append("observation_must_be_read_only")
    if observed.get("wave_untouched") is not True:
        errors.append("wave_isolation_not_proven")
    if observed.get("canonical_archives_mutated") is not False:
        errors.append("canonical_mutation_detected")

    reg_rows = registry.get("candidates") or []
    obs_rows = observed.get("sources") or []
    reg = {r.get("app"): r for r in reg_rows if isinstance(r, dict)}
    obs = {r.get("app"): r for r in obs_rows if isinstance(r, dict)}

    if set(reg) != REQUIRED_APPS:
        errors.append("registry_app_set_mismatch")
    if set(obs) != REQUIRED_APPS:
        errors.append("observation_app_set_mismatch")

    for app in sorted(REQUIRED_APPS):
        r = reg.get(app)
        o = obs.get(app)
        if not r or not o:
            continue
        if o.get("exists") is not True:
            errors.append(f"{app}:authoritative_source_missing")
        if o.get("zip_integrity") is not True:
            errors.append(f"{app}:zip_integrity_not_proven")
        expected = str(r.get("source_sha256") or "").lower()
        actual = str(o.get("source_sha256") or "").lower()
        if len(expected) != 64 or len(actual) != 64:
            errors.append(f"{app}:invalid_sha256_shape")
        elif actual != expected:
            errors.append(f"{app}:SOURCE_DRIFT:{expected}:{actual}")

    # A source lock must never be interpreted as device or release readiness.
    if observed.get("final_or_play_ready") is not False:
        errors.append("observation_must_not_promote_readiness")
    if observed.get("physical_device_evidence") not in ("PENDING", "NOT_COLLECTED"):
        errors.append("physical_device_evidence_claim_invalid")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("registry")
    ap.add_argument("observed")
    ap.add_argument("--json-out")
    ns = ap.parse_args()
    registry = _load(ns.registry)
    observed = _load(ns.observed)
    errors = validate(registry, observed)
    result = {
        "schema": "thf-game-authoritative-source-lock-result-v1",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "final_or_play_ready": False,
        "physical_device_status": "PENDING",
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if ns.json_out:
        Path(ns.json_out).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
