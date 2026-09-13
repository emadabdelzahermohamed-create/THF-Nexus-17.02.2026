#!/usr/bin/env python3
import argparse, json, re, sys
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED = {
    "pulse": "com.topherofit.thf.pulse",
    "forge": "com.topherofit.thf.forge",
    "echo": "com.topherofit.thf.echo",
    "codex": "com.topherofit.thf.codex",
    "spark": "com.topherofit.thf.spark",
    "rush": "com.topherofit.thf.rush",
    "vault": "com.topherofit.thf.vault",
    "signal": "com.topherofit.thf.signal",
    "command": "com.topherofit.thf.command",
}


def fail(errors, msg):
    errors.append(msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("state", type=Path)
    ns = ap.parse_args()
    d = json.loads(ns.state.read_text())
    errors = []

    if d.get("schema") != 2:
        fail(errors, "factory state schema must be 2 (runtime-bound candidates)")

    tb = d.get("truth_boundary", {})
    if tb.get("final_or_play_ready") is not False:
        fail(errors, "portfolio must remain non-final before physical acceptance")
    if tb.get("physical_phone_acceptance_required") is not True:
        fail(errors, "physical phone acceptance must be required")
    for forbidden in ("production_signing_performed", "public_rollout_performed", "token_finance_touched", "native_game_streams_touched"):
        if tb.get(forbidden) is not False:
            fail(errors, f"unsafe truth boundary: {forbidden}")

    shared = d.get("shared_runtime", {})
    if shared.get("health") != "PASS":
        fail(errors, "shared staging health must be PASS for runtime-bound candidates")
    if shared.get("endpoint_binding") != "PASS":
        fail(errors, "shared runtime endpoint binding must be PASS")
    if shared.get("auth_flow") == "PASS" or shared.get("thf_pass_contract") == "PASS":
        fail(errors, "auth/THF Pass must not be promoted by package-binding evidence")
    if shared.get("physical_device") == "PASS":
        fail(errors, "shared runtime state cannot fabricate physical-device PASS")
    for forbidden in ("production_cutover",):
        if shared.get(forbidden) is not False:
            fail(errors, f"unsafe shared runtime state: {forbidden}")
    if shared.get("wave_untouched") is not True:
        fail(errors, "WAVE isolation must remain explicit")
    if not isinstance(shared.get("evidence_workflow_run"), int):
        fail(errors, "shared runtime evidence workflow run missing")
    if not re.fullmatch(r"[0-9a-f]{40}", shared.get("evidence_commit", "")):
        fail(errors, "shared runtime evidence commit invalid")
    if not HEX64.match(shared.get("artifact_digest", "")):
        fail(errors, "shared runtime artifact digest invalid")

    core = d.get("core", {})
    if core.get("package") != "com.topherofit.thf.core":
        fail(errors, "Core package drift")
    if core.get("target_sdk") != 36:
        fail(errors, "Core targetSdk drift")
    if not HEX64.match(core.get("apk_sha256", "")):
        fail(errors, "Core exact APK SHA missing/invalid")
    if core.get("physical_phone_acceptance") == "PASS":
        fail(errors, "Core physical PASS must not be asserted by this non-device state file")

    apps = d.get("apps", [])
    by_name = {a.get("name"): a for a in apps}
    if set(by_name) != set(EXPECTED):
        fail(errors, f"app set mismatch: got={sorted(by_name)} expected={sorted(EXPECTED)}")
    packages = []
    apk_hashes = []
    previous_hashes = []
    for name, pkg in EXPECTED.items():
        a = by_name.get(name, {})
        if a.get("package") != pkg:
            fail(errors, f"{name}: package drift")
        packages.append(a.get("package"))
        if a.get("target_sdk") != 36:
            fail(errors, f"{name}: targetSdk must be 36")
        for field in ("source_sha256", "apk_sha256", "previous_unbound_qa_apk_sha256"):
            if not HEX64.match(a.get(field, "")):
                fail(errors, f"{name}: invalid {field}")
        apk_hashes.append(a.get("apk_sha256"))
        previous_hashes.append(a.get("previous_unbound_qa_apk_sha256"))
        if a.get("apk_sha256") == a.get("previous_unbound_qa_apk_sha256"):
            fail(errors, f"{name}: runtime-bound candidate must not alias prior unbound QA SHA")
        if a.get("runtime_endpoint_binding") != "PASS":
            fail(errors, f"{name}: runtime endpoint binding not PASS")
        if a.get("runtime_health") != "PASS_SHARED_STAGING":
            fail(errors, f"{name}: runtime health truth missing")
        if a.get("auth_flow") == "PASS":
            fail(errors, f"{name}: auth flow cannot be promoted without live credential evidence")
        if a.get("source_policy") != "PASS":
            fail(errors, f"{name}: source policy not PASS")
        if a.get("exact_candidate_package_gate") != "PASS":
            fail(errors, f"{name}: exact-candidate package gate not PASS")
        if a.get("physical_phone_acceptance") != "PENDING":
            fail(errors, f"{name}: physical evidence must remain PENDING here")
        if a.get("pytest") not in {"PASS", "NO_TESTS"}:
            fail(errors, f"{name}: invalid pytest state")

    if len(packages) != len(set(packages)):
        fail(errors, "package collision detected")
    if len(apk_hashes) != len(set(apk_hashes)):
        fail(errors, "runtime-bound APK SHA collision detected")
    if len(previous_hashes) != len(set(previous_hashes)):
        fail(errors, "previous QA APK SHA collision detected")

    pass_identity = d.get("pass_identity", {})
    if pass_identity.get("final_or_play_ready") is not False:
        fail(errors, "THF Pass must not be final without authoritative candidate/service evidence")
    if pass_identity.get("status") == "PASS":
        fail(errors, "THF Pass cannot be PASS from discovery/package evidence")

    report = {
        "schema": 2,
        "state": str(ns.state),
        "validation": "FAIL" if errors else "PASS",
        "apps_exact_package_gate_pass": sum(a.get("exact_candidate_package_gate") == "PASS" for a in apps),
        "apps_runtime_binding_pass": sum(a.get("runtime_endpoint_binding") == "PASS" for a in apps),
        "apps_physical_pending": sum(a.get("physical_phone_acceptance") == "PENDING" for a in apps),
        "pytest_missing_apps": sorted(a.get("name") for a in apps if a.get("pytest") == "NO_TESTS"),
        "errors": errors,
        "truth": "This validator checks evidence consistency only; it does not create auth or physical-device evidence."
    }
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
