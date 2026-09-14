#!/usr/bin/env python3
import json
from pathlib import Path

p = Path("ReleaseOps/THF_APPS_PHONE_FUNDAMENTALS_SOURCE_V1_MANIFEST.json")
d = json.loads(p.read_text(encoding="utf-8"))

assert d["schema"] == "thf-apps-phone-fundamentals-source-v1"
assert d["scope"] == ["core", "forge", "echo", "codex", "vault", "signal", "command"]
assert d["excluded"] == ["pulse", "games", "wave"]

expected_baseline = {
    "core": ("com.topherofit.thf.core", "6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a"),
    "forge": ("com.topherofit.thf.forge", "0f7a416a9e14af9dbb3cdcb26bfb891e0c680d4a33a73d60601eda215e697e51"),
    "echo": ("com.topherofit.thf.echo", "40a197b60563e560cab93ba0a64c859d9b650da222fdaec933993977d63902ab"),
    "codex": ("com.topherofit.thf.codex", "3d60cc550732468c89fe120f552def53ac798646d065e94efa153f8979e15b1e"),
    "vault": ("com.topherofit.thf.vault", "052e2c55c6066c15eee63528218b8eab9711bec9de71335c67c7e1692a5b5432"),
    "signal": ("com.topherofit.thf.signal", "f78890c3bf036d80a568ec39baac4a665d6092b9bbc8c4f080f2651785c1a275"),
    "command": ("com.topherofit.thf.command", "f7da9039041b8142d795e96934b95f00b83ac8fb5e3d6f5d9bfbff0aeb2eb408"),
}
for app, (pkg, sha) in expected_baseline.items():
    assert d["baseline"][app]["package_id"] == pkg
    assert d["baseline"][app]["source_sha256"] == sha
assert d["baseline"]["core"]["same_sha_skip"] is True

approved = {
    "forge": ("THF Market", False),
    "echo": ("THF Community", False),
    "codex": ("THF Learn", False),
    "vault": ("THF Wallet", False),
    "signal": ("THF Publisher", True),
    "command": ("THF Admin", True),
}
assert set(d["source_candidates"]) == set(approved)
for app, (name, private) in approved.items():
    x = d["source_candidates"][app]
    assert x["package_id"] == expected_baseline[app][0]
    assert x["user_facing_name"] == name
    assert x["target_sdk"] == 36
    assert x["resource_locales"] == 20
    assert x["adaptive_icon"] is True
    assert x["monochrome_icon_android_13_plus"] is True
    assert x["store_icon_512"] is True
    assert x["private_internal"] is private
    assert x["android_build_status"] == "NEEDS_EXACT_SOURCE_BUILD"
    assert x["eligible_apk_sha256"] is None
    assert x["sha256"] != d["baseline"][app]["source_sha256"]
    if private:
        assert x["launcher_visible_to_ordinary_users"] is False
        assert x["signature_entry_boundary"] is True
    else:
        assert x["launcher_visible_to_ordinary_users"] is True

assert d["shared_identity"]["private_rbac_contract"] == "PASS_CI_CANDIDATE"
assert d["shared_identity"]["deployed_backend"] == "NOT_PROVEN"
assert all(v is False for v in d["release_truth"].values())

integration = json.loads(Path("ReleaseOps/integration_factory/ANDROID_SHARED_INTEGRATION_V1.json").read_text(encoding="utf-8"))
assert integration["schema"] == "thf.android.shared.integration.v3"
assert integration["android"]["target_sdk"] == 36
assert integration["identity"]["account_deletion"]["authenticated_session_required"] is True
assert integration["identity"]["account_deletion"]["client_is_authoritative"] is False
assert integration["identity"]["account_deletion"]["backend_bound"] is False
assert integration["operator_access"]["ordinary_user_visible"] is False
assert integration["operator_access"]["server_role_claim_required"] is True
assert integration["operator_access"]["hidden_ui_is_not_security"] is True
assert integration["release_truth"]["account_deletion_backend_bound"] is False
assert integration["release_truth"]["physical_device_pass"] is False
assert integration["release_truth"]["final_or_play_ready"] is False

print("THF_APPS_PHONE_FUNDAMENTALS_SOURCE_V1=PASS")
print("SHARED_INTEGRATION_V3=PASS")
print("FINAL_OR_PLAY_READY=FALSE")
