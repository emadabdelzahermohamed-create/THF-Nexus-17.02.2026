#!/usr/bin/env python3
import importlib.util, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('compiler', ROOT/'spl_instruction_compiler.py')
compiler=importlib.util.module_from_spec(spec); spec.loader.exec_module(compiler)
MINT=compiler.MINT; PROGRAM=compiler.TOKEN_PROGRAM
SRC='11111111111111111111111111111111'
OWNER='Vote111111111111111111111111111111111111111'
DST='Stake11111111111111111111111111111111111111'
BIND='a'*64; EVID='b'*64

def source():
    return {'token_account':SRC,'mint':MINT,'owner_wallet':OWNER,'owner_program':PROGRAM,'decimals':8,'onchain_verified':True,'treasury_controlled':True,'control_evidence_sha256':EVID}

def destination():
    return {'token_account':DST,'mint':MINT,'owner_wallet':OWNER,'owner_program':PROGRAM,'decimals':8,'onchain_verified':True}

class CompilerTests(unittest.TestCase):
    def test_transfer_checked(self):
        out=compiler.build({'mint':MINT,'operation':'transfer_checked','amount_raw':'123','decimals':8,'control_plane_binding_sha256':BIND,'source':source(),'destination':destination(),'authority_pubkey':OWNER})
        self.assertEqual(out['opcode'],12)
        self.assertEqual(out['instruction_data_hex'], '0c7b0000000000000008')
        self.assertFalse(out['ready_for_simulation']); self.assertFalse(out['ready_for_signing']); self.assertFalse(out['broadcast_allowed'])
    def test_burn_checked(self):
        out=compiler.build({'mint':MINT,'operation':'burn_checked','amount_raw':'1','decimals':8,'control_plane_binding_sha256':BIND,'source':source(),'authority_pubkey':OWNER})
        self.assertEqual(out['opcode'],15)
        self.assertTrue(out['account_metas'][1]['is_writable'])
        self.assertFalse(out['financial_effect'])
    def test_unverified_source_rejected(self):
        s=source(); s['onchain_verified']=False
        with self.assertRaises(ValueError): compiler.build({'mint':MINT,'operation':'burn_checked','amount_raw':'1','decimals':8,'control_plane_binding_sha256':BIND,'source':s,'authority_pubkey':OWNER})
    def test_third_party_source_rejected(self):
        s=source(); s['treasury_controlled']=False
        with self.assertRaises(ValueError): compiler.build({'mint':MINT,'operation':'burn_checked','amount_raw':'1','decimals':8,'control_plane_binding_sha256':BIND,'source':s,'authority_pubkey':OWNER})
    def test_authority_mismatch_rejected(self):
        with self.assertRaises(ValueError): compiler.build({'mint':MINT,'operation':'burn_checked','amount_raw':'1','decimals':8,'control_plane_binding_sha256':BIND,'source':source(),'authority_pubkey':DST})
    def test_secret_field_rejected(self):
        with self.assertRaises(ValueError): compiler.build({'mint':MINT,'operation':'burn_checked','amount_raw':'1','decimals':8,'control_plane_binding_sha256':BIND,'source':source(),'authority_pubkey':OWNER,'private_key':'never'})

if __name__=='__main__':
    result=unittest.main(exit=False).result
    if not result.wasSuccessful():
        raise SystemExit(1)
    print('THF_TOKENOPS_SPL_COMPILER_TESTS=PASS')
    print('UNVERIFIED_TREASURY_REJECTED=TRUE')
    print('THIRD_PARTY_SOURCE_REJECTED=TRUE')
    print('TRANSACTION_SERIALIZED=FALSE')
    print('TRANSACTION_SIGNED=FALSE')
    print('TRANSACTION_SUBMITTED=FALSE')
    print('FINANCIAL_EFFECT=FALSE')
    print('WAVE_UNTOUCHED=TRUE')
