#!/usr/bin/env python3
import unittest
from mainnet_token_account_verifier import verify_account, MINT, TOKEN_PROGRAM

ADDR = "11111111111111111111111111111111"
OWNER = "So11111111111111111111111111111111111111112"
EVIDENCE = "a" * 64


def account_value(owner=OWNER, mint=MINT, program=TOKEN_PROGRAM, decimals=8):
    return {
        "owner": program,
        "data": {"parsed": {"type":"account", "info": {
            "mint": mint,
            "owner": owner,
            "state": "initialized",
            "tokenAmount": {"amount":"123", "decimals": decimals}
        }}}
    }


class TestVerifier(unittest.TestCase):
    def test_non_treasury_is_verified_but_not_controlled(self):
        out = verify_account({"token_account":ADDR,"treasury_owner_allowlist":[]}, account_value())
        self.assertTrue(out["onchain_verified"])
        self.assertFalse(out["treasury_controlled"])
        self.assertFalse(out["balance_or_rank_used_as_control_evidence"])

    def test_treasury_requires_external_evidence(self):
        with self.assertRaises(ValueError):
            verify_account({"token_account":ADDR,"treasury_owner_allowlist":[OWNER]}, account_value())

    def test_treasury_with_evidence_passes(self):
        out = verify_account({"token_account":ADDR,"treasury_owner_allowlist":[OWNER],"control_evidence_sha256":EVIDENCE}, account_value())
        self.assertTrue(out["treasury_controlled"])
        self.assertEqual(out["control_evidence_sha256"], EVIDENCE)

    def test_wrong_mint_rejected(self):
        with self.assertRaises(ValueError):
            verify_account({"token_account":ADDR}, account_value(mint=OWNER))

    def test_wrong_program_rejected(self):
        with self.assertRaises(ValueError):
            verify_account({"token_account":ADDR}, account_value(program=OWNER))

    def test_wrong_decimals_rejected(self):
        with self.assertRaises(ValueError):
            verify_account({"token_account":ADDR}, account_value(decimals=9))

    def test_secret_fields_rejected(self):
        with self.assertRaises(ValueError):
            verify_account({"token_account":ADDR,"private_key":"no"}, account_value())

    def test_unlisted_evidence_rejected(self):
        with self.assertRaises(ValueError):
            verify_account({"token_account":ADDR,"treasury_owner_allowlist":[],"control_evidence_sha256":EVIDENCE}, account_value())

if __name__ == "__main__":
    unittest.main()
