#!/usr/bin/env python3
import argparse, hashlib, json, pathlib

FORBIDDEN={'private_key','secret_key','seed','seed_phrase','signature','signed_transaction','raw_transaction'}
KINDS={'reward','vesting','burn','treasury_transfer'}
FIELD_BY_KIND={
    'reward':'reward_reservation_raw',
    'vesting':'vesting_liability_raw',
    'burn':'burn_reservation_raw',
    'treasury_transfer':'treasury_transfer_reservation_raw',
}

def scan(obj,path=''):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k.lower() in FORBIDDEN:
                raise ValueError(f'forbidden secret/signature field: {path}{k}')
            scan(v,path+k+'.')
    elif isinstance(obj,list):
        for i,v in enumerate(obj): scan(v,f'{path}{i}.')

def canonical_sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def build(req, reconciliation, ledger, policy):
    scan(req); scan(reconciliation); scan(ledger)
    if req.get('mint') != policy['mint'] or reconciliation.get('mint') != policy['mint'] or ledger.get('mint') != policy['mint']:
        raise ValueError('mint mismatch')
    reservations=req.get('reservations',[])
    if not reservations: raise ValueError('at least one reservation required')
    seen={}; totals={k:0 for k in KINDS}; normalized=[]
    for row in reservations:
        rid=str(row.get('reservation_id','')).strip()
        kind=str(row.get('kind','')).strip()
        source_ref=str(row.get('source_ref','')).strip()
        if not rid or not source_ref: raise ValueError('blank reservation_id/source_ref')
        if kind not in KINDS: raise ValueError('unsupported reservation kind')
        try: amount=int(row.get('amount_raw'))
        except Exception as exc: raise ValueError('invalid reservation amount') from exc
        if amount < 0: raise ValueError('negative reservation amount forbidden')
        fingerprint=canonical_sha({'reservation_id':rid,'kind':kind,'amount_raw':str(amount),'source_ref':source_ref})
        if rid in seen:
            if seen[rid] == fingerprint: raise ValueError('duplicate reservation_id')
            raise ValueError('reservation_id collision')
        seen[rid]=fingerprint
        totals[kind]+=amount
        normalized.append({'reservation_id':rid,'kind':kind,'amount_raw':str(amount),'source_ref':source_ref,'reservation_sha256':fingerprint})
    inputs=reconciliation.get('inputs',{})
    for kind,field in FIELD_BY_KIND.items():
        expected=int(inputs.get(field,'0'))
        if totals[kind] != expected:
            raise ValueError(f'reservation total mismatch for {kind}')
    recon_sha=reconciliation.get('reconciliation_sha256')
    if not recon_sha or recon_sha != canonical_sha({k:v for k,v in reconciliation.items() if k!='reconciliation_sha256'}):
        raise ValueError('reconciliation sha mismatch')
    manifest_sha=ledger.get('manifest_sha256')
    if not manifest_sha: raise ValueError('ledger missing manifest sha')
    if ledger.get('execution_authorized') is not False or ledger.get('transaction_signed') is not False or ledger.get('transaction_submitted') is not False:
        raise ValueError('ledger execution state unsafe')
    binding={
      'version':1,
      'network':policy['network'],
      'mint':policy['mint'],
      'reservation_count':len(normalized),
      'reservation_totals_raw':{k:str(totals[k]) for k in sorted(totals)},
      'reservations':sorted(normalized,key=lambda x:x['reservation_id']),
      'reconciliation_sha256':recon_sha,
      'approval_ledger_sha256':ledger.get('ledger_entry_sha256'),
      'manifest_sha256':manifest_sha,
      'threshold_met':bool(ledger.get('threshold_met')),
      'execution_authorized':False,
      'transaction_signed':False,
      'transaction_submitted':False,
      'financial_effect':False,
      'external_multisig_required':True,
    }
    if not binding['approval_ledger_sha256']:
        raise ValueError('ledger entry sha missing')
    binding['control_plane_binding_sha256']=canonical_sha(binding)
    return binding

def main():
    p=argparse.ArgumentParser(); p.add_argument('reservations'); p.add_argument('reconciliation'); p.add_argument('ledger'); p.add_argument('policy'); p.add_argument('output'); a=p.parse_args()
    out=build(json.load(open(a.reservations)),json.load(open(a.reconciliation)),json.load(open(a.ledger)),json.load(open(a.policy)))
    pathlib.Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
    print(out['control_plane_binding_sha256'])
if __name__=='__main__': main()
