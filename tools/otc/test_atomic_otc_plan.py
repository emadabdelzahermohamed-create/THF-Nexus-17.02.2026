import unittest
from atomic_otc_plan import Quote,TokenAccountSnapshot,build,canonical_ata,THF_MINT,SYSTEM_PROGRAM
BUYER='GG5jCGt6Kzp9StPepZeJf6BeujyMa4TmMEYNEbF1G4Lp'
BUYER_THA='HokdYvghHusxtWPTKfEEaPm1cmcv4FSsBr35aKDwqN84'
BASE=dict(seller_owner='SELLER',seller_token_account='SELLER_ATA',buyer_owner=BUYER,buyer_token_account=BUYER_THA,buyer_fee_payer=BUYER)
def snap(**kw):
 d=dict(address='SELLER_ATA',mint=THF_MINT,owner='SELLER',amount_raw=10**18,state='initialized',delegate=None); d.update(kw); return TokenAccountSnapshot(**d)
class T(unittest.TestCase):
 def test_known_solana_ata_vector(self):
  self.assertEqual(canonical_ata('GG5jCGt6Kzp9StPepZeJf6BeujyMa4TmMEYNEbF1G4Lp','So11111111111111111111111111111111111111112'),'8yDNe4ctQKtZZTFLuXaL51fVW6S2qaUGvmu7rYCTjLEV')
 def test_thf_canonical_ata(self): self.assertEqual(canonical_ata(BUYER),BUYER_THA)
 def test_rejects_noncanonical_buyer_account(self):
  with self.assertRaises(ValueError): build(Quote(**(BASE|{'buyer_token_account':'11111111111111111111111111111111'}),thf_tokens=1,payment_lamports=1),snap())
 def test_atomic_intent(self):
  p=build(Quote(**BASE,thf_tokens=1_000_000,payment_lamports=50_000_000),snap())
  self.assertEqual(p['sellerSOLOutflowLamports'],0); self.assertEqual(p['requiredSigners'],['SELLER',BUYER])
  self.assertEqual(p['buyerAtaValidation'],'CANONICAL_DERIVATION_VERIFIED')
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
