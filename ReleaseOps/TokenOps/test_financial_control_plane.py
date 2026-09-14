import unittest
from financial_control_plane import *

POLICY={"distribution_controls":{"per_user_cap_raw":None,"epoch_budget_cap_raw":None,"distribution_reserve_account":None,"delivery_model":None}}
TREASURY={"approval_classes":{"reward_epoch":{"minimum_approvals":2,"execution":"external_multisig"},"vesting_settlement":{"minimum_approvals":2,"execution":"external_multisig"},"burn":{"minimum_approvals":3,"execution":"external_multisig"},"treasury_transfer":{"minimum_approvals":3,"execution":"external_multisig"}}}
EMPTY={"network":NETWORK,"mint":MINT,"accounts":[]}

class T(unittest.TestCase):
    def test_pubkey(self): self.assertTrue(valid_pubkey(MINT)); self.assertFalse(valid_pubkey("abc"))
    def test_empty_registry_fails(self): self.assertEqual(validate_treasury_registry(EMPTY,100)["status"],"FAIL_CLOSED")
    def test_sensitive_rejected(self):
        with self.assertRaises(ValueError): validate_treasury_registry({"network":NETWORK,"mint":MINT,"accounts":[],"private_key":"x"})
    def test_distribution_fail_closed(self):
        r=distribution_preview(POLICY,validate_treasury_registry(EMPTY),10000,[{"subject_ref":"u1","activity_units":1}]); self.assertEqual(r["status"],"FAIL_CLOSED"); self.assertFalse(r["broadcast"])
    def test_vesting_cliff(self): self.assertEqual(vesting_preview({"start_ts":0,"cliff_ts":10,"end_ts":100,"reward_bps":500},5,1000)["vested_raw"],0)
    def test_vesting_linear(self):
        r=vesting_preview({"start_ts":0,"cliff_ts":10,"end_ts":100,"reward_bps":500},50,1000); self.assertEqual(r["vested_raw"],500); self.assertEqual(r["lock_reward_preview_raw"],25)
    def test_burn_headroom(self):
        r=burn_preview({"supply_raw":str(10_000_000_000*10**8)},validate_treasury_registry(EMPTY)); self.assertEqual(r["theoretical_headroom_raw"],str(2_000_000_000*10**8)); self.assertIsNone(r["review_cap_raw"])
    def test_approval_threshold(self):
        r=approval_manifest("burn",TREASURY,["0"*64]); self.assertEqual(r["minimum_approvals"],3); self.assertFalse(r["execution_authorized"])
    def test_incident_quarantine(self):
        a={"network":NETWORK,"mint":MINT,"decimals":8,"mint_authority":"x","freeze_authority":None,"supply_raw":str(10_000_000_000*10**8)}; self.assertEqual(incident_assessment(a)["status"],"QUARANTINE")
    def test_contracts(self):
        o={"services":{s:{"network":NETWORK,"mint":MINT,"contract_version":"1","may_sign":False,"may_broadcast":False,"accepts_private_key_material":False} for s in ("Vault","Forge","Core")}}; self.assertEqual(validate_integration_contracts(o)["status"],"PASS")
    def test_no_tx_bytes(self): self.assertNotIn("transaction_bytes",approval_manifest("reward_epoch",TREASURY,["f"*64]))

if __name__=="__main__": unittest.main()
