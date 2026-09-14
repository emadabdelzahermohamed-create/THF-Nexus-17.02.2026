import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "ReleaseOps/validators/validate_apps_factory_state.py"
STATE = ROOT / "ReleaseOps/apps_factory/THF_APPS_FACTORY_STATE_20260914_1115_EET.json"
REGISTRY = ROOT / "ReleaseOps/apps_factory/THF_APPS_PHYSICAL_DEVICE_EVIDENCE_REGISTRY_V1.json"


def run_state(tmp_path, mutate=None, registry_mutate=None, bind_registry=False):
    d = json.loads(STATE.read_text())
    if mutate:
        mutate(d)
    p = tmp_path / "state.json"
    p.write_text(json.dumps(d))
    cmd = [sys.executable, str(VALIDATOR), str(p)]
    if bind_registry:
        r = json.loads(REGISTRY.read_text())
        if registry_mutate:
            registry_mutate(r)
        rp = tmp_path / "registry.json"
        rp.write_text(json.dumps(r))
        cmd += ["--physical-registry", str(rp)]
    cp = subprocess.run(cmd, text=True, capture_output=True)
    return cp, json.loads(cp.stdout)


def test_authoritative_state_passes(tmp_path):
    cp, report = run_state(tmp_path)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert report["validation"] == "PASS"
    assert report["apps_exact_package_gate_pass"] == 9
    assert report["apps_runtime_config_binding_pass"] == 9
    assert report["apps_backend_health_auth_proven"] == 0
    assert report["apps_physical_pending"] == 9
    assert report["pytest_missing_apps"] == ["rush", "spark"]


def test_authoritative_state_matches_physical_registry(tmp_path):
    cp, report = run_state(tmp_path, bind_registry=True)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert report["validation"] == "PASS"
    assert report["physical_registry_authority_matches"] == 10


def test_rejects_registry_apk_authority_drift(tmp_path):
    def mutate(r):
        next(c for c in r["candidates"] if c["name"] == "spark")["apk_sha256"] = "0" * 64
    cp, report = run_state(tmp_path, registry_mutate=mutate, bind_registry=True)
    assert cp.returncode != 0
    assert any("spark: factory/physical APK SHA authority drift" in e for e in report["errors"])


def test_rejects_registry_source_authority_drift(tmp_path):
    def mutate(r):
        next(c for c in r["candidates"] if c["name"] == "rush")["source_sha256"] = "1" * 64
    cp, report = run_state(tmp_path, registry_mutate=mutate, bind_registry=True)
    assert cp.returncode != 0
    assert any("rush: factory/physical source SHA authority drift" in e for e in report["errors"])


def test_rejects_registry_false_promotion(tmp_path):
    def mutate(r):
        r["truth_boundary"]["all_pending"] = False
        r["candidates"][0]["status"] = "PASS"
    cp, report = run_state(tmp_path, registry_mutate=mutate, bind_registry=True)
    assert cp.returncode != 0
    assert any("all_pending" in e for e in report["errors"])
    assert any("unexpectedly promoted" in e for e in report["errors"])


def test_rejects_false_final(tmp_path):
    cp, report = run_state(tmp_path, lambda d: d["truth_boundary"].__setitem__("final_or_play_ready", True))
    assert cp.returncode != 0
    assert report["validation"] == "FAIL"


def test_rejects_package_drift(tmp_path):
    cp, report = run_state(tmp_path, lambda d: d["apps"][0].__setitem__("package", "com.example.wrong"))
    assert cp.returncode != 0
    assert any("package drift" in e for e in report["errors"])


def test_rejects_api36_regression(tmp_path):
    cp, report = run_state(tmp_path, lambda d: d["apps"][1].__setitem__("target_sdk", 35))
    assert cp.returncode != 0
    assert any("targetSdk" in e for e in report["errors"])


def test_rejects_fabricated_physical_pass(tmp_path):
    cp, report = run_state(tmp_path, lambda d: d["apps"][2].__setitem__("physical_phone_acceptance", "PASS"))
    assert cp.returncode != 0
    assert any("physical evidence" in e for e in report["errors"])


def test_rejects_unsafe_rollout_truth(tmp_path):
    cp, report = run_state(tmp_path, lambda d: d["truth_boundary"].__setitem__("public_rollout_performed", True))
    assert cp.returncode != 0
    assert any("public_rollout_performed" in e for e in report["errors"])


def test_rejects_missing_runtime_binding(tmp_path):
    cp, report = run_state(tmp_path, lambda d: d["apps"][0].__setitem__("runtime_endpoint_binding", "PENDING"))
    assert cp.returncode != 0
    assert any("configuration-only" in e for e in report["errors"])


def test_rejects_old_pass_shared_staging_health(tmp_path):
    cp, report = run_state(tmp_path, lambda d: d["apps"][0].__setitem__("runtime_health", "PASS_SHARED_STAGING"))
    assert cp.returncode != 0
    assert any("runtime health cannot be promoted" in e for e in report["errors"])


def test_rejects_shared_runtime_health_pass(tmp_path):
    cp, report = run_state(tmp_path, lambda d: d["shared_runtime"].__setitem__("health", "PASS"))
    assert cp.returncode != 0
    assert any("diagnostic-only" in e for e in report["errors"])


def test_rejects_network_release_ready_promotion(tmp_path):
    cp, report = run_state(tmp_path, lambda d: d["shared_runtime"].__setitem__("network_release_ready", True))
    assert cp.returncode != 0
    assert any("network release readiness" in e for e in report["errors"])


def test_rejects_backend_health_auth_promotion(tmp_path):
    cp, report = run_state(tmp_path, lambda d: d["shared_runtime"].__setitem__("backend_health_auth_proof", True))
    assert cp.returncode != 0
    assert any("backend health/auth proof" in e for e in report["errors"])


def test_rejects_core_runtime_health_promotion(tmp_path):
    cp, report = run_state(tmp_path, lambda d: d["core"].__setitem__("runtime_backend_health", "PASS_PREEXISTING_SAME_SHA"))
    assert cp.returncode != 0
    assert any("Core runtime backend health" in e for e in report["errors"])


def test_rejects_false_auth_promotion(tmp_path):
    cp, report = run_state(tmp_path, lambda d: d["apps"][0].__setitem__("auth_flow", "PASS"))
    assert cp.returncode != 0
    assert any("auth flow cannot be promoted" in e for e in report["errors"])


def test_rejects_unbound_candidate_alias(tmp_path):
    def mutate(d):
        d["apps"][0]["apk_sha256"] = d["apps"][0]["previous_unbound_qa_apk_sha256"]
    cp, report = run_state(tmp_path, mutate)
    assert cp.returncode != 0
    assert any("must not alias prior unbound QA SHA" in e for e in report["errors"])


def test_rejects_wave_isolation_regression(tmp_path):
    cp, report = run_state(tmp_path, lambda d: d["shared_runtime"].__setitem__("wave_untouched", False))
    assert cp.returncode != 0
    assert any("WAVE isolation" in e for e in report["errors"])
