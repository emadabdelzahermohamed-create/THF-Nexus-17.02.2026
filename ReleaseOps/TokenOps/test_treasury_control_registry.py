#!/usr/bin/env python3
import copy
import unittest

from treasury_control_registry import MINT, NETWORK, candidate_from_registry, normalize_registry

OWNER = "So11111111111111111111111111111111111111112"
ACCOUNT = "11111111111111111111111111111111"
EVIDENCE = "a" * 64


def registry():
    return {
        "network": NETWORK,
        "mint": MINT,
        "entries": [{
            "owner_wallet": OWNER,
            "token_accounts": [ACCOUNT],
            "control_evidence_sha256": EVIDENCE,
            "evidence_type": "multisig_config_snapshot",
            "governance_reference": "THF treasury governance public record",
        }],
    }


class TestTreasuryControlRegistry(unittest.TestCase):
    def test_snapshot_is_deterministic_and_non_executable(self):
        first = normalize_registry(registry())
        second = normalize_registry(registry())
        self.assertEqual(first["registry_snapshot_sha256"], second["registry_snapshot_sha256"])
        self.assertFalse(first["execution_authorized"])
        self.assertFalse(first["transaction_signing_enabled"])
        self.assertFalse(first["transaction_broadcast_enabled"])
        self.assertFalse(first["contains_signer_secrets"])

    def test_registered_account_builds_verifier_candidate(self):
        snapshot = normalize_registry(registry())
        candidate = candidate_from_registry(snapshot, ACCOUNT, OWNER)
        self.assertEqual(candidate["token_account"], ACCOUNT)
        self.assertEqual(candidate["treasury_owner_allowlist"], [OWNER])
        self.assertEqual(candidate["control_evidence_sha256"], EVIDENCE)
        self.assertEqual(candidate["registry_snapshot_sha256"], snapshot["registry_snapshot_sha256"])

    def test_owner_only_is_not_enough(self):
        snapshot = normalize_registry(registry())
        with self.assertRaises(ValueError):
            candidate_from_registry(snapshot, "DifferentTokenAccount11111111111111111111111", OWNER)

    def test_snapshot_tamper_is_rejected(self):
        snapshot = normalize_registry(registry())
        snapshot["entries"][0]["governance_reference"] = "tampered"
        with self.assertRaises(ValueError):
            candidate_from_registry(snapshot, ACCOUNT, OWNER)

    def test_duplicate_owner_is_rejected(self):
        source = registry()
        source["entries"].append(copy.deepcopy(source["entries"][0]))
        with self.assertRaises(ValueError):
            normalize_registry(source)

    def test_duplicate_token_account_is_rejected(self):
        source = registry()
        source["entries"].append({
            "owner_wallet": "11111111111111111111111111111111",
            "token_accounts": [ACCOUNT],
            "control_evidence_sha256": "b" * 64,
            "evidence_type": "governance_record",
            "governance_reference": "other record",
        })
        with self.assertRaises(ValueError):
            normalize_registry(source)

    def test_secret_material_fields_are_rejected_recursively(self):
        source = registry()
        source["entries"][0]["metadata"] = {"private_key": "forbidden"}
        with self.assertRaises(ValueError):
            normalize_registry(source)

    def test_signature_material_fields_are_rejected(self):
        source = registry()
        source["entries"][0]["signature"] = "forbidden"
        with self.assertRaises(ValueError):
            normalize_registry(source)

    def test_wrong_mint_is_rejected(self):
        source = registry()
        source["mint"] = OWNER
        with self.assertRaises(ValueError):
            normalize_registry(source)

    def test_invalid_evidence_digest_is_rejected(self):
        source = registry()
        source["entries"][0]["control_evidence_sha256"] = "not-a-sha"
        with self.assertRaises(ValueError):
            normalize_registry(source)


if __name__ == "__main__":
    unittest.main()
