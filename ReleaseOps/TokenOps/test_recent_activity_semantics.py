#!/usr/bin/env python3
import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("recent_activity_semantics", HERE / "recent_activity_semantics.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class RecentActivitySemanticsTests(unittest.TestCase):
    def test_classifies_only_explicit_canonical_mint_instructions(self):
        tx = {"result": {"slot": 10, "blockTime": 20, "transaction": {"message": {"instructions": [
            {"parsed": {"type": "mintTo", "info": {"mint": M.MINT}}},
            {"parsed": {"type": "transferChecked", "info": {"mint": M.MINT}}},
            {"parsed": {"type": "transfer", "info": {"source": "x", "destination": "y"}}},
        ]}}, "meta": {"err": None, "innerInstructions": [{"instructions": [
            {"parsed": {"type": "setAuthority", "info": {"account": M.MINT}}},
            {"parsed": {"type": "burn", "info": {"mint": M.MINT}}},
        ]}]}}}
        canonical, unscoped = M.instruction_types(tx)
        self.assertCountEqual(canonical, ["mintTo", "transferChecked", "setAuthority", "burn"])
        self.assertEqual(unscoped, ["transfer"])

    def test_summary_separates_unscoped_token_instructions(self):
        tx = {"result": {"slot": 1, "blockTime": 2, "transaction": {"message": {"instructions": [
            {"parsed": {"type": "mintToChecked", "info": {"mint": M.MINT}}},
            {"parsed": {"type": "transfer", "info": {"source": "x", "destination": "y"}}},
        ]}}, "meta": {"err": None, "innerInstructions": []}}}
        summary = M.summarize_transactions([tx])
        self.assertEqual(summary["mint_instruction_count"], 1)
        self.assertEqual(summary["transfer_instruction_count"], 0)
        self.assertEqual(summary["unscoped_instruction_count"], 1)
        self.assertEqual(summary["unscoped_token_instruction_type_counts"]["transfer"], 1)
        self.assertFalse(summary["signatures_persisted"])
        self.assertTrue(all("signature" not in record for record in summary["records"]))

    def test_wrong_mint_is_not_counted_as_canonical(self):
        parsed = {"type": "burn", "info": {"mint": "DifferentMint1111111111111111111111111111111"}}
        self.assertEqual(M.instruction_scope(parsed), "unscoped")

    def test_set_authority_must_target_canonical_mint(self):
        self.assertEqual(M.instruction_scope({"type": "setAuthority", "info": {"account": M.MINT}}), "canonical")
        self.assertEqual(M.instruction_scope({"type": "setAuthority", "info": {"account": "other"}}), "unscoped")

    def test_unknown_non_token_instruction_is_ignored(self):
        tx = {"result": {"transaction": {"message": {"instructions": [
            {"parsed": {"type": "someOtherInstruction"}},
        ]}}, "meta": {"err": None}}}
        canonical, unscoped = M.instruction_types(tx)
        self.assertEqual(canonical, [])
        self.assertEqual(unscoped, [])

    def test_failed_transaction_is_marked_without_sensitive_material(self):
        tx = {"result": {"slot": 4, "blockTime": 5, "transaction": {"message": {"instructions": []}}, "meta": {"err": {"InstructionError": [0, "Custom"]}}}}
        summary = M.summarize_transactions([tx])
        self.assertTrue(summary["records"][0]["transaction_failed"])
        self.assertFalse(summary["signatures_persisted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
