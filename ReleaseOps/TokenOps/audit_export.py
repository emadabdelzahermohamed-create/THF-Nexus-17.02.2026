#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, time

FORBIDDEN={'private_key','secret_key','seed','seed_phrase','signature','signed_transaction','raw_transaction'}

def scan(obj,path=''):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k.lower() in FORBIDDEN:
                raise ValueError(f'forbidden field: {path}{k}')
            scan(v,path+k+'.')
    elif isinstance(obj,list):
        for i,v in enumerate(obj): scan(v,f'{path}{i}.')

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def append_entry(event, ledger_path, created_at=None):
    scan(event)
    p=pathlib.Path(ledger_path)
    entries=[]
    if p.exists() and p.read_text().strip():
        entries=[json.loads(x) for x in p.read_text().splitlines() if x.strip()]
    previous_hash=entries[-1]['entry_hash'] if entries else 'GENESIS'
    body={
      'version':1,
      'sequence':len(entries)+1,
      'created_at_unix':int(created_at if created_at is not None else time.time()),
      'previous_hash':previous_hash,
      'event':event,
      'execution':{'transaction_created':False,'transaction_signed':False,'transaction_submitted':False}
    }
    body['entry_hash']=digest(body)
    with p.open('a') as f:
        f.write(json.dumps(body,sort_keys=True,separators=(',',':'))+'\n')
    return body

def verify(path):
    prev='GENESIS'; count=0
    for line in pathlib.Path(path).read_text().splitlines():
        if not line.strip(): continue
        entry=json.loads(line); expected=entry['entry_hash']; check=dict(entry); check.pop('entry_hash')
        if entry['previous_hash'] != prev or digest(check) != expected:
            raise ValueError(f'audit chain invalid at sequence {entry.get("sequence")}')
        if entry['execution'] != {'transaction_created':False,'transaction_signed':False,'transaction_submitted':False}:
            raise ValueError('execution safety invariant violated')
        scan(entry['event']); prev=expected; count+=1
    return {'entries':count,'head_hash':prev,'verified':True}

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('append'); a.add_argument('event'); a.add_argument('ledger')
    v=sub.add_parser('verify'); v.add_argument('ledger')
    x=p.parse_args()
    if x.cmd=='append': print(json.dumps(append_entry(json.load(open(x.event)),x.ledger),indent=2))
    else: print(json.dumps(verify(x.ledger),indent=2))
if __name__=='__main__': main()
