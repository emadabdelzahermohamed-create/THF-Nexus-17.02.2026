#!/usr/bin/env python3
import copy, hashlib
from pathlib import Path
from accounting_policy_seal import *
from epoch_accounting_lineage import canonical_sha256, LINEAGE_SCHEMA, CANONICAL_MINT, CANONICAL_NETWORK

BASE = Path(__file__).resolve().parent
POLICY_TEXT = (BASE / "policy.json").read_text(encoding="utf-8")
TREASURY_TEXT = (BASE / "treasury_policy.json").read_text(encoding="utf-8")
LINEAGE_SOURCE = (BASE / "epoch_accounting_lineage.py").read_text(encoding="utf-8")


def lineage():
    obj = {
        "schema": LINEAGE_SCHEMA,
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "request_id": "seal-fixture",
        "previous_lineage_checkpoint_sha256": None,
        "prior_epoch_id": "E1",
        "next_epoch_id": "E2",
        "epoch_close_snapshot_sha256": "1" * 64,
        "cross_epoch_rollforward_sha256": "2" * 64,
        "history": [{"prior_epoch_id": "E1", "next_epoch_id": "E2", "epoch_close_snapshot_sha256": "1" * 64, "cross_epoch_rollforward_sha256": "2" * 64}],
        "lineage_review_eligible": False,
        "blockers": ["production_caps_not_approved"],
        "execution": {"transaction_created": False, "transaction_signed": False, "transaction_submitted": False, "broadcast_allowed": False, "financial_effect": False, "settlement_executed": False, "burn_executed": False, "treasury_migrated": False, "dao_decision_executed": False, "private_key_used": False, "external_multisig_required": True, "wave_mawja_untouched": True},
    }
    obj["lineage_checkpoint_sha256"] = canonical_sha256(obj)
    return obj


def request(l):
    return {
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "lineage_checkpoint_sha256": l["lineage_checkpoint_sha256"],
        "policy_file_sha256": file_sha256(POLICY_TEXT),
        "policy_git_blob_sha": git_blob_sha1(POLICY_TEXT),
        "treasury_policy_file_sha256": file_sha256(TREASURY_TEXT),
        "treasury_policy_git_blob_sha": git_blob_sha1(TREASURY_TEXT),
        "lineage_source_sha256": hashlib.sha256(LINEAGE_SOURCE.encode("utf-8")).hexdigest(),
        "source_commit_sha": "a" * 40,
        "request_id": "seal-test",
    }


def expect_fail(fn):
    try: fn()
    except ValueError: return
    raise AssertionError("expected fail-closed rejection")

l = lineage(); r = request(l)
seal = compile_accounting_policy_seal(l, POLICY_TEXT, TREASURY_TEXT, r)
assert seal["seal_review_eligible"] is False
assert "anti_whale_caps_not_authoritatively_configured" in seal["blockers"]
assert "production_signer_policy_not_approved" in seal["blockers"]
assert seal["execution"]["financial_effect"] is False
assert seal["policy_invariants"]["active_user_revenue_share"] == "35%"
assert seal["policy_invariants"]["approved_supply_floor_target_ui"] == "8000000000"

x = copy.deepcopy(r); x["policy_file_sha256"] = "0" * 64
expect_fail(lambda: compile_accounting_policy_seal(l, POLICY_TEXT, TREASURY_TEXT, x))
x = copy.deepcopy(r); x["policy_git_blob_sha"] = "0" * 40
expect_fail(lambda: compile_accounting_policy_seal(l, POLICY_TEXT, TREASURY_TEXT, x))
x = copy.deepcopy(r); x["lineage_checkpoint_sha256"] = "0" * 64
expect_fail(lambda: compile_accounting_policy_seal(l, POLICY_TEXT, TREASURY_TEXT, x))
x = copy.deepcopy(l); x["execution"]["financial_effect"] = True; x["lineage_checkpoint_sha256"] = canonical_sha256({k:v for k,v in x.items() if k != "lineage_checkpoint_sha256"})
expect_fail(lambda: compile_accounting_policy_seal(x, POLICY_TEXT, TREASURY_TEXT, request(x)))
x = POLICY_TEXT.replace('"active_user_revenue_share": 0.35', '"active_user_revenue_share": 0.36')
y = copy.deepcopy(r); y["policy_file_sha256"] = file_sha256(x); y["policy_git_blob_sha"] = git_blob_sha1(x)
expect_fail(lambda: compile_accounting_policy_seal(l, x, TREASURY_TEXT, y))
x = TREASURY_TEXT.replace('"minimum_approvals": 3', '"minimum_approvals": 1', 1)
y = copy.deepcopy(r); y["treasury_policy_file_sha256"] = file_sha256(x); y["treasury_policy_git_blob_sha"] = git_blob_sha1(x)
expect_fail(lambda: compile_accounting_policy_seal(l, POLICY_TEXT, x, y))
x = copy.deepcopy(r); x["private_key"] = "forbidden"
expect_fail(lambda: compile_accounting_policy_seal(l, POLICY_TEXT, TREASURY_TEXT, x))

print("PASS: policy/source-bound accounting seal fail-closed invariants")
