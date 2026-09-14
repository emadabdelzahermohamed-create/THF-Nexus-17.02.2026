import copy
import json
import pathlib
import unittest

from integration_contract_gate import validate_contracts, validate_message_envelope

ROOT = pathlib.Path(__file__).resolve().parent


def contracts():
    return json.loads((ROOT / "integration_contracts.json").read_text(encoding="utf-8"))


class IntegrationContractGateTests(unittest.TestCase):
    def test_authoritative_contract_passes(self):
        result = validate_contracts(contracts())
        self.assertEqual(result["status"], "PASS_NON_BROADCAST")
        self.assertEqual(result["service_count"], 3)
        self.assertEqual(result["route_count"], 7)
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["broadcast"])
        self.assertFalse(result["financial_effect"])

    def test_identity_drift_fails_closed(self):
        obj = contracts()
        obj["services"]["Vault"]["mint"] = "wrong"
        result = validate_contracts(obj)
        self.assertEqual(result["status"], "FAIL_CLOSED")
        self.assertIn("Vault:mint_mismatch", result["errors"])

    def test_signing_capability_fails_closed(self):
        obj = contracts()
        obj["services"]["Forge"]["may_sign"] = True
        self.assertEqual(validate_contracts(obj)["status"], "FAIL_CLOSED")

    def test_missing_replay_protection_fails_closed(self):
        obj = contracts()
        obj["envelope_requirements"]["replay_protection"] = None
        self.assertEqual(validate_contracts(obj)["status"], "FAIL_CLOSED")

    def test_route_must_match_declared_io(self):
        obj = contracts()
        obj["routes"].append({"from": "Vault", "to": "Core", "message_type": "reserve_snapshot"})
        result = validate_contracts(obj)
        self.assertEqual(result["status"], "FAIL_CLOSED")
        self.assertTrue(any("target_input_not_declared" in x for x in result["errors"]))

    def test_sensitive_material_rejected(self):
        obj = contracts()
        obj["private_key"] = "never"
        with self.assertRaises(ValueError):
            validate_contracts(obj)

    def test_fresh_allowed_envelope_is_review_only(self):
        obj = contracts()
        envelope = {
            "schema": "thf-tokenops-message/v1",
            "contract_version": "1.2.0",
            "message_type": "activity_evidence",
            "network": "solana-mainnet-beta",
            "mint": "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv",
            "token_program": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            "decimals": 8,
            "amount_unit": "THF_RAW",
            "evidence_sha256": "a" * 64,
            "source_observed_at_utc": "2026-09-14T15:40:00Z",
            "source_slot": 447000000,
            "idempotency_key": "core-epoch-20260914-0001",
            "expires_at_utc": "2026-09-14T15:50:00Z",
            "financial_effect": False,
            "signed": False,
            "broadcast": False,
        }
        result = validate_message_envelope(envelope, obj, "Core", "Forge", "2026-09-14T15:41:00Z")
        self.assertEqual(result["status"], "PASS_NON_BROADCAST")
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["signed"])
        self.assertFalse(result["broadcast"])

    def test_stale_envelope_fails_closed(self):
        obj = contracts()
        envelope = {
            "schema": "thf-tokenops-message/v1",
            "contract_version": "1.2.0",
            "message_type": "activity_evidence",
            "network": "solana-mainnet-beta",
            "mint": "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv",
            "token_program": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            "decimals": 8,
            "amount_unit": "THF_RAW",
            "evidence_sha256": "b" * 64,
            "source_observed_at_utc": "2026-09-14T14:00:00Z",
            "source_slot": 447000000,
            "idempotency_key": "core-epoch-20260914-0002",
            "expires_at_utc": "2026-09-14T16:00:00Z",
            "financial_effect": False,
            "signed": False,
            "broadcast": False,
        }
        result = validate_message_envelope(envelope, obj, "Core", "Forge", "2026-09-14T15:41:00Z")
        self.assertEqual(result["status"], "FAIL_CLOSED")
        self.assertIn("evidence_stale_or_future", result["errors"])

    def test_wrong_route_fails_closed(self):
        obj = contracts()
        envelope = {
            "message_type": "burn_preview",
            "network": "solana-mainnet-beta",
            "mint": "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv",
            "token_program": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            "decimals": 8,
            "amount_unit": "THF_RAW",
            "evidence_sha256": "c" * 64,
            "source_observed_at_utc": "2026-09-14T15:40:00Z",
            "source_slot": 447000000,
            "idempotency_key": "forge-route-check-0001",
            "expires_at_utc": "2026-09-14T15:50:00Z",
            "financial_effect": False,
            "signed": False,
            "broadcast": False,
        }
        result = validate_message_envelope(envelope, obj, "Forge", "Vault", "2026-09-14T15:41:00Z")
        self.assertEqual(result["status"], "FAIL_CLOSED")
        self.assertIn("route_not_allowed", result["errors"])


if __name__ == "__main__":
    unittest.main()
