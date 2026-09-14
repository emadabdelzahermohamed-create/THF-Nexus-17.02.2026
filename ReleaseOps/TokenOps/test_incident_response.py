import copy

import pytest

from ReleaseOps.TokenOps.incident_response import assess_incident
from ReleaseOps.TokenOps.tokenops_guard import MINT, NETWORK


def fixtures():
    audit = {
        "network": NETWORK, "mint": MINT,
        "execution": {"read_only": True, "financial_effect": False, "wave_touched": False},
    }
    gate = {"status": "PASS", "failed": []}
    chain = {"status": "PASS", "failed": []}
    provenance = {
        "tokenops_source_root_sha256": "a" * 64,
        "wave_in_inventory": False, "wave_touched": False,
    }
    readiness = {"status": "FAIL_CLOSED", "blockers": ["treasury_accounts_not_verified"]}
    return audit, gate, chain, provenance, readiness


def test_known_readiness_blockers_are_not_incident():
    p = assess_incident(*fixtures())
    assert p["mode"] == "NORMAL_READ_ONLY"
    assert p["execution_authorized"] is False
    assert p["rollback"]["onchain_rollback_allowed"] is False


def test_optional_holder_unavailable_is_degraded_not_critical():
    p = assess_incident(*fixtures(), holder_concentration={"status": "UNAVAILABLE_FAIL_CLOSED"})
    assert p["mode"] == "READ_ONLY_DEGRADED"
    assert p["pause_review_intent_generation"] is False
    assert p["reaudit_required"] is False


def test_onchain_invariant_failure_forces_critical_quarantine():
    args = list(fixtures())
    args[1] = {"status": "FAIL_CLOSED", "failed": ["mint_authority_disabled"]}
    p = assess_incident(*args)
    assert p["mode"] == "FAIL_CLOSED_CRITICAL"
    assert p["pause_review_intent_generation"] is True
    assert p["reaudit_required"] is True
    assert p["execution_authorized"] is False


def test_stale_evidence_chain_forces_critical_quarantine():
    args = list(fixtures())
    args[2] = {"status": "FAIL_CLOSED", "failed": ["audit_fresh"]}
    p = assess_incident(*args)
    assert p["mode"] == "FAIL_CLOSED_CRITICAL"
    assert any(x.startswith("evidence_chain:") for x in p["critical_reasons"])


def test_treasury_mismatch_forces_critical_quarantine():
    p = assess_incident(*fixtures(), treasury_reconciliation={
        "status": "FAIL_CLOSED", "mismatches": ["balance_hash_mismatch"],
    })
    assert p["mode"] == "FAIL_CLOSED_CRITICAL"
    assert "treasury_reconciliation_mismatch" in p["critical_reasons"]


def test_empty_treasury_readiness_blocker_is_not_misclassified_as_incident():
    p = assess_incident(*fixtures(), treasury_reconciliation={
        "status": "FAIL_CLOSED", "mismatches": [],
    })
    assert p["mode"] == "NORMAL_READ_ONLY"


def test_wave_scope_violation_forces_critical_quarantine():
    args = list(fixtures())
    args[3] = copy.deepcopy(args[3])
    args[3]["wave_in_inventory"] = True
    p = assess_incident(*args)
    assert p["mode"] == "FAIL_CLOSED_CRITICAL"
    assert "source_provenance_wave_scope_violation" in p["critical_reasons"]


def test_sensitive_material_is_rejected():
    args = list(fixtures())
    args[0] = copy.deepcopy(args[0])
    args[0]["private_key"] = "never"
    with pytest.raises(ValueError):
        assess_incident(*args)
