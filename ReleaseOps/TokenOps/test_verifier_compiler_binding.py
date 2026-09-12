#!/usr/bin/env python3
import copy, hashlib, json, unittest
from verifier_compiler_binding import build

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

def digest(core):
    return hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def verified(account, owner, treasury=False):
    core = {
        "version":1,"network":"solana-mainnet-beta","token_account":account,"mint":MINT,
        "owner_wallet":owner,"owner_program":PROGRAM,"decimals":8,"amount_raw":"100000000",
        "state":"initialized","onchain_verified":True,"treasury_controlled":treasury,
        "control_evidence_sha256":"a"*64 if treasury else None,
        "verification_policy":"explicit_owner_allowlist_plus_external_evidence",
        "balance_or_rank_used_as_control_evidence":False,
        "transaction_created":False,"transaction_signed":False,"transaction_submitted":False,"financial_effect":False,
    }
    core["verification_sha256"] = digest(core)
    return core

class GateTests(unittest.TestCase):
    def setUp(self):
        self.owner = "11111111111111111111111111111111"
        self.source = verified("So11111111111111111111111111111111111111112", self.owner, True)
        self.dest = verified("SysvarRent111111111111111111111111111111111", "SysvarC1ock11111111111111111111111111111111", False)
        self.req = {"mint":MINT,"operation":"transfer_checked","amount_raw":"42","control_plane_binding_sha256":"b"*64,"source_verification":self.source,"destination_verification":self.dest,"authority_pubkey":self.owner}

    def test_valid_binding(self):
        out = build(self.req)
        self.assertTrue(out["verification_binding_enforced"])
        self.assertTrue(out["ready_for_compilation"])
        self.assertFalse(out["ready_for_signing"])
        self.assertFalse(out["broadcast_allowed"])

    def test_tampered_source_rejected(self):
        req = copy.deepcopy(self.req)
        req["source_verification"]["amount_raw"] = "999999999"
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            build(req)

    def test_non_treasury_source_rejected(self):
        req = copy.deepcopy(self.req)
        src = verified(self.source["token_account"], self.owner, False)
        req["source_verification"] = src
        with self.assertRaisesRegex(ValueError, "not verified treasury"):
            build(req)

    def test_wrong_control_binding_rejected(self):
        req = copy.deepcopy(self.req); req["control_plane_binding_sha256"] = "bad"
        with self.assertRaisesRegex(ValueError, "64-hex"):
            build(req)

    def test_secret_field_rejected_recursively(self):
        req = copy.deepcopy(self.req); req["source_verification"]["private_key"] = "forbidden"
        with self.assertRaisesRegex(ValueError, "secret/signature"):
            build(req)

    def test_burn_needs_no_destination(self):
        req = copy.deepcopy(self.req); req["operation"] = "burn_checked"; req.pop("destination_verification")
        out = build(req)
        self.assertIsNone(out["destination_verification_sha256"])
        self.assertNotIn("destination", out["compiler_request"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
