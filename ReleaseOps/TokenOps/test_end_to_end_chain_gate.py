#!/usr/bin/env python3
import copy
import hashlib
import json
import unittest

from end_to_end_chain_gate import build

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"


def digest(core):
    return hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def verified(account, owner, treasury=False):
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
        "control_evidence_sha256": "a" * 64 if treasury else None,
        "verification_policy": "explicit_owner_allowlist_plus_external_evidence",
        "balance_or_rank_used_as_control_evidence": False,
        "transaction_created": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "financial_effect": False,
    }
    core["verification_sha256"] = digest(core)
    return core


class EndToEndGateTests(unittest.TestCase):
    def setUp(self):
        self.owner = "11111111111111111111111111111111"
        self.source = verified(
            "So11111111111111111111111111111111111111112", self.owner, True
        )
        self.dest = verified(
            "SysvarRent111111111111111111111111111111111",
            "SysvarC1ock11111111111111111111111111111111",
            False,
        )
        self.req = {
            "mint": MINT,
            "operation": "transfer_checked",
            "amount_raw": "42",
            "control_plane_binding_sha256": "b" * 64,
            "source_verification": self.source,
            "destination_verification": self.dest,
            "authority_pubkey": self.owner,
        }

    def test_transfer_chain_is_fully_bound_and_nonexecuting(self):
        out = build(self.req)
        chain = out["chain"]
        envelope = out["instruction_envelope"]
        binding = out["binding"]
        self.assertEqual(
            chain["instruction_envelope_sha256"],
            envelope["instruction_envelope_sha256"],
        )
        self.assertEqual(
            chain["verifier_compiler_binding_sha256"],
            binding["verifier_compiler_binding_sha256"],
        )
        self.assertEqual(
            chain["control_plane_binding_sha256"],
            envelope["control_plane_binding_sha256"],
        )
        self.assertTrue(chain["integrity_chain_enforced"])
        self.assertFalse(chain["ready_for_transaction_serialization"])
        self.assertFalse(chain["ready_for_simulation"])
        self.assertFalse(chain["ready_for_signing"])
        self.assertFalse(chain["broadcast_allowed"])
        self.assertFalse(chain["financial_effect"])

    def test_tampered_verification_is_rejected_before_compilation(self):
        req = copy.deepcopy(self.req)
        req["source_verification"]["amount_raw"] = "43"
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            build(req)

    def test_non_treasury_source_is_rejected(self):
        req = copy.deepcopy(self.req)
        req["source_verification"] = verified(
            self.source["token_account"], self.owner, False
        )
        with self.assertRaisesRegex(ValueError, "not verified treasury"):
            build(req)

    def test_secret_field_is_rejected_recursively(self):
        req = copy.deepcopy(self.req)
        req["destination_verification"]["private_key"] = "forbidden"
        with self.assertRaisesRegex(ValueError, "secret/signature"):
            build(req)

    def test_control_plane_digest_format_is_enforced(self):
        req = copy.deepcopy(self.req)
        req["control_plane_binding_sha256"] = "not-a-digest"
        with self.assertRaisesRegex(ValueError, "64-hex"):
            build(req)

    def test_burn_chain_has_no_destination_and_stays_nonexecuting(self):
        req = copy.deepcopy(self.req)
        req["operation"] = "burn_checked"
        req.pop("destination_verification")
        out = build(req)
        self.assertIsNone(out["chain"]["destination_verification_sha256"])
        self.assertEqual(out["instruction_envelope"]["operation"], "burn_checked")
        self.assertFalse(out["chain"]["ready_for_simulation"])
        self.assertFalse(out["chain"]["ready_for_signing"])
        self.assertFalse(out["chain"]["broadcast_allowed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
