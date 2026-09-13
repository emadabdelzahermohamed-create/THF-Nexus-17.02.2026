#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, sys

FORBIDDEN={'private_key','secret_key','seed','seed_phrase','signature','signed_transaction','raw_transaction'}

def scan(obj,path=''):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k.lower() in FORBIDDEN:
                raise ValueError(f'forbidden field: {path}{k}')
            scan(v,path+k+'.')
    elif isinstance(obj,list):
        for i,v in enumerate(obj): scan(v,f'{path}{i}.')

def canonical_sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def build(manifest, policy):
    scan(manifest)
    op=manifest['operation']
    if manifest.get('mint') != policy['mint']: raise ValueError('mint mismatch')
    cls=policy['approval_classes'][op]
    approvals=manifest.get('approvals',[])
    approved=[]
    seen=set()
    for row in approvals:
        ident=str(row.get('approver_id','')).strip()
        if not ident: raise ValueError('blank approver_id')
        if ident in seen: raise ValueError('duplicate approver')
        seen.add(ident)
        if row.get('approved') is True: approved.append(ident)
    required=int(cls['minimum_approvals'])
    record={
      'version':1,
      'network':policy['network'],
      'mint':policy['mint'],
      'operation':op,
      'manifest_sha256':manifest.get('manifest_sha256'),
      'required_approvals':required,
      'approved_by':sorted(approved),
      'approval_count':len(approved),
      'threshold_met':len(approved)>=required,
      'external_multisig_required':True,
      'execution_authorized':False,
      'transaction_signed':False,
      'transaction_submitted':False
    }
    record['ledger_entry_sha256']=canonical_sha(record)
    return record

def main():
    p=argparse.ArgumentParser(); p.add_argument('manifest'); p.add_argument('policy'); p.add_argument('output'); a=p.parse_args()
    out=build(json.load(open(a.manifest)),json.load(open(a.policy)))
    pathlib.Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
    print(out['ledger_entry_sha256'])
if __name__=='__main__': main()
