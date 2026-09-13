#!/usr/bin/env python3
import argparse, json, pathlib, re, sys

EXPECTED_SCHEMA = "thf-game-backend-authority-dynamic-v1"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def validate(doc: dict) -> list[str]:
    errors = []
    if doc.get("schema") != EXPECTED_SCHEMA:
        errors.append("schema mismatch")
    if not SHA_RE.fullmatch(str(doc.get("runtime_source_sha256", ""))):
        errors.append("invalid runtime_source_sha256")
    if doc.get("canonical_source_sha256_after") != doc.get("runtime_source_sha256"):
        errors.append("canonical source SHA changed or not rebound")
    for key in ("canonical_source_modified", "external_network_allowed", "production_credentials_used", "wave_files_read_or_changed", "final_or_play_ready"):
        if doc.get(key) is not False:
            errors.append(f"{key} must be false")
    if "tooling_error" in doc:
        errors.append("tooling_error present")
    probes = doc.get("probes")
    if not isinstance(probes, list) or len(probes) < 5:
        errors.append("fewer than 5 dynamic probes")
        probes = probes if isinstance(probes, list) else []
    seen = set()
    rejected = 0
    for idx, probe in enumerate(probes):
        if not isinstance(probe, dict):
            errors.append(f"probe[{idx}] malformed")
            continue
        path = probe.get("path")
        method = probe.get("method")
        status = probe.get("status")
        if not isinstance(path, str) or not path.startswith("/"):
            errors.append(f"probe[{idx}] invalid path")
        if method not in ("POST", "PUT", "PATCH", "DELETE"):
            errors.append(f"probe[{idx}] is not a mutation method")
        key = (method, path)
        if key in seen:
            errors.append(f"duplicate probe {method} {path}")
        seen.add(key)
        if status not in (401, 403):
            errors.append(f"probe[{idx}] unauthorized status must be 401/403, got {status!r}")
        if probe.get("unauthorized_rejected") is not True:
            errors.append(f"probe[{idx}] unauthorized_rejected must be true")
        else:
            rejected += 1
        if "probe_error" in probe:
            errors.append(f"probe[{idx}] probe_error present")
    if doc.get("probe_count") != len(probes):
        errors.append("probe_count mismatch")
    if doc.get("unauthorized_rejection_count") != rejected:
        errors.append("unauthorized_rejection_count mismatch")
    if doc.get("all_unauthorized_mutations_rejected") is not True:
        errors.append("all_unauthorized_mutations_rejected must be true")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence", type=pathlib.Path)
    args = ap.parse_args()
    doc = json.loads(args.evidence.read_text())
    errors = validate(doc)
    if errors:
        for e in errors:
            print("ERROR: " + e, file=sys.stderr)
        return 1
    print("THF_GAME_BACKEND_AUTHORITY_DYNAMIC_EVIDENCE=PASS")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
