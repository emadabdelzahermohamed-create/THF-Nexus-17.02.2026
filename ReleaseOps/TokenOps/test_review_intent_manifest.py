import copy
import pytest

from ReleaseOps.TokenOps.review_intent_manifest import build_review_intent


def base_matrix(status="FAIL_CLOSED"):
    return {
        "network": "solana-mainnet-beta",
        "mint": "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv",
        "token_program": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
        "matrix_sha256": "a" * 64,
        "execution_authorized": False,
        "operations": {
            "reward_epoch": {
                "status": status,
                "minimum_approvals": 2,
                "approval_class": "reward_epoch",
                "review_cap_raw": None,
                "exact_signer_action": "USER_CONTROLLED_MULTISIG_APPROVAL_REQUIRED:2:reward_epoch",
                "execution_authorized": False,
                "financial_effect": False,
            }
        },
    }


def base_chain(status="PASS"):
    return {
        "status": status,
        "evidence_root_sha256": "b" * 64,
        "root_material": {"source_commit_sha": "c" * 40},
    }


def test_fail_closed_when_upstream_not_ready():
    p = build_review_intent(base_matrix(), base_chain(), "reward_epoch")
    assert p["status"] == "FAIL_CLOSED"
    assert p["exact_signer_action"] == "NONE"
    assert "operation_not_review_ready" in p["blockers"]
    assert p["transaction_bytes_created"] is False
    assert p["instruction_bytes_created"] is False
    assert p["financial_effect"] is False


def test_review_ready_still_never_execution_ready():
    p = build_review_intent(base_matrix("AWAITING_USER_CONTROLLED_MULTISIG_APPROVAL"), base_chain(), "reward_epoch")
    assert p["status"] == "REVIEW_READY_NOT_EXECUTION_READY"
    assert p["minimum_approvals"] == 2
    assert p["execution_authorized"] is False
    assert p["signed"] is False
    assert p["submitted"] is False
    assert p["broadcast"] is False
    assert p["private_key_required"] is False
    assert p["wave_touched"] is False


def test_bad_evidence_root_fails_closed():
    chain = base_chain()
    chain["evidence_root_sha256"] = "not-a-sha"
    p = build_review_intent(base_matrix("AWAITING_USER_CONTROLLED_MULTISIG_APPROVAL"), chain, "reward_epoch")
    assert p["status"] == "FAIL_CLOSED"
    assert "evidence_root_invalid" in p["blockers"]


def test_execution_claim_is_rejected_into_fail_closed():
    m = base_matrix("AWAITING_USER_CONTROLLED_MULTISIG_APPROVAL")
    m["execution_authorized"] = True
    p = build_review_intent(m, base_chain(), "reward_epoch")
    assert p["status"] == "FAIL_CLOSED"
    assert "matrix_execution_safety_violation" in p["blockers"]


def test_unsupported_operation_rejected():
    with pytest.raises(ValueError):
        build_review_intent(base_matrix(), base_chain(), "mint_more")
