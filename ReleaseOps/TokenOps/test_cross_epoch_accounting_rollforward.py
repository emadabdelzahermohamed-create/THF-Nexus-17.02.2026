#!/usr/bin/env python3
import copy
from cross_epoch_accounting_rollforward import *

def digest(o,field):
    o[field]=canonical_sha256(o); return o

def close():
    o={"schema":SNAPSHOT_SCHEMA,"network":CANONICAL_NETWORK,"mint":CANONICAL_MINT,"epoch_id":"E1","blockers":["production_caps_not_approved"],"accounting":{"source_reserved_total_raw":"100","active_reserved_total_raw":"60","released_or_cancelled_net_raw":"40"},"execution":{"transaction_created":False,"transaction_signed":False,"transaction_submitted":False,"broadcast_allowed":False,"financial_effect":False,"settlement_executed":False,"burn_executed":False,"treasury_migrated":False,"dao_decision_executed":False,"private_key_used":False,"wave_mawja_untouched":True}}
    return digest(o,"epoch_close_snapshot_sha256")

def budget():
    o={"network":CANONICAL_NETWORK,"mint":CANONICAL_MINT,"epoch_id":"E2","blockers":["production_caps_not_approved"],"accounting":{"approved_budget_raw":"35"}}
    return digest(o,"budget_envelope_sha256")

def req(c,b): return {"network":CANONICAL_NETWORK,"mint":CANONICAL_MINT,"prior_epoch_close_snapshot_sha256":c["epoch_close_snapshot_sha256"],"next_budget_envelope_sha256":b["budget_envelope_sha256"],"next_epoch_id":"E2","request_id":"test"}

def expect_fail(fn):
    try: fn()
    except ValueError: return
    raise AssertionError("expected fail-closed rejection")

c=close(); b=budget(); r=req(c,b); out=compile_cross_epoch_rollforward(c,b,r)
assert out["accounting"]["next_opening_accounting_total_raw"]=="95"
assert out["rollforward_review_eligible"] is False
assert out["execution"]["financial_effect"] is False and out["execution"]["transaction_signed"] is False
x=copy.deepcopy(r); x["prior_epoch_close_snapshot_sha256"]="0"*64; expect_fail(lambda:compile_cross_epoch_rollforward(c,b,x))
x=copy.deepcopy(b); x["accounting"]["approved_budget_raw"]="36"; expect_fail(lambda:compile_cross_epoch_rollforward(c,x,r))
x=copy.deepcopy(r); x["next_epoch_id"]="E1"; expect_fail(lambda:compile_cross_epoch_rollforward(c,b,x))
x=copy.deepcopy(c); x["private_key"]="forbidden"; expect_fail(lambda:compile_cross_epoch_rollforward(x,b,r))
x=copy.deepcopy(c); x["execution"]["financial_effect"]=True; x["epoch_close_snapshot_sha256"]=canonical_sha256({k:v for k,v in x.items() if k!="epoch_close_snapshot_sha256"}); expect_fail(lambda:compile_cross_epoch_rollforward(x,b,req(x,b)))
print("PASS: cross-epoch roll-forward gate fail-closed invariants")
