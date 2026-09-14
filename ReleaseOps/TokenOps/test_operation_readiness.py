import pytest

from ReleaseOps.TokenOps.financial_control_plane import MINT, NETWORK, TOKEN_PROGRAM
from ReleaseOps.TokenOps.operation_readiness import build_operation_matrix, summarize_matrix


def _treasury_policy():
    return {
        "network": NETWORK,
        "mint": MINT,
        "approval_classes": {
            "reward_epoch": {"minimum_approvals": 2, "execution": "external_multisig"},
            "vesting_settlement": {"minimum_approvals": 2, "execution": "external_multisig"},
            "burn": {"minimum_approvals": 3, "execution": "external_multisig"},
            "treasury_transfer": {"minimum_approvals": 3, "execution": "external_multisig"},
        },
    }


def _readiness(blockers):
    return {"network": NETWORK, "mint": MINT, "blockers": blockers, "status": "FAIL_CLOSED" if blockers else "PASS"}


def _empty_registry():
    return {"network": NETWORK, "mint": MINT, "accounts": []}


def _account(role, balance=1000, slot=100_000):
    # Public-key-shaped deterministic test values only. No signer material.
    return {
        "token_account": TOKEN_PROGRAM,
        "owner": "11111111111111111111111111111111",
        "mint": MINT,
        "token_program": TOKEN_PROGRAM,
        "decimals": 8,
        "state": "initialized",
        "role": role,
        "observed_balance_raw": balance,
        "observed_slot": slot,
        "ownership_evidence_sha256": "a" * 64,
        "balance_evidence_sha256": "b" * 64,
    }


def test_current_empty_registry_is_fail_closed_with_no_signer_action():
    blockers = [
        "distribution_delivery_model_not_approved",
        "distribution_reserve_not_approved",
        "epoch_budget_cap_not_approved",
        "lock_rewards_terms_not_approved",
        "lock_terms_not_approved",
        "per_user_cap_not_approved",
        "policy_mutation_governance_not_approved",
        "production_signer_policy_not_approved",
        "revenue_value_basis_not_approved",
        "treasury_accounts_and_evidence_missing",
        "vesting_terms_not_approved",
    ]
    matrix = build_operation_matrix(
        _readiness(blockers), _treasury_policy(), _empty_registry(),
        observed_slot=100_000, current_supply_raw=1_000_000_000_000_000_000,
    )
    assert matrix["status"] == "FAIL_CLOSED"
    assert matrix["exact_signer_action_now"] == "NONE"
    assert matrix["treasury_reconciliation"]["status"] == "FAIL_CLOSED"
    assert matrix["unmapped_global_blockers"] == []
    assert matrix["global_policy_only_blockers"] == ["policy_mutation_governance_not_approved"]
    assert all(v["execution_authorized"] is False for v in matrix["operations"].values())
    assert all(v["broadcast"] is False for v in matrix["operations"].values())
    assert matrix["wave_touched"] is False
    assert len(matrix["matrix_sha256"]) == 64


def test_verified_burn_reserve_only_bounds_review_cap_never_authorizes():
    registry = {"network": NETWORK, "mint": MINT, "accounts": [_account("burn_reserve", balance=250)]}
    matrix = build_operation_matrix(
        _readiness(["policy_mutation_governance_not_approved"]), _treasury_policy(), registry,
        observed_slot=100_100, current_supply_raw=1_000_000_000_000_000_000,
    )
    burn = matrix["operations"]["burn"]
    assert burn["status"] == "AWAITING_USER_CONTROLLED_MULTISIG_APPROVAL"
    assert burn["minimum_approvals"] == 3
    assert burn["review_cap_raw"] == "250"
    assert burn["exact_signer_action"] == "USER_CONTROLLED_MULTISIG_APPROVAL_REQUIRED:3:burn"
    assert burn["execution_authorized"] is False
    assert burn["signed"] is False
    assert burn["broadcast"] is False
    # Other operation roles are absent, so the aggregate matrix remains closed.
    assert matrix["status"] == "FAIL_CLOSED"
    assert matrix["exact_signer_action_now"] == "NONE"


def test_burn_below_floor_remains_fail_closed():
    registry = {"network": NETWORK, "mint": MINT, "accounts": [_account("burn_reserve", balance=250)]}
    matrix = build_operation_matrix(
        _readiness([]), _treasury_policy(), registry,
        observed_slot=100_100, current_supply_raw=799_999_999_999_999_999,
    )
    burn = matrix["operations"]["burn"]
    assert burn["status"] == "FAIL_CLOSED"
    assert "supply_below_approved_floor" in burn["evidence_blockers"]
    assert burn["review_cap_raw"] == "0"
    assert burn["exact_signer_action"] == "NONE"


def test_sensitive_material_is_rejected_before_matrix_compilation():
    registry = _empty_registry()
    registry["private_key"] = "never"
    with pytest.raises(ValueError, match="forbidden sensitive field"):
        build_operation_matrix(
            _readiness([]), _treasury_policy(), registry,
            observed_slot=100_000, current_supply_raw=1_000_000_000_000_000_000,
        )


def test_summary_is_non_executable_and_deterministic():
    matrix = build_operation_matrix(
        _readiness(["treasury_accounts_and_evidence_missing"]), _treasury_policy(), _empty_registry(),
        observed_slot=100_000, current_supply_raw=1_000_000_000_000_000_000,
    )
    a = summarize_matrix(matrix)
    b = summarize_matrix(matrix)
    assert a == b
    assert a["status"] == "FAIL_CLOSED"
    assert a["exact_signer_action_now"] == "NONE"
    assert a["execution_authorized"] is False
    assert a["broadcast"] is False
    assert a["financial_effect"] is False
    assert len(a["summary_sha256"]) == 64
