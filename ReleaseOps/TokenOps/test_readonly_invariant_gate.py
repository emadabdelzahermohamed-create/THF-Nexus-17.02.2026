import copy, unittest
from readonly_invariant_gate import validate
MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
BASE={"network":"solana-mainnet-beta","mint":MINT,"account_exists":True,
"program_id":"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA","decimals":8,
"supply_raw":str(10_000_000_000*10**8),"mint_authority":None,"freeze_authority":None,
"largest_accounts_status":"unavailable","recent_signatures_status":"ok",
"safety":{"read_only":True,"transaction_created":False,"transaction_signed":False,
"transaction_submitted":False,"private_key_used":False}}
class TestInvariantGate(unittest.TestCase):
 def test_current_shape_passes_critical_checks_but_can_be_degraded(self):
  r=validate(BASE);self.assertFalse(r["critical_failures"]);self.assertEqual(r["status"],"degraded")
 def test_holder_rpc_limit_is_not_critical(self):
  r=validate(BASE);self.assertIn("holder_concentration_optional_query_unavailable",r["degraded_conditions"])
 def test_program_drift_fails(self):
  a=copy.deepcopy(BASE);a["program_id"]="bad";self.assertIn("program",validate(a)["critical_failures"])
 def test_decimals_drift_fails(self):
  a=copy.deepcopy(BASE);a["decimals"]=9;self.assertIn("decimals",validate(a)["critical_failures"])
 def test_authority_reappearance_fails(self):
  a=copy.deepcopy(BASE);a["freeze_authority"]="x";self.assertIn("freeze_authority_absent",validate(a)["critical_failures"])
 def test_supply_above_original_10b_fails(self):
  a=copy.deepcopy(BASE);a["supply_raw"]=str(10_000_000_001*10**8);self.assertIn("supply_not_above_original_10b",validate(a)["critical_failures"])
 def test_supply_below_8b_fails(self):
  a=copy.deepcopy(BASE);a["supply_raw"]=str(7_999_999_999*10**8);self.assertIn("supply_not_below_approved_8b_floor",validate(a)["critical_failures"])
 def test_safety_drift_fails(self):
  a=copy.deepcopy(BASE);a["safety"]["transaction_signed"]=True;self.assertIn("transaction_signed_false",validate(a)["critical_failures"])
if __name__=="__main__":unittest.main()
