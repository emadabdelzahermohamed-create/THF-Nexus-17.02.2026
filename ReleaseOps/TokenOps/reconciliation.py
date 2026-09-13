#!/usr/bin/env python3
import argparse, hashlib, json, pathlib

FORBIDDEN_FIELDS={
    'private_key','secret_key','seed','seed_phrase','signature','signed_transaction','raw_transaction'
}

def canonical_sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def scan(obj,path=''):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k.lower() in FORBIDDEN_FIELDS:
                raise ValueError(f'forbidden secret/signature field: {path}{k}')
            scan(v,path+k+'.')
    elif isinstance(obj,list):
        for i,v in enumerate(obj): scan(v,f'{path}{i}.')

def as_int(value,name):
    try: return int(value)
    except Exception as exc: raise ValueError(f'invalid integer for {name}') from exc

def build(req, policy):
    scan(req)
    if req.get('mint') != policy['mint']:
        raise ValueError('mint mismatch')

    treasury=as_int(req.get('verified_treasury_balance_raw','0'),'verified_treasury_balance_raw')
    reward=as_int(req.get('reward_reservation_raw','0'),'reward_reservation_raw')
    vesting=as_int(req.get('vesting_liability_raw','0'),'vesting_liability_raw')
    burn=as_int(req.get('burn_reservation_raw','0'),'burn_reservation_raw')
    transfer=as_int(req.get('treasury_transfer_reservation_raw','0'),'treasury_transfer_reservation_raw')
    supply=as_int(req.get('current_supply_raw','0'),'current_supply_raw')
    floor=as_int(req.get('supply_floor_raw','0'),'supply_floor_raw')

    values={'treasury':treasury,'reward':reward,'vesting':vesting,'burn':burn,'transfer':transfer,'supply':supply,'floor':floor}
    if any(v < 0 for v in values.values()):
        raise ValueError('negative accounting value forbidden')
    if burn > 0 and supply - burn < floor:
        raise ValueError('burn reservation violates supply floor')

    reserved = reward + vesting + burn + transfer
    available = treasury - reserved
    solvent = available >= 0
    if not solvent:
        raise ValueError('treasury overcommitted')

    economics=policy['economics']
    out={
      'version':1,
      'network':policy['network'],
      'mint':policy['mint'],
      'inputs':{
        'verified_treasury_balance_raw':str(treasury),
        'reward_reservation_raw':str(reward),
        'vesting_liability_raw':str(vesting),
        'burn_reservation_raw':str(burn),
        'treasury_transfer_reservation_raw':str(transfer),
        'current_supply_raw':str(supply),
        'supply_floor_raw':str(floor),
      },
      'reconciliation':{
        'total_reserved_raw':str(reserved),
        'available_after_reservations_raw':str(available),
        'treasury_solvent':True,
        'burn_supply_floor_preserved': supply-burn >= floor,
        'third_party_balance_included':False,
        'active_user_revenue_share':economics['active_user_revenue_share'],
      },
      'execution':{
        'transaction_created':False,
        'transaction_signed':False,
        'transaction_submitted':False,
        'financial_effect':False,
        'external_multisig_required':True,
      }
    }
    out['reconciliation_sha256']=canonical_sha(out)
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument('request'); p.add_argument('policy'); p.add_argument('output')
    a=p.parse_args()
    req=json.load(open(a.request)); policy=json.load(open(a.policy))
    out=build(req,policy)
    pathlib.Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
    print(out['reconciliation_sha256'])

if __name__=='__main__': main()
