import unittest
from rpc_snapshot import parse_finalized_token_account
from atomic_otc_plan import TOKEN_PROGRAM, THF_MINT
ADDR='Ei9gQahXJW4mynXzdr3xtqJBPEpevfNxGMNEUHnmnLrG'
OWNER='GG5jCGt6Kzp9StPepZeJf6BeujyMa4TmMEYNEbF1G4Lp'

def response(slot=500, program_owner=TOKEN_PROGRAM, amount='850000000000000000', mint=THF_MINT, state='initialized', delegate=None):
 info={'mint':mint,'owner':OWNER,'state':state,'tokenAmount':{'amount':amount,'decimals':8,'uiAmountString':'8500000000'}}
 if delegate is not None: info['delegate']=delegate
 return {'jsonrpc':'2.0','result':{'context':{'slot':slot},'value':{'owner':program_owner,'data':{'program':'spl-token','parsed':{'type':'account','info':info},'space':165}}},'id':1}

class T(unittest.TestCase):
 def test_parses_finalized_shape(self):
  e=parse_finalized_token_account(ADDR,response(),min_context_slot=499)
  self.assertEqual(e.context_slot,500); self.assertEqual(e.snapshot.mint,THF_MINT)
  self.assertEqual(e.snapshot.amount_raw,850000000000000000)
 def test_rejects_stale_slot(self):
  with self.assertRaises(ValueError): parse_finalized_token_account(ADDR,response(slot=498),min_context_slot=499)
 def test_rejects_wrong_program(self):
  with self.assertRaises(ValueError): parse_finalized_token_account(ADDR,response(program_owner='11111111111111111111111111111111'),min_context_slot=499)
 def test_rejects_rpc_error(self):
  with self.assertRaises(ValueError): parse_finalized_token_account(ADDR,{'error':{'code':-1}},min_context_slot=499)
 def test_rejects_missing_account(self):
  r=response(); r['result']['value']=None
  with self.assertRaises(ValueError): parse_finalized_token_account(ADDR,r,min_context_slot=499)
 def test_rejects_bad_amount(self):
  with self.assertRaises(ValueError): parse_finalized_token_account(ADDR,response(amount='x'),min_context_slot=499)
if __name__=='__main__': unittest.main()
