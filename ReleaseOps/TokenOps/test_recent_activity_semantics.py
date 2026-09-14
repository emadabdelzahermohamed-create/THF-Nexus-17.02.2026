#!/usr/bin/env python3
import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("recent_activity_semantics", HERE / "recent_activity_semantics.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class RecentActivitySemanticsTests(unittest.TestCase):
    def test_classifies_outer_and_inner_token_instructions(self):
        tx = {"result": {"slot": 10, "blockTime": 20, "transaction": {"message": {"instructions": [
            {"parsed": {"type": "mintTo", "info": {}}},
            {"parsed": {"type": "transferChecked", "info": {}}},
        ]}}, "meta": {"err": None, "innerInstructions": [{"instructions": [
            {"parsed": {"type": "setAuthority", "info": {}}},
            {"parsed": {"type": "burn", "info": {}}},
        ]}]}}}
        kinds = M.parsed_instruction_types(tx)
        self.assertCountEqual(kinds, ["mintTo", "transferChecked", "setAuthority", "burn"])

    def test_summary_has_exact_category_counts_and_no_signatures(self):
        tx = {"result": {"slot": 1, "blockTime": 2, "transaction": {"message": {"instructions": [
            {"parsed": {"type": "mintToChecked"}},
            {"parsed": {"type": "transfer"}},
        ]}}, "meta": {"err": None, "innerInstructions": []}}}
        summary = M.summarize_transactions([tx])
        self.assertEqual(summary["mint_instruction_count"], 1)
        self.assertEqual(summary["burn_instruction_count"], 0)
        self.assertEqual(summary["transfer_instruction_count"], 1)
        self.assertFalse(summary["signatures_persisted"])
        self.assertNotIn("signature", str(summary).lower())

    def test_unknown_non_token_instruction_is_ignored(self):
        tx = {"result": {"transaction": {"message": {"instructions": [
            {"parsed": {"type": "someOtherInstruction"}},
        ]}}, "meta": {"err": None}}}
        self.assertEqual(M.parsed_instruction_types(tx), [])

    def test_failed_transaction_is_marked_without_sensitive_material(self):
        tx = {"result": {"slot": 4, "blockTime": 5, "transaction": {"message": {"instructions": []}}, "meta": {"err": {"InstructionError": [0, "Custom"]}}}}
        summary = M.summarize_transactions([tx])
        self.assertTrue(summary["records"][0]["transaction_failed"])
        self.assertFalse(summary["signatures_persisted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
