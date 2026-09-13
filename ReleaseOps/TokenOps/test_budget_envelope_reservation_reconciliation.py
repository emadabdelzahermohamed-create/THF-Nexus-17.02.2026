#!/usr/bin/env python3
from __future__ import annotations

import copy

from budget_envelope_reservation_reconciliation import (
    CANONICAL_MINT,
    CANONICAL_NETWORK,
    canonical_sha256,
    compile_reservation_reconciliation,
)


def envelope(eligible=True):
    body = {
        "schema": "thf-tokenops-reward-vesting-budget-envelope/v1",
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "intent": "reward_epoch",
        "request_id": "epoch:test",
        "bound_admission_sha256": "1" * 64,
        "policy_completion_evidence_sha256": "2" * 64,
        "economics": {
            "active_user_revenue_share_bps": 3500,
            "approved_supply_floor_target_ui": "8000000000",
            "burn_source_policy": "treasury_controlled_balances_only",
        },
        "budget_controls": {
            "per_user_cap_raw": "100",
            "epoch_budget_cap_raw": "150",
            "total_requested_raw": "90",
            "caps_authoritatively_configured": True,
        },
        "approval_requirement": {
            "minimum_approvals": 2,
            "execution": "external_multisig",
            "approval_satisfied_here": False,
        },
        "revenue": None,
        "entries": [
            {"subject_id": "u1", "wallet": "w1", "amount_raw": "50"},
            {"subject_id": "u2", "wallet": "w2", "amount_raw": "40"},
        ],
        "review_eligible": eligible,
        "blockers": [] if eligible else ["production_caps_not_approved"],
        "execution": {
            "transaction_created": False,
            "transaction_signed": False,
            "transaction_submitted": False,
            "broadcast_allowed": False,
            "financial_effect": False,
            "settlement_executed": False,
            "burn_executed": False,
            "treasury_migrated": False,
            "dao_decision_executed": False,
            "private_key_used": False,
            "wave_mawja_untouched": True,
        },
    }
    body["envelope_sha256"] = canonical_sha256(body)
    return body


def request(env, reservations=None):
    return {
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "request_id": "reserve:test",
        "budget_envelope_sha256": env["envelope_sha256"],
        "reservations": reservations or [
            {"reservation_id": "r1", "subject_id": "u1", "wallet": "w1", "amount_raw": "30"},
            {"reservation_id": "r2", "subject_id": "u2", "wallet": "w2", "amount_raw": "20"},
        ],
    }


def expect_error(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def main():
    env = envelope(True)
    out = compile_reservation_reconciliation(env, request(env))
    assert out["reservation_review_eligible"] is True
    assert out["accounting"]["budget_total_raw"] == "90"
    assert out["accounting"]["reserved_total_raw"] == "50"
    assert out["accounting"]["remaining_budget_raw"] == "40"
    assert out["accounting"]["overcommitted"] is False
    assert out["execution"]["transaction_created"] is False
    assert out["execution"]["transaction_signed"] is False
    assert out["execution"]["transaction_submitted"] is False
    assert out["execution"]["financial_effect"] is False
    assert out["execution"]["wave_mawja_untouched"] is True

    second_req = request(env, [
        {"reservation_id": "r3", "subject_id": "u1", "wallet": "w1", "amount_raw": "20"},
    ])
    second = compile_reservation_reconciliation(env, second_req, [out])
    assert second["reservation_review_eligible"] is True
    assert second["accounting"]["reserved_total_raw"] == "70"
    assert second["allocation_status"][0]["remaining_raw"] == "0"

    over_req = request(env, [
        {"reservation_id": "r3", "subject_id": "u1", "wallet": "w1", "amount_raw": "21"},
    ])
    over = compile_reservation_reconciliation(env, over_req, [out])
    assert over["reservation_review_eligible"] is False
    assert "budget_allocation_exceeded:u1" in over["blockers"]

    detached = request(env)
    detached["budget_envelope_sha256"] = "f" * 64
    expect_error(lambda: compile_reservation_reconciliation(env, detached))

    unknown = request(env, [
        {"reservation_id": "r9", "subject_id": "other", "wallet": "w9", "amount_raw": "1"},
    ])
    expect_error(lambda: compile_reservation_reconciliation(env, unknown))

    tampered = copy.deepcopy(env)
    tampered["entries"][0]["amount_raw"] = "51"
    expect_error(lambda: compile_reservation_reconciliation(tampered, request(env)))

    sensitive = request(env)
    sensitive["private_key"] = "forbidden"
    expect_error(lambda: compile_reservation_reconciliation(env, sensitive))

    blocked_env = envelope(False)
    blocked = compile_reservation_reconciliation(blocked_env, request(blocked_env))
    assert blocked["reservation_review_eligible"] is False
    assert "budget_envelope_not_review_eligible" in blocked["blockers"]
    assert "production_caps_not_approved" in blocked["blockers"]

    prior_tampered = copy.deepcopy(out)
    prior_tampered["reservations"][0]["amount_raw"] = "31"
    expect_error(lambda: compile_reservation_reconciliation(env, second_req, [prior_tampered]))

    again = compile_reservation_reconciliation(env, request(env))
    assert again["reservation_reconciliation_sha256"] == out["reservation_reconciliation_sha256"]

    print("THF_BUDGET_ENVELOPE_RESERVATION_RECONCILIATION_TESTS=PASS")
    print("TRANSACTION_CREATED=FALSE")
    print("TRANSACTION_SIGNED=FALSE")
    print("TRANSACTION_SUBMITTED=FALSE")
    print("FINANCIAL_EFFECT=FALSE")
    print("PRIVATE_KEY_USED=FALSE")
    print("WAVE_UNTOUCHED=TRUE")


if __name__ == "__main__":
    main()
