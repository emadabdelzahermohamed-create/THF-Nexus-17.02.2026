import copy
import datetime as dt

from ReleaseOps.TokenOps.evidence_chain import build_chain
from ReleaseOps.TokenOps.tokenops_guard import MINT, NETWORK, TOKEN_PROGRAM, DECIMALS, sha256


def fixtures(now):
    audit = {
        "observed_at_utc": now.isoformat(), "network": NETWORK, "mint": MINT,
        "program_id": TOKEN_PROGRAM, "decimals": DECIMALS, "mint_authority": None,
        "freeze_authority": None, "slot": 123, "supply_raw": "1000000000000000000",
        "execution": {"read_only": True, "financial_effect": False, "wave_touched": False},
    }
    audit["audit_sha256"] = sha256(audit)
    gate = {"status": "PASS", "failed": [], "gate_sha256": "a" * 64}
    policy = {"x": 1}
    treasury = {"y": 2}
    readiness = {
        "audit_sha256": audit["audit_sha256"], "policy_sha256": sha256(policy),
        "treasury_policy_sha256": sha256(treasury), "status": "FAIL_CLOSED",
    }
    provenance = {
        "source_commit_sha": "c" * 40, "tokenops_source_root_sha256": "d" * 64,
        "wave_in_inventory": False, "wave_touched": False, "financial_effect": False, "broadcast": False,
    }
    return audit, gate, readiness, provenance, policy, treasury


def test_chain_passes_fresh_consistent_evidence():
    now = dt.datetime(2026, 9, 14, 9, 40, tzinfo=dt.timezone.utc)
    args = fixtures(now)
    p = build_chain(*args, now=now, source_commit_sha="c" * 40, component_file_hashes={"a.json": "e" * 64})
    assert p["status"] == "PASS"
    assert p["execution_authorized"] is False
    assert p["financial_effect"] is False
    assert p["wave_touched"] is False


def test_chain_rejects_stale_audit():
    now = dt.datetime(2026, 9, 14, 10, 0, tzinfo=dt.timezone.utc)
    args = fixtures(now - dt.timedelta(minutes=16))
    p = build_chain(*args, now=now, source_commit_sha="c" * 40)
    assert p["status"] == "FAIL_CLOSED"
    assert "audit_fresh" in p["failed"]


def test_chain_rejects_tampered_audit_after_hash():
    now = dt.datetime(2026, 9, 14, 10, 0, tzinfo=dt.timezone.utc)
    args = list(fixtures(now))
    args[0] = copy.deepcopy(args[0])
    args[0]["supply_raw"] = "900000000000000000"
    p = build_chain(*args, now=now, source_commit_sha="c" * 40)
    assert p["status"] == "FAIL_CLOSED"
    assert "audit_sha_self_consistent" in p["failed"]


def test_chain_rejects_wrong_commit_binding():
    now = dt.datetime(2026, 9, 14, 10, 0, tzinfo=dt.timezone.utc)
    args = fixtures(now)
    p = build_chain(*args, now=now, source_commit_sha="f" * 40)
    assert p["status"] == "FAIL_CLOSED"
    assert "provenance_binds_commit" in p["failed"]


def test_chain_rejects_policy_mismatch():
    now = dt.datetime(2026, 9, 14, 10, 0, tzinfo=dt.timezone.utc)
    args = list(fixtures(now))
    args[4] = {"x": 2}
    p = build_chain(*args, now=now, source_commit_sha="c" * 40)
    assert p["status"] == "FAIL_CLOSED"
    assert "readiness_binds_policy" in p["failed"]
