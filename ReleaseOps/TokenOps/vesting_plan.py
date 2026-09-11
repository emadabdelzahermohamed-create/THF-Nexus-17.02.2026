#!/usr/bin/env python3
import argparse, hashlib, json
from decimal import Decimal, ROUND_DOWN

DECIMALS=8
SCALE=10**DECIMALS

def to_raw(v):
    return int((Decimal(str(v))*SCALE).quantize(Decimal('1'), rounding=ROUND_DOWN))

def build(spec):
    now=int(spec['as_of_unix'])
    rows=[]
    total=0
    for g in spec.get('grants',[]):
        start=int(g['start_unix']); cliff=int(g.get('cliff_unix',start)); end=int(g['end_unix'])
        if not (start <= cliff <= end): raise ValueError('invalid vesting timeline')
        amount=to_raw(g['amount_ui'])
        if amount <= 0: raise ValueError('amount must be positive')
        if now < cliff: vested=0
        elif now >= end: vested=amount
        else:
            elapsed=max(0, now-start); duration=end-start
            vested=(amount*elapsed)//duration if duration else amount
        released=to_raw(g.get('released_ui','0'))
        if released > vested: raise ValueError('released exceeds vested')
        claimable=vested-released
        total += claimable
        rows.append({'beneficiary':g['beneficiary'],'amount_raw':amount,'vested_raw':vested,'released_raw':released,'claimable_raw':claimable})
    out={'version':1,'mint':spec['mint'],'as_of_unix':now,'grants':rows,'total_claimable_raw':total,'execution':'forbidden_unsigned_plan_only'}
    canonical=json.dumps(out,sort_keys=True,separators=(',',':')).encode()
    out['manifest_sha256']=hashlib.sha256(canonical).hexdigest()
    return out

def main():
    p=argparse.ArgumentParser(); p.add_argument('input'); p.add_argument('output'); a=p.parse_args()
    spec=json.load(open(a.input)); out=build(spec)
    json.dump(out,open(a.output,'w'),indent=2); print(out['manifest_sha256'])
if __name__=='__main__': main()
