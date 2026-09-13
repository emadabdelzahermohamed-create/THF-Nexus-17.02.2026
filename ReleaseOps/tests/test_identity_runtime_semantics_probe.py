import importlib.util
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "validators" / "probe_identity_runtime_semantics.py"
spec = importlib.util.spec_from_file_location("probe", P)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def obs(status=404, ctype="text/html", digest="same", length=10):
    return probe.Obs("/x", "POST", status, ctype, digest, length)


def test_same_spa_fallback_is_not_route_evidence():
    control = obs(200, "text/html", "fallback")
    candidate = obs(200, "text/html", "fallback")
    assert probe.distinct(candidate, control) is False


def test_distinct_validation_response_is_route_evidence():
    control = obs(404, "text/html", "missing")
    candidate = obs(422, "application/json", "validation")
    assert probe.distinct(candidate, control) is True
    assert probe.semantic_status_ok(candidate) is True


def test_success_response_is_not_safe_negative_auth_semantics():
    assert probe.semantic_status_ok(obs(200, "application/json", "ok")) is False
    assert probe.semantic_status_ok(obs(302, "text/html", "redirect")) is False


def test_auth_and_validation_failures_are_safe_semantics():
    for status in (400, 401, 403, 405, 409, 415, 422, 429):
        assert probe.semantic_status_ok(obs(status, "application/json", str(status))) is True


def test_network_failure_is_never_distinct_evidence():
    control = obs(404, "text/html", "missing")
    failed = probe.Obs("/auth/login", "POST", 0, "", "", 0, "TimeoutError")
    assert probe.distinct(failed, control) is False
