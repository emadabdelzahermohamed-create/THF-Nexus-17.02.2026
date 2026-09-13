import unittest,copy
from policy_decision_scenario_engine import build as scenarios
from vesting_lock_liability_model import model as vesting
from treasury_solvency_stress import stress
from governance_decision_packet import build as packet
M='HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv'
P={'network':'solana-mainnet-beta','mint':M,'economics':{'active_user_revenue_share':0.35,'approved_supply_floor_target_ui':'8000000000'},'signer_policy':{'production_policy_status':'not_yet_approved'},'distribution_controls':{'per_user_cap':None,'epoch_budget_cap':None,'claim_or_push_model':'to_be_selected_after_treasury_design'}}
T={'network':'solana-mainnet-beta','mint':M,'approval_classes':{'reward_epoch':{'minimum_approvals':2},'vesting_settlement':{'minimum_approvals':2},'burn':{'minimum_approvals':3},'treasury_transfer':{'minimum_approvals':3}}}
R={'schema':'thf-tokenops-public-treasury-registry/v1','network':'solana-mainnet-beta','mint':M,'status':'not_authoritatively_configured','accounts':[]}
A={'network':'solana-mainnet-beta','mint':M,'supply_raw':'1000000000000000000'}
class X(unittest.TestCase):
 def test_scenario_nonbinding(self):
  r=scenarios(P,[{'name':'A','epoch_budget_cap_raw':1000,'per_user_cap_raw':100,'claim_or_push_model':'claim'}]);self.assertFalse(r['policy_mutated']);self.assertEqual(r['scenarios'][0]['minimum_recipients_to_fully_allocate_at_cap'],10)
 def test_scenario_bad_model(self):
  with self.assertRaises(ValueError): scenarios(P,[{'name':'A','epoch_budget_cap_raw':1000,'per_user_cap_raw':100,'claim_or_push_model':'x'}])
 def test_scenario_secret_rejected(self):
  p=copy.deepcopy(P);p['private_key']='x'
  with self.assertRaises(ValueError): scenarios(p,[])
 def test_vesting_math_and_no_settlement(self):
  r=vesting(P,{'lock_reward_apr_bps':1000,'max_lock_reward_budget_raw':100},[{'position_id':'p1','principal_raw':1000,'start_unix':0,'cliff_unix':0,'end_unix':365*86400}],365*86400)
  self.assertEqual(r['liability']['capped_lock_reward_raw'],'100');self.assertFalse(r['settlement_authorized'])
 def test_vesting_cliff(self):
  r=vesting(P,{'lock_reward_apr_bps':0,'max_lock_reward_budget_raw':0},[{'position_id':'p1','principal_raw':1000,'start_unix':10,'cliff_unix':20,'end_unix':30}],15);self.assertEqual(r['positions'][0]['unlocked_raw'],'0')
 def test_stress_current_registry_blocks(self):
  r=stress(P,R,A,{'reward_raw':1});self.assertIsNone(r['review_burn_cap_raw']);self.assertIn('authoritative_treasury_inventory_ownership_balance_evidence_incomplete',r['blockers'])
 def test_stress_verified_never_exceeds_8b_headroom(self):
  rr={'network':'solana-mainnet-beta','mint':M,'status':'authoritatively_configured','accounts':[{'balance_verified':True,'ownership_evidence_sha256':'a'*64,'observed_balance_raw':3000000000*10**8}]}
  r=stress(P,rr,A,{'reward_raw':100000000*10**8,'vesting_raw':100000000*10**8,'operating_reserve_raw':100000000*10**8});self.assertEqual(int(r['review_burn_cap_raw']),2000000000*10**8);self.assertFalse(r['burn_authorized'])
 def test_packet_does_not_invent_threshold(self):
  s=scenarios(P,[]);r=packet(P,T,s);self.assertEqual(r['policy_governance_threshold_status'],'not_authoritatively_defined_in_current_treasury_policy');self.assertFalse(r['approval_satisfied'])
 def test_constitutional_drift_rejected(self):
  p=copy.deepcopy(P);p['economics']['active_user_revenue_share']=.34
  with self.assertRaises(ValueError): scenarios(p,[])
if __name__=='__main__': unittest.main()
