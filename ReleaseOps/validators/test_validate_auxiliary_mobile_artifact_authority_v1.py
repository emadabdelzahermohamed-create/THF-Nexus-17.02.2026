import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "ReleaseOps/validators/validate_auxiliary_mobile_artifact_authority_v1.py"
AUX = ROOT / "ReleaseOps/apps_factory/THF_AUXILIARY_MOBILE_ARTIFACT_REGISTRY_V1.json"
STATE = ROOT / "ReleaseOps/apps_factory/THF_APPS_FACTORY_STATE_20260914_1115_EET.json"
PHYSICAL = ROOT / "ReleaseOps/apps_factory/THF_APPS_PHYSICAL_DEVICE_EVIDENCE_REGISTRY_V1.json"


def run_guard(tmp_path, mutate_aux=None, mutate_state=None, mutate_physical=None):
    aux = json.loads(AUX.read_text())
    state = json.loads(STATE.read_text())
    physical = json.loads(PHYSICAL.read_text())
    if mutate_aux:
        mutate_aux(aux)
    if mutate_state:
        mutate_state(state)
    if mutate_physical:
        mutate_physical(physical)
    ap = tmp_path / "aux.json"
    sp = tmp_path / "state.json"
    pp = tmp_path / "physical.json"
    ap.write_text(json.dumps(aux))
    sp.write_text(json.dumps(state))
    pp.write_text(json.dumps(physical))
    cp = subprocess.run(
        [sys.executable, str(VALIDATOR), str(ap), str(sp), str(pp), "--repo-root", str(ROOT)],
        text=True,
        capture_output=True,
    )
    return cp, json.loads(cp.stdout)


def test_authoritative_auxiliary_registry_passes(tmp_path):
    cp, report = run_guard(tmp_path)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert report["validation"] == "PASS"
    assert report["registered_auxiliary_artifacts"] == 1
    assert report["validated_auxiliary_artifacts"] == 1
    assert report["final_or_play_ready"] is False


def test_rejects_release_authority_promotion(tmp_path):
    cp, report = run_guard(tmp_path, lambda d: d["artifacts"][0].__setitem__("release_authority", True))
    assert cp.returncode != 0
    assert any("release_authority must be false" in e for e in report["errors"])


def test_rejects_physical_evidence_eligibility_promotion(tmp_path):
    cp, report = run_guard(tmp_path, lambda d: d["artifacts"][0].__setitem__("physical_release_evidence_eligible", True))
    assert cp.returncode != 0
    assert any("physical_release_evidence_eligible must be false" in e for e in report["errors"])


def test_rejects_final_promotion(tmp_path):
    cp, report = run_guard(tmp_path, lambda d: d["artifacts"][0].__setitem__("final_or_play_ready", True))
    assert cp.returncode != 0
    assert any("final_or_play_ready must be false" in e for e in report["errors"])


def test_rejects_production_package_alias(tmp_path):
    def mutate(d):
        d["artifacts"][0]["package"] = "com.topherofit.thf.core"
    cp, report = run_guard(tmp_path, mutate)
    assert cp.returncode != 0
    assert any("QA package aliases production package" in e or "isolated .debug identity" in e for e in report["errors"])


def test_rejects_production_apk_sha_alias(tmp_path):
    def mutate(d):
        d["artifacts"][0]["apk_sha256"] = d["artifacts"][0]["production_candidate_apk_sha256"]
    cp, report = run_guard(tmp_path, mutate)
    assert cp.returncode != 0
    assert any("QA APK aliases production candidate SHA" in e for e in report["errors"])


def test_rejects_lineage_drift_from_factory_state(tmp_path):
    def mutate(d):
        d["artifacts"][0]["production_candidate_apk_sha256"] = "0" * 64
    cp, report = run_guard(tmp_path, mutate)
    assert cp.returncode != 0
    assert any("production candidate APK lineage drift" in e for e in report["errors"])


def test_rejects_state_physical_authority_drift(tmp_path):
    def mutate(r):
        next(c for c in r["candidates"] if c["name"] == "core")["apk_sha256"] = "1" * 64
    cp, report = run_guard(tmp_path, mutate_physical=mutate)
    assert cp.returncode != 0
    assert any("state/physical production authority drift" in e for e in report["errors"])


def test_rejects_qa_artifact_in_physical_release_registry(tmp_path):
    aux = json.loads(AUX.read_text())["artifacts"][0]
    def mutate(r):
        core = next(c for c in r["candidates"] if c["name"] == "core")
        core["package"] = aux["package"]
        core["apk_sha256"] = aux["apk_sha256"]
    cp, report = run_guard(tmp_path, mutate_physical=mutate)
    assert cp.returncode != 0
    assert any("QA artifact appears in physical release authority registry" in e for e in report["errors"])


def test_rejects_missing_auxiliary_artifact(tmp_path):
    def mutate(d):
        d["artifacts"][0]["artifact_path"] = "ReleaseOps/phone-apks/does-not-exist.apk"
    cp, report = run_guard(tmp_path, mutate)
    assert cp.returncode != 0
    assert any("missing artifact_path" in e for e in report["errors"])


def test_rejects_evidence_identity_mismatch(tmp_path):
    def mutate(d):
        d["artifacts"][0]["version_name"] = "tampered-debug"
    cp, report = run_guard(tmp_path, mutate)
    assert cp.returncode != 0
    assert any("evidence mismatch for versionName" in e for e in report["errors"])
