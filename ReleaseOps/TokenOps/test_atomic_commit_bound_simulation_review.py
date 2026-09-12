#!/usr/bin/env python3
import pathlib
import unittest

import atomic_commit_bound_simulation_review as mod
import anchored_approval_ledger_commit
import test_anchored_approval_binding as fx


class T(unittest.TestCase):
    def fixture(self):
        p, req, rec, fg, guard = fx.T().fixture()
        manifest = fx.manifest()
        receipt = anchored_approval_ledger_commit.commit_review(
            manifest, fx.policy(), fg, guard, req, rec, p, fx.HEAD, created_at=2
        )
        return p, manifest, receipt

    def test_exact_committed_head_binds_review(self):
        p, manifest, receipt = self.fixture()
        out = mod.build(manifest, receipt, p, fx.HEAD)
        self.assertTrue(mod.verify(out)['verified'])
        self.assertTrue(out['durable_approval_commit_verified'])
        self.assertTrue(out['exact_final_ledger_head_verified'])
        self.assertTrue(out['simulation_review_eligible'])
        self.assertFalse(out['simulation_execution_permitted'])
        self.assertFalse(out['execution_authorized'])
        self.assertFalse(out['transaction_created'])
        self.assertFalse(out['transaction_signed'])
        self.assertFalse(out['transaction_submitted'])
        self.assertFalse(out['broadcast_allowed'])
        self.assertFalse(out['financial_effect'])
        self.assertFalse(out['private_key_used'])
        self.assertFalse(out['wave_mawja_touched'])

    def test_receipt_tamper_fails_closed(self):
        p, manifest, receipt = self.fixture()
        receipt['final_ledger_head_sha256'] = 'a' * 64
        with self.assertRaises(ValueError):
            mod.build(manifest, receipt, p, fx.HEAD)

    def test_manifest_mismatch_fails_closed(self):
        p, manifest, receipt = self.fixture()
        manifest['manifest_sha256'] = 'b' * 64
        with self.assertRaises(ValueError):
            mod.build(manifest, receipt, p, fx.HEAD)

    def test_source_head_mismatch_fails_closed(self):
        p, manifest, receipt = self.fixture()
        with self.assertRaises(ValueError):
            mod.build(manifest, receipt, p, 'd' * 40)

    def test_live_ledger_advance_invalidates_old_receipt(self):
        p, manifest, receipt = self.fixture()
        with open(p, 'a', encoding='utf-8') as f:
            f.write('{"tamper":true}\n')
        with self.assertRaises(ValueError):
            mod.build(manifest, receipt, p, fx.HEAD)

    def test_secret_field_rejected(self):
        p, manifest, receipt = self.fixture()
        manifest['private_key'] = 'never'
        with self.assertRaises(ValueError):
            mod.build(manifest, receipt, p, fx.HEAD)


if __name__ == '__main__':
    unittest.main()
