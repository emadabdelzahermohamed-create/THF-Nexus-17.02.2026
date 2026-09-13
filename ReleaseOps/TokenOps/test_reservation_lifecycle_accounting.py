#!/usr/bin/env python3
from __future__ import annotations

import copy

from reservation_lifecycle_accounting import CANONICAL_MINT, CANONICAL_NETWORK, canonical_sha256, compile_reservation_lifecycle

def source(blocked=False):
    body = {
        "schema": "thf-tokenops-budget-reservation-reconciliation/v1", "network": CANONICAL_NETWORK, "mint": CANONICAL_MINT,
        "intent": "reward_epoch", "request_id": "reserve:test", "budget_envelope_sha256": "a" * 64,
        "bound_admission_sha256": "b" * 64, "policy_completion_evidence_sha256": "c" * 64,
        "prior_reservation_count": 0, "new_reservation_count": 2,
        "reservations": [{"reservation_id": "r1", "subject_id": "u1", "wallet": "w1", "amount_raw": "30"}, {"reservation_id": "r2", "subject_id": "u2", "wallet": "w2", "amount_raw": "20"}],
        "allocation_status": [], "accounting": {"budget_total_raw": "90", "reserved_total_raw": "50", "remaining_budget_raw": "40", "overcommitted": False},
        "reservation_review_eligible": not blocked, "blockers": ["production_caps_not_approved"] if blocked else [],
        "execution": {"transaction_created": False, "transaction_signed": False, "transaction_submitted": False, "broadcast_allowed": False, "financial_effect": False, "settlement_executed": False, "private_key_used": False, "external_multisig_required": True, "wave_mawja_untouched": True},
    }
    body["reservation_reconciliation_sha256"] = canonical_sha256(body)
    return body

def request(src, operations, prior_sha=None):
    return {"network": CANONICAL_NETWORK, "mint": CANONICAL_MINT, "request_id": "lifecycle:test", "budget_envelope_sha256": src["budget_envelope_sha256"], "source_reservation_reconciliation_sha256": src["reservation_reconciliation_sha256"], "expected_prior_reservation_lifecycle_sha256": prior_sha, "operations": operations}

def expect_error(fn):
    try: fn()
    except ValueError: return
    raise AssertionError("expected ValueError")

def main():
    src = source(False)
    released = compile_reservation_lifecycle(src, request(src, [{"event_id": "e1", "action": "release", "reservation_id": "r1"}]))
    assert released["lifecycle_review_eligible"] is True
    assert released["accounting"]["source_reserved_total_raw"] == "50"
    assert released["accounting"]["active_reserved_total_raw"] == "20"
    assert released["accounting"]["released_or_cancelled_net_raw"] == "30"
    assert [x["reservation_id"] for x in released["active_reservations"]] == ["r2"]
    cancelled = compile_reservation_lifecycle(src, request(src, [{"event_id": "e2", "action": "cancel", "reservation_id": "r2"}], released["reservation_lifecycle_sha256"]), released)
    assert cancelled["accounting"]["active_reserved_total_raw"] == "0"
    assert cancelled["accounting"]["lifecycle_event_count"] == 2
    replaced = compile_reservation_lifecycle(src, request(src, [{"event_id": "e3", "action": "replace", "reservation_id": "r1", "replacement_reservation_id": "r1b", "replacement_amount_raw": "25"}]))
    assert replaced["accounting"]["active_reserved_total_raw"] == "45"
    assert replaced["accounting"]["released_or_cancelled_net_raw"] == "5"
    assert any(x["reservation_id"] == "r1b" and x["amount_raw"] == "25" for x in replaced["active_reservations"])
    expect_error(lambda: compile_reservation_lifecycle(src, request(src, [{"event_id": "e4", "action": "replace", "reservation_id": "r1", "replacement_reservation_id": "r1x", "replacement_amount_raw": "31"}])))
    expect_error(lambda: compile_reservation_lifecycle(src, request(src, [{"event_id": "e5", "action": "release", "reservation_id": "nope"}])))
    expect_error(lambda: compile_reservation_lifecycle(src, request(src, [{"event_id": "e1", "action": "cancel", "reservation_id": "r2"}], released["reservation_lifecycle_sha256"]), released))
    expect_error(lambda: compile_reservation_lifecycle(src, request(src, [{"event_id": "e6", "action": "cancel", "reservation_id": "r2"}], "f" * 64), released))
    expect_error(lambda: compile_reservation_lifecycle(src, request(src, [{"event_id": "e7", "action": "cancel", "reservation_id": "r2"}], "e" * 64)))
    tampered_src = copy.deepcopy(src); tampered_src["reservations"][0]["amount_raw"] = "31"
    expect_error(lambda: compile_reservation_lifecycle(tampered_src, request(src, [{"event_id": "e8", "action": "release", "reservation_id": "r1"}])))
    tampered_prior = copy.deepcopy(released); tampered_prior["active_reservations"][0]["amount_raw"] = "21"
    expect_error(lambda: compile_reservation_lifecycle(src, request(src, [{"event_id": "e9", "action": "cancel", "reservation_id": "r2"}], released["reservation_lifecycle_sha256"]), tampered_prior))
    sensitive = request(src, [{"event_id": "e10", "action": "release", "reservation_id": "r1"}]); sensitive["private_key"] = "forbidden"
    expect_error(lambda: compile_reservation_lifecycle(src, sensitive))
    blocked_src = source(True)
    blocked = compile_reservation_lifecycle(blocked_src, request(blocked_src, [{"event_id": "e11", "action": "release", "reservation_id": "r1"}]))
    assert blocked["lifecycle_review_eligible"] is False and "production_caps_not_approved" in blocked["blockers"]
    again = compile_reservation_lifecycle(src, request(src, [{"event_id": "e1", "action": "release", "reservation_id": "r1"}]))
    assert again["reservation_lifecycle_sha256"] == released["reservation_lifecycle_sha256"]
    for key in ("transaction_created", "transaction_signed", "transaction_submitted", "broadcast_allowed", "financial_effect", "settlement_executed", "burn_executed", "treasury_migrated", "dao_decision_executed", "private_key_used"):
        assert released["execution"][key] is False
    assert released["execution"]["wave_mawja_untouched"] is True
    print("THF_RESERVATION_LIFECYCLE_ACCOUNTING_TESTS=PASS")
    print("TRANSACTION_CREATED=FALSE")
    print("TRANSACTION_SIGNED=FALSE")
    print("TRANSACTION_SUBMITTED=FALSE")
    print("FINANCIAL_EFFECT=FALSE")
    print("PRIVATE_KEY_USED=FALSE")
    print("WAVE_UNTOUCHED=TRUE")

if __name__ == "__main__": main()
