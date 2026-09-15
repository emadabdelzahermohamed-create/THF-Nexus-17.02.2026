import unittest
from treasury_control_plane import Recipient,plan_distribution,validate_vesting,burn_gap

class TestTreasury(unittest.TestCase):
 def test_35pct_and_cap(self):
  p=plan_distribution(1_000_000,[Recipient('a','wa','9'),Recipient('b','wb','1')],max_recipient_bps=5000)
  self.assertEqual(p['pool_atomic'],350000); self.assertFalse(p['broadcast']); self.assertLessEqual(max(x['amount_atomic'] for x in p['allocations']),175000)
 def test_deterministic(self):
  rs=[Recipient('b','wb','1'),Recipient('a','wa','1')]
  self.assertEqual(plan_distribution(10000,rs)['manifest_sha256'],plan_distribution(10000,list(reversed(rs)))['manifest_sha256'])
 def test_vesting_never_settles(self):
  p=validate_vesting(1000,100,100,200,150); self.assertEqual(p['claimable_atomic'],400); self.assertFalse(p['settle'])
 def test_burn_is_plan_only(self):
  p=burn_gap(10_000_000_000,8_000_000_000); self.assertEqual(p['planned_gap_atomic'],2_000_000_000); self.assertFalse(p['execute']); self.assertTrue(p['requires_governance_and_multisig'])
if __name__=='__main__': unittest.main()
