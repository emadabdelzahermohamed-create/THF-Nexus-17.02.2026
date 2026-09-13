#!/usr/bin/env python3
from __future__ import annotations
import copy
from reservation_epoch_close_snapshot import CANONICAL_MINT,CANONICAL_NETWORK,canonical_sha256,compile_epoch_close_snapshot

def lifecycle(prior=None, events=None, active=None, blockers=None):
    events=list(events or [{"event_id":"e1","action":"release","reservation_id":"r1","subject_id":"u1","wallet":"w1","released_amount_raw":"30","replacement":None}])
    active=list([{"reservation_id":"r2","subject_id":"u2","wallet":"w2","amount_raw":"20"}] if active is None else active)
    source_total=50
    active_total=sum(int(x["amount_raw"]) for x in active)
    body={
        "schema":"thf-tokenops-reservation-lifecycle-accounting/v1","network":CANONICAL_NETWORK,"mint":CANONICAL_MINT,
        "request_id":"lifecycle:test","budget_envelope_sha256":"a"*64,"source_reservation_reconciliation_sha256":"b"*64,
        "prior_reservation_lifecycle_sha256":prior,"active_reservations":active,"lifecycle_events":events,
        "accounting":{"source_reserved_total_raw":str(source_total),"active_reserved_total_raw":str(active_total),"released_or_cancelled_net_raw":str(source_total-active_total),"active_reservation_count":len(active),"lifecycle_event_count":len(events)},
        "lifecycle_review_eligible":not blockers,"blockers":list(blockers or []),
        "execution":{"transaction_created":False,"transaction_signed":False,"transaction_submitted":False,"broadcast_allowed":False,"financial_effect":False,"settlement_executed":False,"burn_executed":False,"treasury_migrated":False,"dao_decision_executed":False,"private_key_used":False,"external_multisig_required":True,"wave_mawja_untouched":True},
    }
    body["reservation_lifecycle_sha256"]=canonical_sha256(body)
    return body

def req(lc,prior_snapshot=None):
    return {"network":CANONICAL_NETWORK,"mint":CANONICAL_MINT,"epoch_id":"epoch-2026-09","request_id":"snapshot:test","budget_envelope_sha256":lc["budget_envelope_sha256"],"source_reservation_reconciliation_sha256":lc["source_reservation_reconciliation_sha256"],"source_reservation_lifecycle_sha256":lc["reservation_lifecycle_sha256"],"expected_prior_epoch_close_snapshot_sha256":None if prior_snapshot is None else prior_snapshot["epoch_close_snapshot_sha256"]}

def expect_error(fn):
    try: fn()
    except ValueError: return
    raise AssertionError("expected ValueError")

def main():
    first=lifecycle()
    snap1=compile_epoch_close_snapshot(first,req(first))
    assert snap1["epoch_close_review_eligible"] is True
    assert snap1["journal_event_count"]==1
    assert snap1["accounting"]["active_reserved_total_raw"]=="20"

    second_events=first["lifecycle_events"]+[{"event_id":"e2","action":"cancel","reservation_id":"r2","subject_id":"u2","wallet":"w2","released_amount_raw":"20","replacement":None}]
    second=lifecycle(prior=first["reservation_lifecycle_sha256"],events=second_events,active=[])
    snap2=compile_epoch_close_snapshot(second,req(second,snap1),snap1)
    assert snap2["journal_event_count"]==2
    assert snap2["accounting"]["active_reserved_total_raw"]=="0"
    assert snap2["prior_epoch_close_snapshot_sha256"]==snap1["epoch_close_snapshot_sha256"]

    bad_req=req(second,snap1); bad_req["expected_prior_epoch_close_snapshot_sha256"]="f"*64
    expect_error(lambda: compile_epoch_close_snapshot(second,bad_req,snap1))

    fork=copy.deepcopy(second); fork["prior_reservation_lifecycle_sha256"]="e"*64; fork.pop("reservation_lifecycle_sha256"); fork["reservation_lifecycle_sha256"]=canonical_sha256(fork)
    expect_error(lambda: compile_epoch_close_snapshot(fork,req(fork,snap1),snap1))

    rollback=lifecycle(prior=first["reservation_lifecycle_sha256"],events=first["lifecycle_events"],active=first["active_reservations"])
    expect_error(lambda: compile_epoch_close_snapshot(rollback,req(rollback,snap1),snap1))

    duplicate=copy.deepcopy(first); duplicate["lifecycle_events"].append(copy.deepcopy(duplicate["lifecycle_events"][0])); duplicate["accounting"]["lifecycle_event_count"]=2; duplicate.pop("reservation_lifecycle_sha256"); duplicate["reservation_lifecycle_sha256"]=canonical_sha256(duplicate)
    expect_error(lambda: compile_epoch_close_snapshot(duplicate,req(duplicate)))

    badacct=copy.deepcopy(first); badacct["accounting"]["active_reserved_total_raw"]="21"; badacct.pop("reservation_lifecycle_sha256"); badacct["reservation_lifecycle_sha256"]=canonical_sha256(badacct)
    expect_error(lambda: compile_epoch_close_snapshot(badacct,req(badacct)))

    blocked=lifecycle(blockers=["production_caps_not_approved"])
    bs=compile_epoch_close_snapshot(blocked,req(blocked))
    assert bs["epoch_close_review_eligible"] is False and "production_caps_not_approved" in bs["blockers"]

    sensitive=req(first); sensitive["private_key"]="forbidden"
    expect_error(lambda: compile_epoch_close_snapshot(first,sensitive))

    again=compile_epoch_close_snapshot(first,req(first))
    assert again["epoch_close_snapshot_sha256"]==snap1["epoch_close_snapshot_sha256"]
    for key in ("transaction_created","transaction_signed","transaction_submitted","broadcast_allowed","financial_effect","settlement_executed","burn_executed","treasury_migrated","dao_decision_executed","private_key_used"):
        assert snap2["execution"][key] is False
    assert snap2["execution"]["wave_mawja_untouched"] is True
    print("THF_RESERVATION_EPOCH_CLOSE_SNAPSHOT_TESTS=PASS")
    print("TRANSACTION_CREATED=FALSE")
    print("TRANSACTION_SIGNED=FALSE")
    print("TRANSACTION_SUBMITTED=FALSE")
    print("FINANCIAL_EFFECT=FALSE")
    print("PRIVATE_KEY_USED=FALSE")
    print("WAVE_UNTOUCHED=TRUE")

if __name__=="__main__": main()
