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


def is_hex64(value):
    """Return False for missing/non-string evidence instead of throwing.

    Release state may intentionally carry null while exact source/APK lineage is
    unresolved. That is a validation failure, not a validator/runtime failure.
    """
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def validate_registry_alignment(d, registry, errors):
    """Fail closed if release-state identity drifts from exact-device authority."""
    tb = registry.get("truth_boundary", {})
    if tb.get("final_or_play_ready") is not False:
        fail(errors, "physical registry cannot assert final_or_play_ready")
    if tb.get("all_pending") is not True:
        fail(errors, "physical registry must remain all_pending before device evidence")

    candidates = registry.get("candidates", [])
    reg_by_name = {c.get("name"): c for c in candidates}
    expected_names = {"core", *EXPECTED.keys()}
    if set(reg_by_name) != expected_names:
        fail(errors, f"physical registry candidate set mismatch: got={sorted(reg_by_name)} expected={sorted(expected_names)}")
        return 0

    state_by_name = {"core": d.get("core", {}), **{a.get("name"): a for a in d.get("apps", [])}}
    matched = 0
    for name in sorted(expected_names):
        s = state_by_name.get(name, {})
        r = reg_by_name.get(name, {})
        if r.get("status") != "PENDING_PHYSICAL_PHONE":
            fail(errors, f"{name}: physical registry unexpectedly promoted: {r.get('status')}")
        if s.get("package") != r.get("package"):
            fail(errors, f"{name}: factory/physical package authority drift")
        if s.get("apk_sha256") != r.get("apk_sha256"):
            fail(errors, f"{name}: factory/physical APK SHA authority drift")
        if name != "core" and s.get("source_sha256") != r.get("source_sha256"):
            fail(errors, f"{name}: factory/physical source SHA authority drift")
        if (s.get("package"), s.get("apk_sha256")) == (r.get("package"), r.get("apk_sha256")):
            matched += 1
    return matched


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("state", type=Path)
    ap.add_argument("--physical-registry", type=Path)
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

    # Runtime Network Evidence V2 proved that configured bindings and literal
    # third-party HTTPS responses are diagnostic only. State must not relabel
    # them as THF backend health/auth evidence.
    shared = d.get("shared_runtime", {})
    if shared.get("health") != "DIAGNOSTIC_REACHABILITY_ONLY":
        fail(errors, "shared runtime health must remain diagnostic-only until THF backend proof exists")
    if shared.get("endpoint_binding") != "PASS_CONFIG_BINDING_ONLY":
        fail(errors, "shared runtime endpoint binding must be configuration-only")
    if shared.get("backend_health_auth_proof") is not False:
        fail(errors, "shared runtime cannot claim backend health/auth proof")
    if shared.get("network_release_ready") is not False:
        fail(errors, "shared runtime cannot claim network release readiness")
    if shared.get("auth_flow") == "PASS" or shared.get("thf_pass_contract") == "PASS":
        fail(errors, "auth/THF Pass must not be promoted by package-binding evidence")
    if shared.get("physical_device") == "PASS":
        fail(errors, "shared runtime state cannot fabricate physical-device PASS")
    if shared.get("production_cutover") is not False:
        fail(errors, "unsafe shared runtime state: production_cutover")
    if shared.get("wave_untouched") is not True:
        fail(errors, "WAVE isolation must remain explicit")
    if not isinstance(shared.get("evidence_workflow_run"), int):
        fail(errors, "shared runtime evidence workflow run missing")
    if not isinstance(shared.get("evidence_commit"), str) or not re.fullmatch(r"[0-9a-f]{40}", shared.get("evidence_commit")):
        fail(errors, "shared runtime evidence commit invalid")
    if not is_hex64(shared.get("artifact_digest")):
        fail(errors, "shared runtime artifact digest invalid")

    core = d.get("core", {})
    if core.get("package") != "com.topherofit.thf.core":
        fail(errors, "Core package drift")
    if core.get("target_sdk") != 36:
        fail(errors, "Core targetSdk drift")
    if not is_hex64(core.get("apk_sha256")):
        fail(errors, "Core exact APK SHA missing/invalid")
    if core.get("runtime_backend_health") != "NOT_PROVEN_THF_BACKEND":
        fail(errors, "Core runtime backend health cannot exceed current network evidence")
    if core.get("physical_phone_acceptance") == "PASS":
        fail(errors, "Core physical PASS must not be asserted by this non-device state file")

    apps = d.get("apps", [])
    by_name = {a.get("name"): a for a in apps}
    if set(by_name) != set(EXPECTED):
        fail(errors, f"app set mismatch: got={sorted(by_name)} expected={sorted(EXPECTED)}")
    packages, apk_hashes, previous_hashes = [], [], []
    for name, pkg in EXPECTED.items():
        a = by_name.get(name, {})
        if a.get("package") != pkg:
            fail(errors, f"{name}: package drift")
        packages.append(a.get("package"))
        if a.get("target_sdk") != 36:
            fail(errors, f"{name}: targetSdk must be 36")
        for field in ("source_sha256", "apk_sha256", "previous_unbound_qa_apk_sha256"):
            if not is_hex64(a.get(field)):
                fail(errors, f"{name}: invalid {field}")
        apk_hashes.append(a.get("apk_sha256"))
        previous_hashes.append(a.get("previous_unbound_qa_apk_sha256"))
        if a.get("apk_sha256") == a.get("previous_unbound_qa_apk_sha256"):
            fail(errors, f"{name}: runtime-bound candidate must not alias prior unbound QA SHA")
        if a.get("runtime_endpoint_binding") != "PASS_CONFIG_BINDING_ONLY":
            fail(errors, f"{name}: runtime endpoint binding must remain configuration-only")
        if a.get("runtime_health") != "NOT_PROVEN_THF_BACKEND":
            fail(errors, f"{name}: runtime health cannot be promoted without THF backend health/auth proof")
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

    registry_matches = None
    if ns.physical_registry:
        registry = json.loads(ns.physical_registry.read_text())
        registry_matches = validate_registry_alignment(d, registry, errors)

    report = {
        "schema": 2,
        "state": str(ns.state),
        "physical_registry": str(ns.physical_registry) if ns.physical_registry else None,
        "validation": "FAIL" if errors else "PASS",
        "apps_exact_package_gate_pass": sum(a.get("exact_candidate_package_gate") == "PASS" for a in apps),
        "apps_runtime_config_binding_pass": sum(a.get("runtime_endpoint_binding") == "PASS_CONFIG_BINDING_ONLY" for a in apps),
        "apps_backend_health_auth_proven": sum(a.get("runtime_health") == "PASS_THF_BACKEND" for a in apps),
        "apps_physical_pending": sum(a.get("physical_phone_acceptance") == "PENDING" for a in apps),
        "physical_registry_authority_matches": registry_matches,
        "pytest_missing_apps": sorted(a.get("name") for a in apps if a.get("pytest") == "NO_TESTS"),
        "errors": errors,
        "truth": "Configured endpoint binding and third-party reachability are not THF backend health/auth proof; this validator does not create auth or physical-device evidence."
    }
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
