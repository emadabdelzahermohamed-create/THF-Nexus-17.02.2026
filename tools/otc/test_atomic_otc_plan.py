import unittest
from atomic_otc_plan import Quote,TokenAccountSnapshot,build,THF_MINT,SYSTEM_PROGRAM
BASE=dict(seller_owner='SELLER',seller_token_account='SELLER_ATA',buyer_owner='BUYER',buyer_token_account='BUYER_ATA',buyer_fee_payer='BUYER')
def snap(**kw):
 d=dict(address='SELLER_ATA',mint=THF_MINT,owner='SELLER',amount_raw=10**18,state='initialized',delegate=None); d.update(kw); return TokenAccountSnapshot(**d)
class T(unittest.TestCase):
 def test_atomic_intent(self):
  p=build(Quote(**BASE,thf_tokens=1_000_000,payment_lamports=50_000_000),snap())
  self.assertEqual(p['sellerSOLOutflowLamports'],0); self.assertEqual(p['requiredSigners'],['SELLER','BUYER'])
  self.assertEqual(p['instructions'][1]['amountRaw'],'100000000000000'); self.assertEqual(p['instructions'][1]['mint'],THF_MINT)
  self.assertEqual(p['instructions'][2]['program'],SYSTEM_PROGRAM)
 def test_requires_snapshot(self):
  with self.assertRaises(ValueError): build(Quote(**BASE,thf_tokens=1,payment_lamports=1))
 def test_rejects_wrong_mint(self):
  with self.assertRaises(ValueError): build(Quote(**BASE,thf_tokens=1,payment_lamports=1),snap(mint='OTHER'))
 def test_rejects_wrong_owner(self):
  with self.assertRaises(ValueError): build(Quote(**BASE,thf_tokens=1,payment_lamports=1),snap(owner='OTHER'))
 def test_rejects_delegate(self):
  with self.assertRaises(ValueError): build(Quote(**BASE,thf_tokens=1,payment_lamports=1),snap(delegate='DELEGATE'))
 def test_rejects_insufficient_balance(self):
  with self.assertRaises(ValueError): build(Quote(**BASE,thf_tokens=2,payment_lamports=1),snap(amount_raw=1))
 def test_cap(self):
  with self.assertRaises(ValueError): build(Quote(**BASE,thf_tokens=25_000_001,payment_lamports=1),snap())
 def test_positive_payment(self):
  with self.assertRaises(ValueError): build(Quote(**BASE,thf_tokens=1,payment_lamports=0),snap())
 def test_buyer_fee_payer(self):
  x=BASE|{'buyer_fee_payer':'SELLER'}
  with self.assertRaises(ValueError): build(Quote(**x,thf_tokens=1,payment_lamports=1),snap())
if __name__=='__main__': unittest.main()
