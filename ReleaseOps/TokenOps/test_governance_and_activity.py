import copy,unittest
from governance_parameter_proposal import build
from policy_transition_guard import validate
M='HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv'
BASE={'network':'solana-mainnet-beta','mint':M,'economics':{'active_user_revenue_share':0.35,'approved_supply_floor_target_ui':'8000000000'},'distribution_controls':{'per_user_cap':None,'epoch_budget_cap':None,'distribution_reserve_account':None,'claim_or_push_model':'to_be_selected_after_treasury_design'}}
class T(unittest.TestCase):
 def test_incomplete_proposal_fails_closed(self):
  p=build('per_user_cap',None); self.assertFalse(p['proposal_complete']); self.assertFalse(p['execution_authorized'])
 def test_sensitive_material_rejected(self):
  with self.assertRaises(ValueError): build('per_user_cap',{'private_key':'x'},'a','b',1)
 def test_complete_proposal_still_nonexecuting(self):
  p=build('per_user_cap','1000','a'*64,'b'*64,7); self.assertTrue(p['proposal_complete']); self.assertFalse(p['policy_mutation_authorized'])
 def test_transition_without_proposal_blocks(self):
  n=copy.deepcopy(BASE); n['distribution_controls']['per_user_cap']='1000'; r=validate(BASE,n,[]); self.assertFalse(r['transition_review_pass'])
 def test_transition_with_exact_proposal_passes_review_only(self):
  n=copy.deepcopy(BASE); n['distribution_controls']['per_user_cap']='1000'; p=build('per_user_cap','1000','a'*64,'b'*64,7); r=validate(BASE,n,[p]); self.assertTrue(r['transition_review_pass']); self.assertFalse(r['execution_authorized'])
 def test_share_drift_blocks(self):
  n=copy.deepcopy(BASE); n['economics']['active_user_revenue_share']=0.34; self.assertFalse(validate(BASE,n,[])['transition_review_pass'])
 def test_floor_drift_blocks(self):
  n=copy.deepcopy(BASE); n['economics']['approved_supply_floor_target_ui']='7000000000'; self.assertFalse(validate(BASE,n,[])['transition_review_pass'])
if __name__=='__main__': unittest.main()
