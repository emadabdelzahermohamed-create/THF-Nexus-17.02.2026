#!/usr/bin/env python3
from __future__ import annotations

import copy

from reward_vesting_budget_envelope import CANONICAL_MINT, CANONICAL_NETWORK, canonical_sha256, compile_budget_envelope


def base_bound(eligible: bool = True):
    body = {
        "gate": "THF_TOKENOPS_POLICY_COMPLETION_BOUND_UNSIGNED_ADMISSION_V1",
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "intent": "reward_epoch",
        "policy_completion_evidence_sha256": "1" * 64,
        "base_admission_sha256": "2" * 64,
        "authoritative_policy_sha256": "3" * 64,
        "treasury_policy_sha256": "4" * 64,
        "simulation_review_eligible": eligible,
        "blockers": [] if eligible else ["production_caps_not_approved"],
        "simulation_execution_permitted": False,
        "execution_authorized": False,
        "transaction_created": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "broadcast_allowed": False,
        "financial_effect": False,
        "private_key_used": False,
        "wave_mawja_untouched": True,
    }
    body["bound_admission_sha256"] = canonical_sha256(body)
    return body


def policy(caps=True):
    return {
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "economics": {
            "active_user_revenue_share": 0.35,
            "approved_supply_floor_target_ui": "8000000000",
            "burn_source_policy": "treasury_controlled_balances_only",
        },
        "distribution_controls": {
            "anti_whale_cap_required": True,
            "per_user_cap": "100",
            "epoch_budget_cap": "150",
        } if caps else {
            "anti_whale_cap_required": True,
            "per_user_cap": None,
            "epoch_budget_cap": None,
        },
    }


def treasury():
    return {
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "approval_classes": {
            "reward_epoch": {"minimum_approvals": 2, "execution": "external_multisig"},
            "vesting_settlement": {"minimum_approvals": 2, "execution": "external_multisig"},
        },
    }


def reward_request(bound):
    return {
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "intent": "reward_epoch",
        "request_id": "epoch:test",
        "bound_admission_sha256": bound["bound_admission_sha256"],
        "epoch_revenue_minor": "10001",
        "entries": [
            {"subject_id": "u2", "wallet": "wallet2", "amount_raw": "40"},
            {"subject_id": "u1", "wallet": "wallet1", "amount_raw": "50"},
        ],
    }


def expect_error(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def main():
    b = base_bound(True)
    req = reward_request(b)

    out = compile_budget_envelope(b, policy(True), treasury(), req)
    assert out["review_eligible"] is True
    assert out["budget_controls"]["total_requested_raw"] == "90"
    assert out["revenue"]["active_user_share_bps"] == 3500
    assert out["revenue"]["active_user_share_minor"] == "3500"
    assert out["revenue"]["token_price_inferred"] is False
    assert [x["subject_id"] for x in out["entries"]] == ["u1", "u2"]
    assert out["execution"]["transaction_created"] is False
    assert out["execution"]["transaction_signed"] is False
    assert out["execution"]["transaction_submitted"] is False
    assert out["execution"]["financial_effect"] is False

    prod = compile_budget_envelope(b, policy(False), treasury(), req)
    assert prod["review_eligible"] is False
    assert prod["budget_controls"]["per_user_cap_raw"] is None
    assert prod["budget_controls"]["epoch_budget_cap_raw"] is None
    assert "anti_whale_per_user_cap_not_authoritatively_configured" in prod["blockers"]
    assert "epoch_budget_cap_not_authoritatively_configured" in prod["blockers"]

    blocked = compile_budget_envelope(base_bound(False), policy(True), treasury(), reward_request(base_bound(False)))
    assert blocked["review_eligible"] is False
    assert "bound_admission_not_review_eligible" in blocked["blockers"]

    per_user = reward_request(b)
    per_user["entries"][0]["amount_raw"] = "101"
    over = compile_budget_envelope(b, policy(True), treasury(), per_user)
    assert over["review_eligible"] is False
    assert "per_user_cap_exceeded:u2" in over["blockers"]

    epoch = reward_request(b)
    epoch["entries"] = [
        {"subject_id": "u1", "wallet": "w1", "amount_raw": "80"},
        {"subject_id": "u2", "wallet": "w2", "amount_raw": "80"},
    ]
    over = compile_budget_envelope(b, policy(True), treasury(), epoch)
    assert over["review_eligible"] is False
    assert "epoch_budget_cap_exceeded" in over["blockers"]

    tampered = copy.deepcopy(b)
    tampered["blockers"] = ["tampered"]
    expect_error(lambda: compile_budget_envelope(tampered, policy(True), treasury(), req))

    sensitive = reward_request(b)
    sensitive["private_key"] = "forbidden"
    expect_error(lambda: compile_budget_envelope(b, policy(True), treasury(), sensitive))

    vest_req = {
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "intent": "vesting_settlement",
        "request_id": "vesting:test",
        "bound_admission_sha256": b["bound_admission_sha256"],
        "entries": [
            {"subject_id": "v1", "wallet": "vw1", "amount_raw": "70", "start_unix": 10, "cliff_unix": 20, "end_unix": 30}
        ],
    }
    vest = compile_budget_envelope(b, policy(True), treasury(), vest_req)
    assert vest["review_eligible"] is True
    assert vest["revenue"] is None
    assert vest["approval_requirement"]["minimum_approvals"] == 2
    assert vest["execution"]["settlement_executed"] is False

    again = compile_budget_envelope(b, policy(True), treasury(), req)
    assert again["envelope_sha256"] == out["envelope_sha256"]

    print("THF_REWARD_VESTING_BUDGET_ENVELOPE_TESTS=PASS")
    print("TRANSACTION_CREATED=FALSE")
    print("TRANSACTION_SIGNED=FALSE")
    print("TRANSACTION_SUBMITTED=FALSE")
    print("FINANCIAL_EFFECT=FALSE")
    print("PRIVATE_KEY_USED=FALSE")
    print("WAVE_UNTOUCHED=TRUE")


if __name__ == "__main__":
    main()
