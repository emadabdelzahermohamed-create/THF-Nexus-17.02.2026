import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "ReleaseOps/validators/validate_external_exact_source_tests.py"
REGISTRY = ROOT / "ReleaseOps/apps_factory/THF_EXTERNAL_EXACT_SOURCE_TESTS_20260914.json"


def run(path):
    return subprocess.run([sys.executable, str(VALIDATOR), str(path)], cwd=ROOT, capture_output=True, text=True)


def test_authoritative_registry_passes():
    r = run(REGISTRY)
    assert r.returncode == 0, r.stdout + r.stderr


def test_final_promotion_is_rejected(tmp_path):
    d = json.loads(REGISTRY.read_text())
    d["truth_boundary"]["final_or_play_ready"] = True
    p = tmp_path / "bad.json"; p.write_text(json.dumps(d))
    r = run(p)
    assert r.returncode != 0
    assert "must not promote final readiness" in r.stdout


def test_source_sha_drift_is_rejected(tmp_path):
    d = json.loads(REGISTRY.read_text())
    d["apps"]["spark"]["source_sha256"] = "0" * 64
    p = tmp_path / "bad.json"; p.write_text(json.dumps(d))
    r = run(p)
    assert r.returncode != 0
    assert "source SHA drift" in r.stdout


def test_zero_test_false_pass_is_rejected(tmp_path):
    d = json.loads(REGISTRY.read_text())
    d["apps"]["rush"]["executed_test_count"] = 0
    p = tmp_path / "bad.json"; p.write_text(json.dumps(d))
    r = run(p)
    assert r.returncode != 0
    assert "insufficient executed regression count" in r.stdout


def test_embedded_test_history_cannot_be_fabricated(tmp_path):
    d = json.loads(REGISTRY.read_text())
    d["apps"]["spark"]["source_embedded_tests"] = True
    p = tmp_path / "bad.json"; p.write_text(json.dumps(d))
    r = run(p)
    assert r.returncode != 0
    assert "embedded-test truth changed" in r.stdout
