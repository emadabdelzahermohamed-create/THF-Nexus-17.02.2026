#!/usr/bin/env python3
import copy
from epoch_accounting_lineage import *

def digest(obj, field):
    obj[field] = canonical_sha256(obj); return obj

def close(epoch, active="60", released="40"):
    source = str(int(active) + int(released))
    obj = {"schema": SNAPSHOT_SCHEMA, "network": CANONICAL_NETWORK, "mint": CANONICAL_MINT, "epoch_id": epoch, "blockers": ["production_caps_not_approved"], "accounting": {"source_reserved_total_raw": source, "active_reserved_total_raw": active, "released_or_cancelled_net_raw": released}, "execution": {"transaction_created": False, "transaction_signed": False, "transaction_submitted": False, "broadcast_allowed": False, "financial_effect": False, "settlement_executed": False, "burn_executed": False, "treasury_migrated": False, "dao_decision_executed": False, "private_key_used": False, "wave_mawja_untouched": True}}
    return digest(obj, "epoch_close_snapshot_sha256")

def roll(c, nxt, budget="35"):
    carry = c["accounting"]["active_reserved_total_raw"]
    obj = {"schema": ROLLFORWARD_SCHEMA, "network": CANONICAL_NETWORK, "mint": CANONICAL_MINT, "prior_epoch_id": c["epoch_id"], "next_epoch_id": nxt, "request_id": "rf", "prior_epoch_close_snapshot_sha256": c["epoch_close_snapshot_sha256"], "next_budget_envelope_sha256": "1" * 64, "accounting": {"carry_forward_active_reserved_raw": carry, "next_approved_budget_raw": budget, "next_opening_accounting_total_raw": str(int(carry) + int(budget))}, "rollforward_review_eligible": False, "blockers": ["production_caps_not_approved"], "execution": {"transaction_created": False, "transaction_signed": False, "transaction_submitted": False, "broadcast_allowed": False, "financial_effect": False, "settlement_executed": False, "burn_executed": False, "treasury_migrated": False, "dao_decision_executed": False, "private_key_used": False, "external_multisig_required": True, "wave_mawja_untouched": True}}
    return digest(obj, "cross_epoch_rollforward_sha256")

def request(c, r, previous=None):
    return {"network": CANONICAL_NETWORK, "mint": CANONICAL_MINT, "prior_epoch_close_snapshot_sha256": c["epoch_close_snapshot_sha256"], "cross_epoch_rollforward_sha256": r["cross_epoch_rollforward_sha256"], "previous_lineage_checkpoint_sha256": None if previous is None else previous["lineage_checkpoint_sha256"], "request_id": "lineage-test"}

def expect_fail(fn):
    try: fn()
    except ValueError: return
    raise AssertionError("expected fail-closed rejection")

c1 = close("E1"); r1 = roll(c1, "E2")
l1 = compile_lineage_checkpoint(c1, r1, request(c1, r1))
assert len(l1["history"]) == 1 and l1["lineage_review_eligible"] is False
assert l1["execution"]["financial_effect"] is False and l1["execution"]["transaction_signed"] is False
c2 = close("E2", active="25", released="10"); r2 = roll(c2, "E3", budget="20")
l2 = compile_lineage_checkpoint(c2, r2, request(c2, r2, l1), l1)
assert [x["next_epoch_id"] for x in l2["history"]] == ["E2", "E3"]
assert l2["previous_lineage_checkpoint_sha256"] == l1["lineage_checkpoint_sha256"]
x = request(c2, r2, l1); x["previous_lineage_checkpoint_sha256"] = "0" * 64; expect_fail(lambda: compile_lineage_checkpoint(c2, r2, x, l1))
x = copy.deepcopy(r2); x["accounting"]["next_opening_accounting_total_raw"] = "999"; x["cross_epoch_rollforward_sha256"] = canonical_sha256({k:v for k,v in x.items() if k != "cross_epoch_rollforward_sha256"}); expect_fail(lambda: compile_lineage_checkpoint(c2, x, request(c2, x, l1), l1))
x = copy.deepcopy(c2); x["accounting"]["active_reserved_total_raw"] = "24"; x["epoch_close_snapshot_sha256"] = canonical_sha256({k:v for k,v in x.items() if k != "epoch_close_snapshot_sha256"}); expect_fail(lambda: compile_lineage_checkpoint(x, r2, request(x, r2, l1), l1))
x = copy.deepcopy(c2); x["private_key"] = "forbidden"; expect_fail(lambda: compile_lineage_checkpoint(x, r2, request(c2, r2, l1), l1))
x = copy.deepcopy(r2); x["execution"]["financial_effect"] = True; x["cross_epoch_rollforward_sha256"] = canonical_sha256({k:v for k,v in x.items() if k != "cross_epoch_rollforward_sha256"}); expect_fail(lambda: compile_lineage_checkpoint(c2, x, request(c2, x, l1), l1))
expect_fail(lambda: compile_lineage_checkpoint(c1, r1, request(c1, r1, l1), l1))
print("PASS: multi-epoch lineage gate fail-closed invariants")
