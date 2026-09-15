import unittest
from treasury_epoch_ledger import *

class EpochLedgerTests(unittest.TestCase):
    def inp(self): return EpochInput("2026-09","a"*40,100000,"b"*64,"c"*64)
    def test_reconciled_35_percent_epoch(self):
        e=build_epoch(self.inp(),pool_atomic=35000,allocated_atomic=30000,unallocated_atomic=5000)
        self.assertTrue(e["reconciled"]); self.assertFalse(e["financial_execution"]); self.assertFalse(e["broadcast"])
    def test_rejects_wrong_share(self):
        with self.assertRaises(ValueError): build_epoch(self.inp(),pool_atomic=34999,allocated_atomic=30000,unallocated_atomic=4999)
    def test_unsigned_manifest_blocks_missing_treasury(self):
        e=build_epoch(self.inp(),pool_atomic=35000,allocated_atomic=30000,unallocated_atomic=5000)
        m=unsigned_settlement_manifest(e,[{"wallet":"w","amount_atomic":30000}],treasury_pubkey=None)
        self.assertEqual(m["status"],"BLOCKED_TREASURY_PUBKEY"); self.assertFalse(m["sign"]); self.assertFalse(m["broadcast"])
    def test_manifest_deterministic(self):
        e=build_epoch(self.inp(),pool_atomic=35000,allocated_atomic=30000,unallocated_atomic=5000)
        a=[{"wallet":"b","amount_atomic":10000},{"wallet":"a","amount_atomic":20000}]
        self.assertEqual(unsigned_settlement_manifest(e,a,treasury_pubkey="T")["manifest_sha256"],unsigned_settlement_manifest(e,list(reversed(a)),treasury_pubkey="T")["manifest_sha256"])
    def test_accounting_reconciliation(self):
        self.assertTrue(accounting_delta(100,50,25,125)["reconciled"])
        self.assertFalse(accounting_delta(100,50,25,124)["reconciled"])

if __name__ == "__main__": unittest.main()
