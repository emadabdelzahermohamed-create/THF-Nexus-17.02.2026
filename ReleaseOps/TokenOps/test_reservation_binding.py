#!/usr/bin/env python3
import copy, json
from reservation_binding import build, canonical_sha

MINT='HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv'
POLICY=json.load(open('ReleaseOps/TokenOps/policy.json'))

RECON={
  'version':1,'network':'solana-mainnet-beta','mint':MINT,
  'inputs':{
    'verified_treasury_balance_raw':'1000000',
    'reward_reservation_raw':'350000',
    'vesting_liability_raw':'100000',
    'burn_reservation_raw':'200000',
    'treasury_transfer_reservation_raw':'50000',
    'current_supply_raw':'1000000000000000000',
    'supply_floor_raw':'800000000000000000'
  },
  'reconciliation':{
    'total_reserved_raw':'700000','available_after_reservations_raw':'300000',
    'treasury_solvent':True,'burn_supply_floor_preserved':True,
    'third_party_balance_included':False,'active_user_revenue_share':0.35
  },
  'execution':{
    'transaction_created':False,'transaction_signed':False,'transaction_submitted':False,
    'financial_effect':False,'external_multisig_required':True
  }
}
RECON['reconciliation_sha256']=canonical_sha(RECON)
LEDGER={
  'version':1,'network':'solana-mainnet-beta','mint':MINT,'operation':'reward_epoch',
  'manifest_sha256':'a'*64,'required_approvals':2,'approved_by':['a','b'],'approval_count':2,
  'threshold_met':True,'external_multisig_required':True,'execution_authorized':False,
  'transaction_signed':False,'transaction_submitted':False
}
LEDGER['ledger_entry_sha256']=canonical_sha(LEDGER)
REQ={'mint':MINT,'reservations':[
  {'reservation_id':'reward:epoch-1','kind':'reward','amount_raw':'350000','source_ref':'reward-manifest:epoch-1'},
  {'reservation_id':'vesting:batch-1','kind':'vesting','amount_raw':'100000','source_ref':'vesting-plan:batch-1'},
  {'reservation_id':'burn:proposal-1','kind':'burn','amount_raw':'200000','source_ref':'burn-plan:proposal-1'},
  {'reservation_id':'transfer:ops-1','kind':'treasury_transfer','amount_raw':'50000','source_ref':'treasury-request:ops-1'}
]}

def fail(req,recon=RECON,ledger=LEDGER,text=''):
    try: build(req,recon,ledger,POLICY)
    except ValueError as exc:
        assert text in str(exc),(text,str(exc)); return
    raise AssertionError('expected failure')

out=build(REQ,RECON,LEDGER,POLICY)
assert out['reservation_count']==4
assert out['reservation_totals_raw']['reward']=='350000'
assert out['reservation_totals_raw']['vesting']=='100000'
assert out['reservation_totals_raw']['burn']=='200000'
assert out['reservation_totals_raw']['treasury_transfer']=='50000'
assert out['reconciliation_sha256']==RECON['reconciliation_sha256']
assert out['manifest_sha256']==LEDGER['manifest_sha256']
assert out['execution_authorized'] is False
assert out['transaction_signed'] is False
assert out['transaction_submitted'] is False
assert out['financial_effect'] is False

bad=copy.deepcopy(REQ); bad['reservations'].append(copy.deepcopy(bad['reservations'][0]))
fail(bad,text='duplicate reservation_id')
bad=copy.deepcopy(REQ); bad['reservations'].append({'reservation_id':'reward:epoch-1','kind':'reward','amount_raw':'1','source_ref':'other'})
fail(bad,text='reservation_id collision')
bad=copy.deepcopy(REQ); bad['reservations'][0]['amount_raw']='349999'
fail(bad,text='reservation total mismatch for reward')
bad_recon=copy.deepcopy(RECON); bad_recon['inputs']['reward_reservation_raw']='1'
fail(REQ,recon=bad_recon,text='reservation total mismatch for reward')
bad_recon=copy.deepcopy(RECON); bad_recon['reconciliation_sha256']='0'*64
fail(REQ,recon=bad_recon,text='reconciliation sha mismatch')
bad_ledger=copy.deepcopy(LEDGER); bad_ledger['execution_authorized']=True
fail(REQ,ledger=bad_ledger,text='ledger execution state unsafe')
bad=copy.deepcopy(REQ); bad['private_key']='forbidden'
fail(bad,text='forbidden secret/signature field')

print('THF_TOKENOPS_RESERVATION_BINDING_GATE=PASS')
print('DUPLICATE_RESERVATION_REJECTED=TRUE')
print('RESERVATION_COLLISION_REJECTED=TRUE')
print('RECONCILIATION_CRYPTO_BOUND=TRUE')
print('APPROVAL_LEDGER_CRYPTO_BOUND=TRUE')
print('TRANSACTION_SIGNED=FALSE')
print('TRANSACTION_SUBMITTED=FALSE')
print('FINANCIAL_EFFECT=FALSE')
