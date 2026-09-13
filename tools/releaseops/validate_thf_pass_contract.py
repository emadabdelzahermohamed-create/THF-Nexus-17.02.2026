#!/usr/bin/env python3
import hashlib
import json
import pathlib
import sys

REQUIRED_TRUE = {
    "required_session_semantics": [
        "refresh_rotates_token",
        "refresh_reuse_rejected",
        "expired_refresh_rejected",
        "logout_revokes_current_session",
        "revoke_all_revokes_user_sessions",
    ],
    "required_federation_semantics": [
        "handoff_is_one_time",
        "handoff_has_short_expiry",
        "handoff_binds_audience_app",
        "handoff_binds_subject",
        "handoff_replay_rejected",
        "handoff_query_token_forbidden",
        "cross_app_session_exchange_requires_https",
    ],
}

SHA_KEYS = (
    ("baseline", "app_py_sha256"),
    ("baseline", "identity_service_py_sha256"),
    ("candidate", "app_py_sha256"),
    ("candidate", "identity_service_py_sha256"),
)


def is_sha256(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def validate(data):
    errors = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("contract") != "thf-pass-federation-handoff":
        errors.append("unexpected contract name")
    if data.get("final_or_play_ready") is not False:
        errors.append("candidate contract must remain FINAL_OR_PLAY_READY=false")
    if data.get("status") != "candidate-only":
        errors.append("status must remain candidate-only until runtime and device gates pass")

    for section, key in SHA_KEYS:
        value = data.get(section, {}).get(key)
        if not is_sha256(value):
            errors.append(f"{section}.{key} is not a lowercase SHA-256")
    if data.get("baseline") == data.get("candidate"):
        errors.append("candidate hashes must differ from deployed baseline hashes")

    for section, keys in REQUIRED_TRUE.items():
        values = data.get(section, {})
        for key in keys:
            if values.get(key) is not True:
                errors.append(f"{section}.{key} must be true")

    runtime = data.get("required_runtime_evidence", {})
    expected_runtime = {
        "reachable_https_health",
        "nonprod_login",
        "refresh",
        "logout",
        "revoke",
        "federation_handoff",
        "rollback_rehearsal",
    }
    if set(runtime) != expected_runtime:
        errors.append("runtime evidence keys drifted")
    # Evidence starts false. Promotion tooling must update each item only from bound evidence.
    for key, value in runtime.items():
        if not isinstance(value, bool):
            errors.append(f"required_runtime_evidence.{key} must be boolean")

    gates = data.get("owner_or_device_gates", {})
    for key in ("production_signing", "public_rollout", "physical_phone_acceptance"):
        if gates.get(key) is not False:
            errors.append(f"owner_or_device_gates.{key} must remain false in this candidate contract")
    return errors


def main(argv):
    path = pathlib.Path(argv[1] if len(argv) > 1 else "ReleaseOps/apps_factory/contracts/thf_pass_federation_handoff_v1.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate(data)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"CONTRACT_SHA256={digest}")
    if errors:
        for e in errors:
            print(f"ERROR={e}")
        return 1
    print("THF_PASS_FEDERATION_CONTRACT=PASS")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
