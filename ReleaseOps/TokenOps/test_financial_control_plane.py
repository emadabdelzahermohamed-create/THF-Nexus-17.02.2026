import unittest
from financial_control_plane import *

POLICY={"distribution_controls":{"per_user_cap_raw":None,"epoch_budget_cap_raw":None,"distribution_reserve_account":None,"delivery_model":None,"revenue_value_basis_status":"not_approved"}}
TREASURY={"approval_classes":{"reward_epoch":{"minimum_approvals":2,"execution":"external_multisig"},"vesting_settlement":{"minimum_approvals":2,"execution":"external_multisig"},"burn":{"minimum_approvals":3,"execution":"external_multisig"},"treasury_transfer":{"minimum_approvals":3,"execution":"external_multisig"}}}
EMPTY={"network":NETWORK,"mint":MINT,"accounts":[]}
OWNER="11111111111111111111111111111111"
TOKEN_ACCOUNT="SysvarRent111111111111111111111111111111111"

def account(role="burn_reserve",balance=10,slot=100):
    return {"token_account":TOKEN_ACCOUNT,"owner":OWNER,"role":role,"mint":MINT,"token_program":TOKEN_PROGRAM,"decimals":DECIMALS,"state":"initialized","observed_balance_raw":balance,"observed_slot":slot,"ownership_evidence_sha256":"a"*64,"balance_evidence_sha256":"b"*64}

class T(unittest.TestCase):
    def test_pubkey(self): self.assertTrue(valid_pubkey(MINT)); self.assertFalse(valid_pubkey("abc"))
    def test_identity_pass(self): self.assertEqual(validate_identity({"network":NETWORK,"mint":MINT,"token_program":TOKEN_PROGRAM,"decimals":8})["status"],"PASS")
    def test_identity_program_drift(self): self.assertEqual(validate_identity({"network":NETWORK,"mint":MINT,"token_program":"x","decimals":8})["status"],"FAIL_CLOSED")
    def test_empty_registry_fails(self): self.assertEqual(validate_treasury_registry(EMPTY,100)["status"],"FAIL_CLOSED")
    def test_registry_pass(self): self.assertEqual(validate_treasury_registry({"network":NETWORK,"mint":MINT,"accounts":[account()]},100)["status"],"PASS")
    def test_registry_mint_mismatch(self):
        a=account(); a["mint"]=OWNER
        self.assertIn("accounts[0]:mint_mismatch",validate_treasury_registry({"network":NETWORK,"mint":MINT,"accounts":[a]},100)["errors"])
    def test_registry_program_mismatch(self):
        a=account(); a["token_program"]="wrong"
        self.assertIn("accounts[0]:token_program_mismatch",validate_treasury_registry({"network":NETWORK,"mint":MINT,"accounts":[a]},100)["errors"])
    def test_registry_decimals_mismatch(self):
        a=account(); a["decimals"]=9
        self.assertIn("accounts[0]:decimals_mismatch",validate_treasury_registry({"network":NETWORK,"mint":MINT,"accounts":[a]},100)["errors"])
    def test_registry_stale(self): self.assertEqual(validate_treasury_registry({"network":NETWORK,"mint":MINT,"accounts":[account(slot=1)]},10000,max_slot_lag=10)["status"],"FAIL_CLOSED")
    def test_sensitive_rejected(self):
        with self.assertRaises(ValueError): validate_treasury_registry({"network":NETWORK,"mint":MINT,"accounts":[],"private_key":"x"})
    def test_distribution_fail_closed(self):
        r=distribution_preview(POLICY,validate_treasury_registry(EMPTY),10000,[{"subject_ref":"u1","activity_units":1}]); self.assertEqual(r["status"],"FAIL_CLOSED"); self.assertFalse(r["broadcast"]); self.assertIn("revenue_value_basis_not_approved",r["blockers"])
    def test_value_basis_thf_raw(self):
        r=distribution_value_basis(10000,"THF_RAW"); self.assertEqual(r["proposed_thf_budget_raw"],3500); self.assertEqual(r["status"],"REVIEW_READY_NOT_EXECUTION_READY")
    def test_value_basis_external_fails_without_evidence(self): self.assertEqual(distribution_value_basis(10000,"USD_MINOR")["status"],"FAIL_CLOSED")
    def test_value_basis_external_review_only(self):
        r=distribution_value_basis(10000,"USD_MINOR",123,"c"*64); self.assertEqual(r["status"],"REVIEW_READY_NOT_EXECUTION_READY"); self.assertFalse(r["execution_authorized"])
    def test_vesting_cliff(self): self.assertEqual(vesting_preview({"start_ts":0,"cliff_ts":10,"end_ts":100,"reward_bps":500},5,1000)["vested_raw"],0)
    def test_vesting_linear(self):
        r=vesting_preview({"start_ts":0,"cliff_ts":10,"end_ts":100,"reward_bps":500},50,1000); self.assertEqual(r["vested_raw"],500); self.assertEqual(r["lock_reward_preview_raw"],25)
    def test_burn_headroom_unverified(self):
        r=burn_preview({"supply_raw":str(10_000_000_000*10**8)},validate_treasury_registry(EMPTY)); self.assertEqual(r["theoretical_headroom_raw"],str(2_000_000_000*10**8)); self.assertIsNone(r["review_cap_raw"])
    def test_burn_cap_from_verified_reserve(self):
        tv=validate_treasury_registry({"network":NETWORK,"mint":MINT,"accounts":[account(balance=123)]},100)
        r=burn_preview({"supply_raw":str(10_000_000_000*10**8)},tv); self.assertEqual(r["review_cap_raw"],"123"); self.assertFalse(r["execution_authorized"])
    def test_approval_threshold(self):
        r=approval_manifest("burn",TREASURY,["0"*64]); self.assertEqual(r["minimum_approvals"],3); self.assertFalse(r["execution_authorized"]); self.assertEqual(r["token_program"],TOKEN_PROGRAM)
    def test_unsigned_intent_pass(self):
        i={"network":NETWORK,"mint":MINT,"token_program":TOKEN_PROGRAM,"kind":"burn","amount_raw":1,"evidence_sha256":["d"*64],"signed":False,"broadcast":False,"execution_authorized":False}
        r=validate_unsigned_intent(i,TREASURY); self.assertEqual(r["status"],"PASS_NON_BROADCAST"); self.assertEqual(r["minimum_approvals"],3)
    def test_unsigned_intent_secret_rejected(self):
        i={"network":NETWORK,"mint":MINT,"token_program":TOKEN_PROGRAM,"kind":"burn","amount_raw":1,"evidence_sha256":["d"*64],"signed":False,"broadcast":False,"execution_authorized":False,"private_key":"no"}
        with self.assertRaises(ValueError): validate_unsigned_intent(i,TREASURY)
    def test_incident_quarantine_authority(self):
        a={"network":NETWORK,"mint":MINT,"token_program":TOKEN_PROGRAM,"decimals":8,"mint_authority":"x","freeze_authority":None,"supply_raw":str(10_000_000_000*10**8)}; self.assertEqual(incident_assessment(a)["status"],"QUARANTINE")
    def test_incident_quarantine_program(self):
        a={"network":NETWORK,"mint":MINT,"token_program":"wrong","decimals":8,"mint_authority":None,"freeze_authority":None,"supply_raw":str(10_000_000_000*10**8)}; self.assertEqual(incident_assessment(a)["status"],"QUARANTINE")
    def test_contracts(self):
        o={"services":{s:{"network":NETWORK,"mint":MINT,"token_program":TOKEN_PROGRAM,"contract_version":"1","may_sign":False,"may_broadcast":False,"accepts_private_key_material":False} for s in ("Vault","Forge","Core")}}; self.assertEqual(validate_integration_contracts(o)["status"],"PASS")
    def test_contract_program_drift(self):
        o={"services":{s:{"network":NETWORK,"mint":MINT,"token_program":TOKEN_PROGRAM,"contract_version":"1","may_sign":False,"may_broadcast":False,"accepts_private_key_material":False} for s in ("Vault","Forge","Core")}}; o["services"]["Vault"]["token_program"]="wrong"; self.assertEqual(validate_integration_contracts(o)["status"],"FAIL_CLOSED")
    def test_no_tx_bytes(self): self.assertNotIn("transaction_bytes",approval_manifest("reward_epoch",TREASURY,["f"*64]))

if __name__=="__main__": unittest.main()