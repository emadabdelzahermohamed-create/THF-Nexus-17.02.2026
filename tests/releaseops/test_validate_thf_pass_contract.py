import copy
import json
import pathlib
import unittest

from tools.releaseops.validate_thf_pass_contract import validate

ROOT = pathlib.Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "ReleaseOps/apps_factory/contracts/thf_pass_federation_handoff_v1.json"


class PassContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_authoritative_candidate_contract_passes(self):
        self.assertEqual(validate(copy.deepcopy(self.base)), [])

    def test_rejects_final_claim(self):
        data = copy.deepcopy(self.base)
        data["final_or_play_ready"] = True
        self.assertTrue(validate(data))

    def test_rejects_missing_replay_protection(self):
        data = copy.deepcopy(self.base)
        data["required_federation_semantics"]["handoff_replay_rejected"] = False
        self.assertTrue(validate(data))

    def test_rejects_query_token_handoff(self):
        data = copy.deepcopy(self.base)
        data["required_federation_semantics"]["handoff_query_token_forbidden"] = False
        self.assertTrue(validate(data))

    def test_rejects_candidate_equal_to_baseline(self):
        data = copy.deepcopy(self.base)
        data["candidate"] = copy.deepcopy(data["baseline"])
        self.assertTrue(validate(data))

    def test_rejects_owner_gate_claim(self):
        data = copy.deepcopy(self.base)
        data["owner_or_device_gates"]["physical_phone_acceptance"] = True
        self.assertTrue(validate(data))


if __name__ == "__main__":
    unittest.main()
