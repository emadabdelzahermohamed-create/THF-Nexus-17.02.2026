#!/usr/bin/env python3
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("reward_manifest", HERE / "reward_manifest.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

sample = json.loads((HERE / "examples" / "reward_epoch.sample.json").read_text())

m1 = mod.build_manifest(copy.deepcopy(sample))
m2 = mod.build_manifest(copy.deepcopy(sample))
assert m1 == m2, "manifest must be deterministic"
assert m1["revenue"]["active_user_share_minor"] == "350000"
assert m1["execution"]["transaction_created"] is False
assert m1["execution"]["transaction_signed"] is False
assert m1["execution"]["transaction_submitted"] is False
assert m1["eligibility"]["eligible_count"] == 2
assert len(m1["allocations"]) == 2
# user-a would receive 62.5B raw but is capped at 40B; user-b receives 37.5B.
# The 22.5B remainder remains in treasury and is deliberately not redistributed.
assert m1["treasury_budget"]["allocated_raw"] == "77500000000"
assert m1["treasury_budget"]["unallocated_raw"] == "22500000000"

bad = copy.deepcopy(sample)
bad["mint"] = "bad"
try:
    mod.build_manifest(bad)
    raise AssertionError("wrong mint must fail")
except ValueError:
    pass

bad = copy.deepcopy(sample)
bad["participants"][0]["anti_sybil_pass"] = False
m3 = mod.build_manifest(bad)
assert m3["eligibility"]["eligible_count"] == 1

print("THF_TOKENOPS_REWARD_TESTS=PASS")
print("TRANSACTION_CREATED=FALSE")
print("TRANSACTION_SIGNED=FALSE")
print("TRANSACTION_SUBMITTED=FALSE")
