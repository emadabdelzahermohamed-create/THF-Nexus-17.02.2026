import copy, json, unittest
from execution_precondition_graph import compile_precondition_graph
from credential_posture import validate_credential_posture
from blocker_action_map import compile_blocker_actions

MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
with open("policy.json",encoding="utf-8") as f: POLICY=json.load(f)
with open("treasury_policy.json",encoding="utf-8") as f: TREASURY=json.load(f)
AUDIT={
 "network":"solana-mainnet-beta","mint":MINT,
 "program_id":"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA","decimals":8,
 "supply_raw":"1000000000000000000","supply_ui":"10000000000",
 "mint_authority":None,"freeze_authority":None,"rpc_slot":446820516,
 "largest_accounts_status":"unavailable","recent_signature_count":5,
}
HASH="a"*64
def ev(names):
    return {n:{"status":"verified","sha256":HASH} for n in names}

class TestPreconditionGraph(unittest.TestCase):
 def test_current_policy_is_fail_closed(self):
    r=compile_precondition_graph(POLICY,TREASURY,AUDIT,{})
    self.assertEqual(r["exact_remaining_signer_action"],"none_until_fail_closed_blockers_are_resolved")
    self.assertIn("per_user_cap_not_approved",r["intents"]["reward_epoch"]["blockers"])
    self.assertIn("epoch_budget_cap_not_approved",r["intents"]["reward_epoch"]["blockers"])
    self.assertIn("reward_delivery_model_not_approved",r["intents"]["reward_epoch"]["blockers"])
    self.assertIn("production_signer_policy_not_approved",r["intents"]["burn"]["blockers"])
    self.assertFalse(r["safety"]["financial_effect"])

 def test_approval_thresholds_derive_from_authoritative_treasury_policy(self):
    r=compile_precondition_graph(POLICY,TREASURY,AUDIT,{})
    self.assertEqual(r["intents"]["reward_epoch"]["minimum_external_multisig_approvals"],2)
    self.assertEqual(r["intents"]["vesting_settlement"]["minimum_external_multisig_approvals"],2)
    self.assertEqual(r["intents"]["burn"]["minimum_external_multisig_approvals"],3)
    self.assertEqual(r["intents"]["treasury_transfer"]["minimum_external_multisig_approvals"],3)

 def test_theoretical_burn_headroom_is_2b_not_authorization(self):
    r=compile_precondition_graph(POLICY,TREASURY,AUDIT,{})
    self.assertEqual(r["approved_economics"]["theoretical_burn_headroom_raw"],2_000_000_000*10**8)
    self.assertFalse(r["intents"]["burn"]["execution_authorized"])

 def test_supply_floor_drift_quarantines_every_intent(self):
    a=copy.deepcopy(AUDIT); a["supply_raw"]=str(7_999_999_999*10**8)
    r=compile_precondition_graph(POLICY,TREASURY,a,{})
    for x in r["intents"].values(): self.assertIn("supply_below_approved_8b_floor",x["blockers"])

 def test_authority_reappearance_quarantines_every_intent(self):
    a=copy.deepcopy(AUDIT);a["mint_authority"]="Unexpected"
    r=compile_precondition_graph(POLICY,TREASURY,a,{})
    for x in r["intents"].values(): self.assertIn("mint_authority_reappeared",x["blockers"])

 def test_burn_verified_reserve_cannot_exceed_8b_floor_headroom(self):
    names=["mainnet_audit","policy_snapshot","treasury_policy_snapshot","simulation_receipt","treasury_ownership","treasury_balance","burn_reserve","governance_authority"]
    e=ev(names);e["burn_reserve"]["amount_raw"]=2_000_000_001*10**8
    r=compile_precondition_graph(POLICY,TREASURY,AUDIT,e)
    self.assertIn("burn_reserve_exceeds_8b_floor_headroom",r["intents"]["burn"]["blockers"])

 def test_third_party_burn_hard_guard_is_mandatory(self):
    t=copy.deepcopy(TREASURY);t["hard_guards"]["third_party_balance_burn_forbidden"]=False
    r=compile_precondition_graph(POLICY,t,AUDIT,{})
    self.assertIn("hard_guard_not_asserted:third_party_balance_burn_forbidden",r["global_blockers"])

 def test_missing_evidence_is_explicit_per_intent(self):
    r=compile_precondition_graph(POLICY,TREASURY,AUDIT,{})
    self.assertIn("missing_verified_evidence:activity_eligibility",r["intents"]["reward_epoch"]["blockers"])
    self.assertIn("missing_verified_evidence:vesting_terms",r["intents"]["vesting_settlement"]["blockers"])
    self.assertIn("missing_verified_evidence:treasury_ownership",r["intents"]["burn"]["blockers"])
    self.assertIn("missing_verified_evidence:destination_review",r["intents"]["treasury_transfer"]["blockers"])

 def test_invalid_evidence_hash_does_not_count(self):
    e={"mainnet_audit":{"status":"verified","sha256":"bad"}}
    r=compile_precondition_graph(POLICY,TREASURY,AUDIT,e)
    self.assertIn("missing_verified_evidence:mainnet_audit",r["intents"]["burn"]["blockers"])

 def test_forbidden_secret_fields_rejected(self):
    e={"mainnet_audit":{"status":"verified","sha256":HASH},"private_key":"never"}
    with self.assertRaises(ValueError): compile_precondition_graph(POLICY,TREASURY,AUDIT,e)

 def test_signature_fields_rejected(self):
    with self.assertRaises(ValueError): compile_precondition_graph(POLICY,TREASURY,AUDIT,{"signature":"x"})

 def test_well_formed_review_evidence_still_never_authorizes_execution(self):
    p=copy.deepcopy(POLICY)
    p["signer_policy"]["production_policy_status"]="approved"
    p["distribution_controls"]["per_user_cap"]="100000000"
    p["distribution_controls"]["epoch_budget_cap"]="1000000000"
    p["distribution_controls"]["claim_or_push_model"]="claim"
    required=set()
    for n in ("reward_epoch","vesting_settlement","burn","treasury_transfer"):
       required.update(compile_precondition_graph(p,TREASURY,AUDIT,{})["intents"][n]["required_evidence"])
    e=ev(required);e["burn_reserve"]["amount_raw"]=100*10**8
    r=compile_precondition_graph(p,TREASURY,AUDIT,e)
    for x in r["intents"].values():
       self.assertTrue(x["unsigned_review_ready"])
       self.assertFalse(x["external_signer_handoff_ready"])
       self.assertFalse(x["execution_authorized"])
       self.assertFalse(x["broadcast_allowed"])

 def test_external_multisig_control_model_required(self):
    t=copy.deepcopy(TREASURY);t["control_model"]="single_key"
    with self.assertRaises(ValueError): compile_precondition_graph(POLICY,t,AUDIT,{})

class TestCredentialPosture(unittest.TestCase):
 def test_wif_short_lived_external_signer_posture_passes(self):
    d={"automation_auth_mode":"github_oidc_wif","credential_ttl_seconds":1800,"persistent_service_account_key":False,"financial_signer_location":"external_multisig"}
    r=validate_credential_posture(d)
    self.assertTrue(r["posture_ready"]);self.assertFalse(r["financial_signing_enabled"])

 def test_static_auth_fails_closed(self):
    d={"automation_auth_mode":"service_account_json","credential_ttl_seconds":86400,"persistent_service_account_key":True,"financial_signer_location":"ci"}
    r=validate_credential_posture(d)
    self.assertFalse(r["posture_ready"]);self.assertEqual(len(r["blockers"]),4)

 def test_credentials_themselves_are_rejected(self):
    d={"automation_auth_mode":"wif_oidc","credential_ttl_seconds":900,"persistent_service_account_key":False,"financial_signer_location":"external_multisig","access_token":"never"}
    with self.assertRaises(ValueError): validate_credential_posture(d)

 def test_ttl_over_one_hour_rejected(self):
    d={"automation_auth_mode":"gcp_workload_identity_federation","credential_ttl_seconds":3601,"persistent_service_account_key":False,"financial_signer_location":"user_controlled_external_signer"}
    r=validate_credential_posture(d)
    self.assertIn("credential_ttl_not_bounded_to_1h",r["blockers"])

class TestBlockerActionMap(unittest.TestCase):
 def test_current_blockers_get_safe_exact_actions(self):
    g=compile_precondition_graph(POLICY,TREASURY,AUDIT,{})
    r=compile_blocker_actions(g);by={x["blocker"]:x for x in r["actions"]}
    self.assertEqual(by["per_user_cap_not_approved"]["owner"],"governance")
    self.assertIn("do not provide keys to CI",by["production_signer_policy_not_approved"]["action"])
    self.assertFalse(r["financial_effect"])
    self.assertEqual(r["signer_action_now"],"none_until_fail_closed_blockers_are_resolved")

 def test_drift_maps_to_incident_quarantine(self):
    a=copy.deepcopy(AUDIT);a["freeze_authority"]="Unexpected"
    r=compile_blocker_actions(compile_precondition_graph(POLICY,TREASURY,a,{}))
    x=next(x for x in r["actions"] if x["blocker"]=="freeze_authority_reappeared")
    self.assertEqual(x["owner"],"incident_response");self.assertIn("quarantine",x["action"])

 def test_unknown_evidence_gets_nonfinancial_generic_action(self):
    g=compile_precondition_graph(POLICY,TREASURY,AUDIT,{})
    g=copy.deepcopy(g);g["global_blockers"].append("missing_verified_evidence:new_receipt")
    r=compile_blocker_actions(g)
    x=next(x for x in r["actions"] if x["blocker"]=="missing_verified_evidence:new_receipt")
    self.assertFalse(x["binding_financial_action"])

if __name__=="__main__": unittest.main()
