#!/usr/bin/env python3
import argparse, hashlib, json, pathlib

def sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def build(cfg, token_accounts):
    if cfg['mint'] != token_accounts['mint']: raise ValueError('mint mismatch')
    allowed=set(cfg.get('verified_treasury_owners',[]))
    rows=[]; total=0
    for a in token_accounts.get('accounts',[]):
        owner=a.get('owner_wallet'); amount=int(a.get('amount_raw','0'))
        controlled=owner in allowed
        rows.append({'token_account':a.get('token_account'),'owner_wallet':owner,'amount_raw':str(amount),'treasury_control_verified':controlled})
        if controlled: total += amount
    out={
      'version':1,'network':'solana-mainnet-beta','mint':cfg['mint'],
      'verified_treasury_owners':sorted(allowed),'accounts':rows,
      'verified_treasury_balance_raw':str(total),
      'third_party_balance_included':False,
      'read_only':True,'transaction_created':False,'transaction_signed':False,'transaction_submitted':False
    }
    out['inventory_sha256']=sha(out)
    return out

def main():
    p=argparse.ArgumentParser(); p.add_argument('config'); p.add_argument('accounts'); p.add_argument('output'); a=p.parse_args()
    out=build(json.load(open(a.config)),json.load(open(a.accounts)))
    pathlib.Path(a.output).write_text(json.dumps(out,indent=2)+'\n'); print(out['inventory_sha256'])
if __name__=='__main__': main()
