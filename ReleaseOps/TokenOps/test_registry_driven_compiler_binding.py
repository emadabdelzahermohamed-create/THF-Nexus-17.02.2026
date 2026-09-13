import copy, unittest
from treasury_control_registry import normalize_registry, MINT, NETWORK
from registry_driven_mainnet_verifier import build_registry_driven_verification
from registry_driven_compiler_binding import build

OWNER='So11111111111111111111111111111111111111112'
ACCOUNT='11111111111111111111111111111111'

def source():
    reg=normalize_registry({'network':NETWORK,'mint':MINT,'entries':[{'owner_wallet':OWNER,'token_accounts':[ACCOUNT],'control_evidence_sha256':'a'*64,'evidence_type':'multisig_config_snapshot','governance_reference':'synthetic test only'}]})
    val={'owner':'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA','data':{'parsed':{'type':'account','info':{'mint':MINT,'owner':OWNER,'state':'initialized','tokenAmount':{'amount':'1000','decimals':8}}}}}
    return build_registry_driven_verification(reg,ACCOUNT,OWNER,val)

class T(unittest.TestCase):
    def test_burn_binding(self):
        out=build({'registry_driven_source':source(),'operation':'burn_checked','amount_raw':'1','control_plane_binding_sha256':'b'*64})
        self.assertTrue(out['registry_source_required']); self.assertFalse(out['ready_for_simulation']); self.assertFalse(out['broadcast_allowed'])
    def test_tamper_rejected(self):
        s=source(); s['owner_wallet']='tampered'
        with self.assertRaises(ValueError): build({'registry_driven_source':s,'operation':'burn_checked','amount_raw':'1','control_plane_binding_sha256':'b'*64})
    def test_caller_control_metadata_rejected(self):
        with self.assertRaises(ValueError): build({'registry_driven_source':source(),'operation':'burn_checked','amount_raw':'1','control_plane_binding_sha256':'b'*64,'private_key':'forbidden'})
    def test_registry_required(self):
        with self.assertRaises(ValueError): build({'operation':'burn_checked','amount_raw':'1','control_plane_binding_sha256':'b'*64})

if __name__=='__main__': unittest.main()
