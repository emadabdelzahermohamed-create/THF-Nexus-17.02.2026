#!/usr/bin/env python3
import copy
import hashlib
import json
import unittest

from registry_bound_end_to_end_gate import build
from treasury_control_registry import normalize_registry

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"


def digest(core):
    return hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def verified(account, owner, treasury=False, evidence=None):
    core = {
        "version": 1,
        "network": "solana-mainnet-beta",
        "token_account": account,
        "mint": MINT,
        "owner_wallet": owner,
        "owner_program": PROGRAM,
        "decimals": 8,
        "amount_raw": "100000000",
        "state": "initialized",
        "onchain_verified": True,
        "treasury_controlled": treasury,
        "control_evidence_sha256": evidence if treasury else None,
        "verification_policy": "explicit_owner_allowlist_plus_external_evidence",
        "balance_or_rank_used_as_control_evidence": False,
        "transaction_created": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "financial_effect": False,
    }
    core["verification_sha256"] = digest(core)
    return core


class RegistryBoundChainTests(unittest.TestCase):
    def setUp(self):
        self.owner = "11111111111111111111111111111111"
        self.source_account = "So11111111111111111111111111111111111111112"
        self.dest_account = "SysvarRent111111111111111111111111111111111"
        self.dest_owner = "SysvarC1ock11111111111111111111111111111111"
        self.evidence = "a" * 64
        self.registry = normalize_registry({
            "network": "solana-mainnet-beta",
            "mint": MINT,
            "entries": [{
                "owner_wallet": self.owner,
                "token_accounts": [self.source_account],
                "control_evidence_sha256": self.evidence,
                "evidence_type": "multisig_config_snapshot",
                "governance_reference": "THF-TEST-PUBLIC-CONTROL-REF",
            }],
        })
        self.source = verified(
            self.source_account, self.owner, True, self.evidence
        )
        self.dest = verified(self.dest_account, self.dest_owner, False, None)
        self.req = {
            "mint": MINT,
            "operation": "transfer_checked",
            "amount_raw": "42",
            "control_plane_binding_sha256": "b" * 64,
            "source_verification": self.source,
            "destination_verification": self.dest,
            "authority_pubkey": self.owner,
            "treasury_registry_snapshot": self.registry,
        }

    def test_registered_source_is_bound_without_execution(self):
        out = build(self.req)
        chain = out["registry_bound_chain"]
        self.assertEqual(
            chain["registry_snapshot_sha256"],
            self.registry["registry_snapshot_sha256"],
        )
        self.assertEqual(chain["control_evidence_sha256"], self.evidence)
        self.assertEqual(
            chain["source_verification_sha256"],
            self.source["verification_sha256"],
        )
        self.assertTrue(chain["registry_membership_enforced"])
        self.assertTrue(chain["registry_evidence_continuity_enforced"])
        self.assertFalse(chain["ready_for_transaction_serialization"])
        self.assertFalse(chain["ready_for_simulation"])
        self.assertFalse(chain["ready_for_signing"])
        self.assertFalse(chain["broadcast_allowed"])
        self.assertFalse(chain["financial_effect"])
        self.assertEqual(len(chain["registry_bound_chain_sha256"]), 64)

    def test_unregistered_source_account_is_rejected(self):
        req = copy.deepcopy(self.req)
        req["treasury_registry_snapshot"] = normalize_registry({
            "network": "solana-mainnet-beta",
            "mint": MINT,
            "entries": [{
                "owner_wallet": self.owner,
                "token_accounts": ["SysvarRecentB1ockHashes11111111111111111111"],
                "control_evidence_sha256": self.evidence,
                "evidence_type": "multisig_config_snapshot",
                "governance_reference": "THF-TEST-PUBLIC-CONTROL-REF",
            }],
        })
        with self.assertRaisesRegex(ValueError, "not explicitly registered"):
            build(req)

    def test_registry_tampering_is_rejected(self):
        req = copy.deepcopy(self.req)
        req["treasury_registry_snapshot"]["entries"][0]["governance_reference"] = "tampered"
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            build(req)

    def test_registry_evidence_mismatch_is_rejected(self):
        req = copy.deepcopy(self.req)
        req["source_verification"] = verified(
            self.source_account, self.owner, True, "c" * 64
        )
        with self.assertRaisesRegex(ValueError, "control evidence mismatch"):
            build(req)

    def test_owner_allowlist_without_exact_account_membership_is_insufficient(self):
        req = copy.deepcopy(self.req)
        req["treasury_registry_snapshot"] = normalize_registry({
            "network": "solana-mainnet-beta",
            "mint": MINT,
            "entries": [{
                "owner_wallet": self.owner,
                "token_accounts": [],
                "control_evidence_sha256": self.evidence,
                "evidence_type": "multisig_config_snapshot",
                "governance_reference": "THF-TEST-PUBLIC-CONTROL-REF",
            }],
        })
        with self.assertRaisesRegex(ValueError, "not explicitly registered"):
            build(req)

    def test_secret_field_is_rejected_recursively(self):
        req = copy.deepcopy(self.req)
        req["treasury_registry_snapshot"]["private_key"] = "forbidden"
        with self.assertRaisesRegex(ValueError, "secret/signature"):
            build(req)

    def test_non_treasury_source_is_rejected(self):
        req = copy.deepcopy(self.req)
        req["source_verification"] = verified(
            self.source_account, self.owner, False, None
        )
        with self.assertRaisesRegex(ValueError, "not verified treasury"):
            build(req)

    def test_burn_path_is_bound_and_nonexecuting(self):
        req = copy.deepcopy(self.req)
        req["operation"] = "burn_checked"
        req.pop("destination_verification")
        out = build(req)
        chain = out["registry_bound_chain"]
        self.assertEqual(chain["operation"], "burn_checked")
        self.assertEqual(
            chain["registry_snapshot_sha256"],
            self.registry["registry_snapshot_sha256"],
        )
        self.assertFalse(chain["ready_for_simulation"])
        self.assertFalse(chain["ready_for_signing"])
        self.assertFalse(chain["broadcast_allowed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
