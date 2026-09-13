#!/usr/bin/env python3
import argparse, hashlib, json

ALLOWED={'reward_epoch','vesting_settlement','burn','treasury_transfer'}
FORBIDDEN_FIELDS={'private_key','secret_key','seed','seed_phrase','signature','signed_transaction','raw_transaction'}

def scan(obj,path=''):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k.lower() in FORBIDDEN_FIELDS: raise ValueError(f'forbidden secret/signature field: {path}{k}')
            scan(v,path+k+'.')
    elif isinstance(obj,list):
        for i,v in enumerate(obj): scan(v,f'{path}{i}.')

def build(req,policy):
    scan(req)
    kind=req['operation']
    if kind not in ALLOWED: raise ValueError('unsupported operation')
    cls=policy['approval_classes'][kind]
    if req.get('mint') != policy['mint']: raise ValueError('mint mismatch')
    approvals=req.get('approvals',[])
    identities=[a['approver_id'] for a in approvals if a.get('approved') is True]
    if len(identities) != len(set(identities)): raise ValueError('duplicate approver')
    ready=len(identities) >= int(cls['minimum_approvals'])
    if kind=='burn':
        supply=int(req['current_supply_raw']); amount=int(req['amount_raw']); floor=int(req['supply_floor_raw'])
        if amount<=0 or supply-amount < floor: raise ValueError('burn violates supply floor')
        if req.get('source_control')!='treasury_verified': raise ValueError('burn source is not verified treasury')
    out={
      'version':1,'network':policy['network'],'mint':policy['mint'],'operation':kind,
      'payload':req.get('payload',{}),'approvals':approvals,'approval_count':len(identities),
      'required_approvals':int(cls['minimum_approvals']),'approval_gate_pass':ready,
      'execution_backend':cls['execution'],'transaction_created':False,'transaction_signed':False,
      'transaction_submitted':False,'broadcast_allowed':False,'external_signer_required':True
    }
    canonical=json.dumps(out,sort_keys=True,separators=(',',':')).encode()
    out['manifest_sha256']=hashlib.sha256(canonical).hexdigest()
    return out

def main():
    p=argparse.ArgumentParser(); p.add_argument('request'); p.add_argument('policy'); p.add_argument('output'); a=p.parse_args()
    out=build(json.load(open(a.request)),json.load(open(a.policy)))
    json.dump(out,open(a.output,'w'),indent=2); print(out['manifest_sha256'])
if __name__=='__main__': main()
