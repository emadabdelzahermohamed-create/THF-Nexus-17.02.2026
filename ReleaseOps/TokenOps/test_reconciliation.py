#!/usr/bin/env python3
import copy, json
from reconciliation import build

MINT='HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv'
POLICY=json.load(open('ReleaseOps/TokenOps/policy.json'))
BASE={
  'mint':MINT,
  'verified_treasury_balance_raw':'1000000',
  'reward_reservation_raw':'350000',
  'vesting_liability_raw':'100000',
  'burn_reservation_raw':'200000',
  'treasury_transfer_reservation_raw':'50000',
  'current_supply_raw':'1000000000000000000',
  'supply_floor_raw':'800000000000000000',
}

def expect_fail(req, text):
    try: build(req,POLICY)
    except ValueError as exc:
        assert text in str(exc), (text,str(exc)); return
    raise AssertionError('expected failure')

out=build(BASE,POLICY)
assert out['reconciliation']['total_reserved_raw']=='700000'
assert out['reconciliation']['available_after_reservations_raw']=='300000'
assert out['reconciliation']['treasury_solvent'] is True
assert out['reconciliation']['burn_supply_floor_preserved'] is True
assert out['reconciliation']['third_party_balance_included'] is False
assert out['reconciliation']['active_user_revenue_share']==0.35
assert out['execution']['transaction_created'] is False
assert out['execution']['transaction_signed'] is False
assert out['execution']['transaction_submitted'] is False
assert out['execution']['financial_effect'] is False
assert out['execution']['external_multisig_required'] is True

bad=copy.deepcopy(BASE); bad['reward_reservation_raw']='800000'
expect_fail(bad,'treasury overcommitted')
bad=copy.deepcopy(BASE); bad['burn_reservation_raw']='200000000000000001'
expect_fail(bad,'burn reservation violates supply floor')
bad=copy.deepcopy(BASE); bad['private_key']='forbidden'
expect_fail(bad,'forbidden secret/signature field')
bad=copy.deepcopy(BASE); bad['mint']='WrongMint'
expect_fail(bad,'mint mismatch')
bad=copy.deepcopy(BASE); bad['vesting_liability_raw']='-1'
expect_fail(bad,'negative accounting value forbidden')

print('THF_TOKENOPS_RECONCILIATION_GATE=PASS')
print('TREASURY_SOLVENT=TRUE')
print('BURN_FLOOR_PRESERVED=TRUE')
print('THIRD_PARTY_BALANCE_INCLUDED=FALSE')
print('TRANSACTION_CREATED=FALSE')
print('TRANSACTION_SIGNED=FALSE')
print('TRANSACTION_SUBMITTED=FALSE')
print('FINANCIAL_EFFECT=FALSE')
