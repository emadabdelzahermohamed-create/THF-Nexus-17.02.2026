import unittest
from vesting_plan import build as vesting_build
from tx_manifest import build as tx_build

MINT='HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv'
POLICY={'network':'solana-mainnet-beta','mint':MINT,'approval_classes':{
'reward_epoch':{'minimum_approvals':2,'execution':'external_multisig'},
'vesting_settlement':{'minimum_approvals':2,'execution':'external_multisig'},
'burn':{'minimum_approvals':3,'execution':'external_multisig'},
'treasury_transfer':{'minimum_approvals':3,'execution':'external_multisig'}}}

class Gates(unittest.TestCase):
  def test_vesting_before_cliff(self):
    o=vesting_build({'mint':MINT,'as_of_unix':50,'grants':[{'beneficiary':'walletA','start_unix':0,'cliff_unix':100,'end_unix':200,'amount_ui':'100'}]})
    self.assertEqual(o['total_claimable_raw'],0); self.assertFalse('signature' in o)
  def test_vesting_linear(self):
    o=vesting_build({'mint':MINT,'as_of_unix':150,'grants':[{'beneficiary':'walletA','start_unix':0,'cliff_unix':100,'end_unix':200,'amount_ui':'100','released_ui':'10'}]})
    self.assertEqual(o['total_claimable_raw'],6500000000)
  def test_reward_approval_gate(self):
    r={'operation':'reward_epoch','mint':MINT,'payload':{},'approvals':[{'approver_id':'a','approved':True}]}
    self.assertFalse(tx_build(r,POLICY)['approval_gate_pass'])
    r['approvals'].append({'approver_id':'b','approved':True})
    self.assertTrue(tx_build(r,POLICY)['approval_gate_pass'])
  def test_no_secret_or_signature_fields(self):
    with self.assertRaises(ValueError): tx_build({'operation':'reward_epoch','mint':MINT,'seed_phrase':'x','approvals':[]},POLICY)
  def test_burn_floor_and_control(self):
    base={'operation':'burn','mint':MINT,'amount_raw':200000000000000000,'current_supply_raw':1000000000000000000,'supply_floor_raw':800000000000000000,'source_control':'treasury_verified','payload':{},'approvals':[]}
    self.assertFalse(tx_build(base,POLICY)['approval_gate_pass'])
    bad=dict(base); bad['amount_raw']=200000000000000001
    with self.assertRaises(ValueError): tx_build(bad,POLICY)
    bad2=dict(base); bad2['source_control']='unknown'
    with self.assertRaises(ValueError): tx_build(bad2,POLICY)

if __name__=='__main__': unittest.main()
