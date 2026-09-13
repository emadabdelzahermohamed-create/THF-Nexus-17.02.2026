#!/usr/bin/env python3
import importlib.util, json, pathlib, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parent

def load(name):
    spec=importlib.util.spec_from_file_location(name, ROOT/f'{name}.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
approval=load('approval_ledger'); inventory=load('treasury_inventory')
POLICY=json.loads((ROOT/'treasury_policy.json').read_text())

class ControlPlaneTests(unittest.TestCase):
    def test_approval_threshold_not_execution(self):
        manifest={'mint':POLICY['mint'],'operation':'reward_epoch','manifest_sha256':'abc','approvals':[{'approver_id':'a','approved':True},{'approver_id':'b','approved':True}]}
        out=approval.build(manifest,POLICY)
        self.assertTrue(out['threshold_met']); self.assertFalse(out['execution_authorized']); self.assertFalse(out['transaction_submitted'])
    def test_duplicate_approver_rejected(self):
        manifest={'mint':POLICY['mint'],'operation':'burn','approvals':[{'approver_id':'a','approved':True},{'approver_id':'a','approved':True}]}
        with self.assertRaises(ValueError): approval.build(manifest,POLICY)
    def test_secret_field_rejected(self):
        manifest={'mint':POLICY['mint'],'operation':'reward_epoch','approvals':[],'seed_phrase':'never'}
        with self.assertRaises(ValueError): approval.build(manifest,POLICY)
    def test_inventory_excludes_third_party(self):
        cfg={'mint':POLICY['mint'],'verified_treasury_owners':['treasury-owner']}
        src={'mint':POLICY['mint'],'accounts':[{'token_account':'ta1','owner_wallet':'treasury-owner','amount_raw':'100'},{'token_account':'ta2','owner_wallet':'someone-else','amount_raw':'900'}]}
        out=inventory.build(cfg,src)
        self.assertEqual(out['verified_treasury_balance_raw'],'100'); self.assertFalse(out['third_party_balance_included']); self.assertFalse(out['transaction_created'])

if __name__=='__main__': unittest.main()
