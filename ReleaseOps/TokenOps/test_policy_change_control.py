import pytest

from ReleaseOps.TokenOps.financial_control_plane import MINT, NETWORK
from ReleaseOps.TokenOps.policy_change_control import (
    PROPOSAL_SCHEMA,
    build_current_failclosed_proof,
    compile_policy_change_packet,
)


def _policy(approved=False):
    return {
        "network": NETWORK,
        "mint": MINT,
        "policy_mutation_governance": {
            "status": "approved" if approved else "not_approved",
            "minimum_approvals": 3 if approved else None,
            "authority_model": "external_multisig" if approved else None,
            "evidence_sha256": "a" * 64 if approved else None,
        },
    }


def _proposal(delta=None):
    return {
        "schema": PROPOSAL_SCHEMA,
        "network": NETWORK,
        "mint": MINT,
        "proposal_id": "test-proposal",
        "target_file": "ReleaseOps/TokenOps/policy.json",
        "action": "review_only_policy_delta",
        "before_sha256": "b" * 64,
        "rationale_evidence_sha256": "c" * 64,
        "delta": delta or {"per_user_cap_raw": "1000"},
    }


def test_current_governance_is_fail_closed_and_non_executable():
    packet = build_current_failclosed_proof(_policy(False))
    assert packet["status"] == "FAIL_CLOSED"
    assert packet["exact_next_action"] == "NONE"
    assert "policy_mutation_governance_not_approved" in packet["blockers"]
    assert packet["policy_mutation_applied"] is False
    assert packet["execution_authorized"] is False
    assert packet["signed"] is False
    assert packet["broadcast"] is False
    assert packet["financial_effect"] is False
    assert packet["private_key_required"] is False
    assert packet["wave_touched"] is False
    assert len(packet["packet_sha256"]) == 64


def test_approved_governance_only_reaches_external_multisig_review():
    packet = compile_policy_change_packet(_policy(True), _proposal())
    assert packet["status"] == "AWAITING_USER_CONTROLLED_POLICY_MULTISIG_APPROVAL"
    assert packet["exact_next_action"] == "USER_CONTROLLED_POLICY_MULTISIG_APPROVAL_REQUIRED:3"
    assert packet["policy_mutation_applied"] is False
    assert packet["execution_authorized"] is False
    assert packet["transaction_bytes_created"] is False
    assert packet["instruction_bytes_created"] is False
    assert "per_user_cap_raw" in packet["high_impact_terms"]


def test_target_outside_tokenops_policy_allowlist_is_rejected():
    p = _proposal()
    p["target_file"] = "WAVE/config.json"
    with pytest.raises(ValueError, match="outside TokenOps policy allowlist"):
        compile_policy_change_packet(_policy(True), p)


def test_sensitive_material_is_rejected():
    p = _proposal()
    p["private_key"] = "never"
    with pytest.raises(ValueError, match="forbidden sensitive field"):
        compile_policy_change_packet(_policy(True), p)


def test_rationale_evidence_hash_is_required():
    p = _proposal()
    p["rationale_evidence_sha256"] = None
    with pytest.raises(ValueError, match="rationale_evidence_sha256 required"):
        compile_policy_change_packet(_policy(True), p)


def test_packet_is_deterministic():
    a = compile_policy_change_packet(_policy(True), _proposal({"epoch_budget_cap_raw": "2000"}))
    b = compile_policy_change_packet(_policy(True), _proposal({"epoch_budget_cap_raw": "2000"}))
    assert a == b
    assert a["delta_sha256"] == b["delta_sha256"]
    assert a["packet_sha256"] == b["packet_sha256"]
