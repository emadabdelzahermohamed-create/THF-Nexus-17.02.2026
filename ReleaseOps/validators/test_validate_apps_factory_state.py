import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "ReleaseOps/validators/validate_apps_factory_state.py"
STATE = ROOT / "ReleaseOps/apps_factory/THF_APPS_FACTORY_STATE_20260913_2035_EET.json"


def run_state(tmp_path, mutate=None):
    d = json.loads(STATE.read_text())
    if mutate:
        mutate(d)
    p = tmp_path / "state.json"
    p.write_text(json.dumps(d))
    cp = subprocess.run([sys.executable, str(VALIDATOR), str(p)], text=True, capture_output=True)
    return cp, json.loads(cp.stdout)


def test_authoritative_state_passes(tmp_path):
    cp, report = run_state(tmp_path)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert report["validation"] == "PASS"
    assert report["apps_exact_package_gate_pass"] == 9
    assert report["apps_runtime_binding_pass"] == 9
    assert report["apps_physical_pending"] == 9
    assert report["pytest_missing_apps"] == ["rush", "spark"]


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
    assert any("runtime endpoint binding" in e for e in report["errors"])


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
