import unittest
from reward_eligibility_commitment import build
from reward_allocation_engine import allocate

H="a"*64
class RewardAllocationTests(unittest.TestCase):
    def eligibility(self):
        return build(epoch_id="e1",source_sha256=H,policy_sha256=H,rows=[
            {"subject_id":"u2","weight":1,"provenance":"core:v1"},
            {"subject_id":"u1","weight":3,"provenance":"pulse:v1"}])
    def test_35pct_and_non_execution(self):
        out=allocate(epoch_id="e1",revenue_units=100000,eligibility=self.eligibility(),anti_whale_bps=3500)
        self.assertEqual(out["active_user_pool_units"],35000)
        self.assertEqual(out["status"],"ALLOCATION_PLAN_READY")
        self.assertFalse(out["sign"]); self.assertFalse(out["broadcast"]); self.assertFalse(out["financial_execution"])
    def test_deterministic(self):
        a=allocate(epoch_id="e1",revenue_units=123456,eligibility=self.eligibility(),anti_whale_bps=3500)
        b=allocate(epoch_id="e1",revenue_units=123456,eligibility=self.eligibility(),anti_whale_bps=3500)
        self.assertEqual(a["allocation_plan_sha256"],b["allocation_plan_sha256"])
    def test_anti_whale_cap(self):
        out=allocate(epoch_id="e1",revenue_units=100000,eligibility=self.eligibility(),anti_whale_bps=1000)
        self.assertTrue(all(x["amount_units"]<=out["per_subject_cap_units"] for x in out["allocations"]))
        self.assertGreater(out["remainder_units"],0)
    def test_bad_commitment_blocks(self):
        e=self.eligibility(); e["status"]="BLOCKED"
        out=allocate(epoch_id="e1",revenue_units=100,eligibility=e)
        self.assertEqual(out["status"],"BLOCKED")
        self.assertEqual(out["allocations"],[])
if __name__=="__main__": unittest.main()
