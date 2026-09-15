import unittest
from settlement_risk_gate import assess

class RiskGateTests(unittest.TestCase):
    def test_safe_plan_stays_unsigned(self):
        x=assess(epoch_id='e1',manifest_sha256='m1',allocations=[{'wallet':'a','amount_atomic':100},{'wallet':'b','amount_atomic':100}],pool_atomic=1000,max_recipient_bps=2000)
        self.assertEqual(x['status'],'READY_FOR_SIMULATION'); self.assertFalse(x['sign']); self.assertFalse(x['broadcast']); self.assertFalse(x['financial_execution'])
    def test_whale_is_blocked(self):
        x=assess(epoch_id='e1',manifest_sha256='m1',allocations=[{'wallet':'a','amount_atomic':201}],pool_atomic=1000,max_recipient_bps=2000)
        self.assertIn('ANTI_WHALE_RECIPIENT_CAP_EXCEEDED',x['blockers'])
    def test_duplicate_and_replay_are_blocked(self):
        x=assess(epoch_id='e1',manifest_sha256='m1',allocations=[{'wallet':'a','amount_atomic':1},{'wallet':'a','amount_atomic':1}],pool_atomic=100,max_recipient_bps=1000,previously_settled_manifest_sha256s={'m1'})
        self.assertIn('DUPLICATE_RECIPIENT',x['blockers']); self.assertIn('REPLAYED_SETTLEMENT_MANIFEST',x['blockers'])
    def test_overallocation_is_blocked(self):
        x=assess(epoch_id='e1',manifest_sha256='m1',allocations=[{'wallet':'a','amount_atomic':60},{'wallet':'b','amount_atomic':60}],pool_atomic=100,max_recipient_bps=10000)
        self.assertIn('ALLOCATION_EXCEEDS_POOL',x['blockers'])

if __name__=='__main__': unittest.main()
