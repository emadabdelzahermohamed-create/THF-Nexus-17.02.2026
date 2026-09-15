import unittest
from reward_epoch_commitment import commit

H="a"*64
BASE={"status":"ALLOCATION_PLAN_READY","active_user_bps":3500,"sign":False,"broadcast":False,"financial_execution":False,
      "epoch_id":"e1","allocation_plan_sha256":"b"*64,"eligibility_commitment_sha256":"c"*64,"allocated_units":350,"remainder_units":0}
class TestRewardEpochCommitment(unittest.TestCase):
    def test_commits_complete_evidence_without_execution(self):
        r=commit(allocation=BASE,revenue_evidence_sha256=H,accounting_ledger_sha256=H,policy_sha256=H,source_commit_sha="d"*40)
        self.assertEqual(r["status"],"COMMITTED_FOR_SIMULATION")
        self.assertFalse(r["sign"]); self.assertFalse(r["broadcast"]); self.assertFalse(r["financial_execution"])
        self.assertEqual(len(r["reward_epoch_commitment_sha256"]),64)
    def test_missing_evidence_fails_closed(self):
        r=commit(allocation=BASE,revenue_evidence_sha256="",accounting_ledger_sha256=H,policy_sha256=H,source_commit_sha="d"*40)
        self.assertEqual(r["status"],"BLOCKED")
    def test_share_or_execution_drift_blocks(self):
        bad=dict(BASE); bad["active_user_bps"]=3400; bad["broadcast"]=True
        r=commit(allocation=bad,revenue_evidence_sha256=H,accounting_ledger_sha256=H,policy_sha256=H,source_commit_sha="d"*40)
        self.assertEqual(r["status"],"BLOCKED")
        self.assertIn("ACTIVE_USER_SHARE_MISMATCH",r["blockers"]); self.assertIn("UNSAFE_ALLOCATION_FLAGS",r["blockers"])
if __name__=="__main__": unittest.main()
