#!/usr/bin/env python3
import copy
import unittest

from registry_driven_mainnet_verifier import build_registry_driven_verification, verify_request
from treasury_control_registry import MINT, NETWORK, normalize_registry

OWNER = "So11111111111111111111111111111111111111112"
ACCOUNT = "11111111111111111111111111111111"
EVIDENCE = "a" * 64


def snapshot():
    return normalize_registry({
        "network": NETWORK,
        "mint": MINT,
        "entries": [{
            "owner_wallet": OWNER,
            "token_accounts": [ACCOUNT],
            "control_evidence_sha256": EVIDENCE,
            "evidence_type": "multisig_config_snapshot",
            "governance_reference": "public fixture only",
        }],
    })


def account_value(owner=OWNER, mint=MINT, decimals=8, amount="100000000"):
    return {
        "owner": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
        "data": {
            "parsed": {
                "type": "account",
                "info": {
                    "mint": mint,
                    "owner": owner,
                    "state": "initialized",
                    "tokenAmount": {"amount": amount, "decimals": decimals},
                },
            }
        },
    }


class TestRegistryDrivenVerifier(unittest.TestCase):
    def test_registry_derives_control_metadata_and_binds_snapshot(self):
        s = snapshot()
        out = build_registry_driven_verification(s, ACCOUNT, OWNER, account_value())
        self.assertEqual(out["registry_snapshot_sha256"], s["registry_snapshot_sha256"])
        self.assertEqual(out["control_evidence_sha256"], EVIDENCE)
        self.assertEqual(out["candidate_source"], "validated_treasury_control_registry_only")
        self.assertFalse(out["caller_supplied_allowlist"])
        self.assertFalse(out["caller_supplied_control_evidence"])
        self.assertFalse(out["transaction_created"])
        self.assertFalse(out["transaction_signed"])
        self.assertFalse(out["transaction_submitted"])
        self.assertFalse(out["ready_for_simulation"])
        self.assertFalse(out["ready_for_signing"])
        self.assertFalse(out["broadcast_allowed"])
        self.assertFalse(out["financial_effect"])

    def test_unregistered_token_account_is_rejected(self):
        with self.assertRaises(ValueError):
            build_registry_driven_verification(snapshot(), "DifferentAccount111111111111111111111111111", OWNER, account_value())

    def test_onchain_owner_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            build_registry_driven_verification(snapshot(), ACCOUNT, OWNER, account_value(owner="11111111111111111111111111111111"))

    def test_registry_tamper_is_rejected(self):
        s = snapshot()
        s["entries"][0]["governance_reference"] = "tampered"
        with self.assertRaises(ValueError):
            build_registry_driven_verification(s, ACCOUNT, OWNER, account_value())

    def test_caller_cannot_supply_allowlist(self):
        req = {
            "registry_snapshot": snapshot(),
            "token_account": ACCOUNT,
            "owner_wallet": OWNER,
            "treasury_owner_allowlist": [OWNER],
        }
        with self.assertRaises(ValueError):
            verify_request(req, account_value())

    def test_caller_cannot_supply_control_evidence(self):
        req = {
            "registry_snapshot": snapshot(),
            "token_account": ACCOUNT,
            "owner_wallet": OWNER,
            "control_evidence_sha256": EVIDENCE,
        }
        with self.assertRaises(ValueError):
            verify_request(req, account_value())

    def test_secret_fields_are_rejected(self):
        req = {
            "registry_snapshot": snapshot(),
            "token_account": ACCOUNT,
            "owner_wallet": OWNER,
            "metadata": {"private_key": "forbidden"},
        }
        with self.assertRaises(ValueError):
            verify_request(req, account_value())

    def test_wrong_mint_is_rejected(self):
        req = {
            "registry_snapshot": snapshot(),
            "token_account": ACCOUNT,
            "owner_wallet": OWNER,
            "mint": OWNER,
        }
        with self.assertRaises(ValueError):
            verify_request(req, account_value())

    def test_wrong_token_mint_is_rejected(self):
        with self.assertRaises(ValueError):
            build_registry_driven_verification(snapshot(), ACCOUNT, OWNER, account_value(mint=OWNER))

    def test_digest_changes_when_verified_balance_changes(self):
        s = snapshot()
        one = build_registry_driven_verification(s, ACCOUNT, OWNER, account_value(amount="1"))
        two = build_registry_driven_verification(s, ACCOUNT, OWNER, account_value(amount="2"))
        self.assertNotEqual(one["registry_driven_verification_sha256"], two["registry_driven_verification_sha256"])


if __name__ == "__main__":
    unittest.main()
