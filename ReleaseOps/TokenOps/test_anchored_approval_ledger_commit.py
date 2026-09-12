#!/usr/bin/env python3
import pathlib
import unittest

import audit_export
import anchored_approval_ledger_commit as mod
import test_anchored_approval_binding as fx


class T(unittest.TestCase):
    def fixture(self):
        return fx.T().fixture()

    def test_atomic_commit_chains_consumption_then_approval(self):
        p, req, rec, fg, guard = self.fixture()
        before = audit_export.verify(p)
        out = mod.commit_review(
            fx.manifest(), fx.policy(), fg, guard, req, rec, p, fx.HEAD, created_at=2
        )
        after = audit_export.verify(p)
        self.assertEqual(after['entries'], before['entries'] + 2)
        self.assertEqual(after['head_hash'], out['approval_ledger_entry_sha256'])
        self.assertEqual(out['final_ledger_head_sha256'], out['approval_ledger_entry_sha256'])
        self.assertTrue(out['atomic_local_commit'])
        self.assertTrue(out['anchored_replay_consumed'])
        self.assertTrue(out['approval_evidence_appended'])
        self.assertFalse(out['simulation_execution_permitted'])
        self.assertFalse(out['execution_authorized'])
        self.assertFalse(out['transaction_created'])
        self.assertFalse(out['transaction_signed'])
        self.assertFalse(out['transaction_submitted'])
        self.assertFalse(out['broadcast_allowed'])
        self.assertFalse(out['financial_effect'])
        self.assertFalse(out['private_key_used'])
        self.assertFalse(out['wave_mawja_touched'])

    def test_replay_attempt_leaves_committed_ledger_unchanged(self):
        p, req, rec, fg, guard = self.fixture()
        mod.commit_review(fx.manifest(), fx.policy(), fg, guard, req, rec, p, fx.HEAD, created_at=2)
        before = pathlib.Path(p).read_bytes()
        with self.assertRaises(ValueError):
            mod.commit_review(fx.manifest(), fx.policy(), fg, guard, req, rec, p, fx.HEAD, created_at=3)
        self.assertEqual(pathlib.Path(p).read_bytes(), before)

    def test_source_head_mismatch_leaves_ledger_unchanged(self):
        p, req, rec, fg, guard = self.fixture()
        before = pathlib.Path(p).read_bytes()
        with self.assertRaises(ValueError):
            mod.commit_review(fx.manifest(), fx.policy(), fg, guard, req, rec, p, 'd' * 40, created_at=2)
        self.assertEqual(pathlib.Path(p).read_bytes(), before)

    def test_manifest_tamper_leaves_ledger_unchanged(self):
        p, req, rec, fg, guard = self.fixture()
        m = fx.manifest()
        m['manifest_sha256'] = 'e' * 64
        before = pathlib.Path(p).read_bytes()
        with self.assertRaises(ValueError):
            mod.commit_review(m, fx.policy(), fg, guard, req, rec, p, fx.HEAD, created_at=2)
        self.assertEqual(pathlib.Path(p).read_bytes(), before)

    def test_secret_field_rejected_without_mutation(self):
        p, req, rec, fg, guard = self.fixture()
        m = fx.manifest()
        m['private_key'] = 'never'
        before = pathlib.Path(p).read_bytes()
        with self.assertRaises(ValueError):
            mod.commit_review(m, fx.policy(), fg, guard, req, rec, p, fx.HEAD, created_at=2)
        self.assertEqual(pathlib.Path(p).read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
