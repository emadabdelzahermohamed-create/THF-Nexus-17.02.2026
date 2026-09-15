import unittest
from reward_eligibility_commitment import build
H="a"*64; P="b"*64
class T(unittest.TestCase):
 def test_deterministic_and_nonexecuting(self):
  rows=[{"subject_id":"u2","weight":2,"provenance":"core:v1"},{"subject_id":"u1","weight":3,"provenance":"pulse:v1"}]
  a=build(epoch_id="e1",source_sha256=H,policy_sha256=P,rows=rows)
  b=build(epoch_id="e1",source_sha256=H,policy_sha256=P,rows=list(reversed(rows)))
  self.assertEqual(a["eligibility_commitment_sha256"],b["eligibility_commitment_sha256"])
  self.assertEqual(a["total_weight"],5); self.assertFalse(a["financial_execution"])
  self.assertFalse(a["fabricated_activity_allowed"]); self.assertEqual(a["status"],"COMMITTED_FOR_TREASURY_PLANNING")
 def test_duplicate_fails_closed(self):
  x=build(epoch_id="e",source_sha256=H,policy_sha256=P,rows=[{"subject_id":"u","weight":1,"provenance":"x"},{"subject_id":"u","weight":1,"provenance":"x"}])
  self.assertEqual(x["status"],"BLOCKED"); self.assertIn("DUPLICATE_SUBJECT",x["blockers"])
 def test_missing_provenance_fails(self):
  x=build(epoch_id="e",source_sha256=H,policy_sha256=P,rows=[{"subject_id":"u","weight":1}])
  self.assertIn("INVALID_ELIGIBILITY_ROW",x["blockers"])
if __name__=="__main__": unittest.main()
